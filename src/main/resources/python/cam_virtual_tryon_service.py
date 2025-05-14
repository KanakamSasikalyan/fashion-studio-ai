import cv2
import numpy as np
import argparse
import base64
import sys
import time
import json
import websockets
import logging
import asyncio

# Set up argument parsing
parser = argparse.ArgumentParser(description='Virtual Try-On Application')
parser.add_argument('--cloth-image', type=str, required=True,
                   help='Path to the cloth image for virtual try-on')
parser.add_argument('--port', type=int, required=True,
                   help='Port for the WebSocket server')
args = parser.parse_args()

# Initialize webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print(json.dumps({"type": "error", "message": "Could not open webcam"}))
    sys.exit(1)

# Load cloth image
cloth_img = cv2.imread(args.cloth_image, cv2.IMREAD_UNCHANGED)
if cloth_img is None:
    print(json.dumps({"type": "error", "message": "Could not read cloth image"}))
    sys.exit(1)

# Load OpenCV's face and upper body detectors
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
upper_body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_upperbody.xml')

def detect_upper_body(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

    if len(faces) == 0:
        # If no face detected, try detecting upper body directly
        upper_bodies = upper_body_cascade.detectMultiScale(
            gray, scaleFactor=1.05, minNeighbors=5, minSize=(100, 100))
        if len(upper_bodies) == 0:
            return None
        (x, y, w, h) = upper_bodies[0]
        width_expansion = 0.6
        upper_body_rect = (
            max(0, x - int(w * width_expansion)),
            y,
            min(frame.shape[1]-1, x + w + int(w * width_expansion)),
            y + int(h * 1.5)
        )
    else:
        (x, y, w, h) = faces[0]
        upper_bodies = upper_body_cascade.detectMultiScale(
            gray[y+h//2:], scaleFactor=1.05, minNeighbors=5, minSize=(w, h))

        if len(upper_bodies) > 0:
            (ub_x, ub_y, ub_w, ub_h) = upper_bodies[0]
            ub_y += y + h//2
            width_expansion = 0.4
            upper_body_rect = (
                max(0, ub_x - int(ub_w * width_expansion)),
                y + h,
                min(frame.shape[1]-1, ub_x + ub_w + int(ub_w * width_expansion)),
                ub_y + int(ub_h * 1.5)
            )
        else:
            neck_y = y + h
            shoulder_width = int(w * 3.5)
            left_shoulder_x = max(0, x - int((shoulder_width - w) / 2))
            right_shoulder_x = min(frame.shape[1]-1, left_shoulder_x + shoulder_width)
            hips_y = neck_y + int(h * 3.5)
            upper_body_rect = (
                left_shoulder_x,
                neck_y,
                right_shoulder_x,
                min(frame.shape[0]-1, hips_y)
            )

    if (upper_body_rect[2] <= upper_body_rect[0]) or (upper_body_rect[3] <= upper_body_rect[1]):
        return None

    return upper_body_rect

def process_cloth_image(cloth_img, target_width, target_height):
    if cloth_img.shape[2] == 4:
        cloth_rgb = cloth_img[:, :, :3]
        mask = cloth_img[:, :, 3]
    else:
        cloth_rgb = cloth_img.copy()
        gray = cv2.cvtColor(cloth_rgb, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)
    cloth_cropped = cloth_rgb[y:y+h, x:x+w]
    mask_cropped = mask[y:y+h, x:x+w]

    scale_width = target_width / w
    scale_height = target_height / h
    effective_scale = max(scale_width, scale_height) * 1.1

    new_w = int(w * effective_scale)
    new_h = int(h * effective_scale)

    cloth_resized = cv2.resize(cloth_cropped, (new_w, new_h))
    mask_resized = cv2.resize(mask_cropped, (new_w, new_h))

    cloth_final = np.zeros((target_height, target_width, 3), dtype=np.uint8)
    mask_final = np.zeros((target_height, target_width), dtype=np.uint8)

    x_offset = max(0, (target_width - new_w) // 2)
    y_offset = 0

    y_end = min(y_offset + new_h, target_height)
    x_end = min(x_offset + new_w, target_width)

    cloth_final[y_offset:y_end, x_offset:x_end] = cloth_resized[:y_end-y_offset, :x_end-x_offset]
    mask_final[y_offset:y_end, x_offset:x_end] = mask_resized[:y_end-y_offset, :x_end-x_offset]

    return cloth_final, mask_final

def overlay_cloth(frame, upper_body_rect, cloth_img, cloth_mask):
    x1, y1, x2, y2 = upper_body_rect
    roi = frame[y1:y2, x1:x2]

    cloth_resized = cv2.resize(cloth_img, (roi.shape[1], roi.shape[0]))
    mask_resized = cv2.resize(cloth_mask, (roi.shape[1], roi.shape[0]))
    mask_normalized = cv2.merge([mask_resized, mask_resized, mask_resized]) / 255.0

    blended_roi = (roi * (1 - mask_normalized) + cloth_resized * mask_normalized).astype(np.uint8)
    frame[y1:y2, x1:x2] = blended_roi
    return frame

async def virtual_try_on_session(websocket, path, cloth_img):
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                await websocket.send(json.dumps({"type": "error", "message": "Failed to capture frame"}))
                break

            frame = cv2.flip(frame, 1)

            upper_body_rect = detect_upper_body(frame)

            if upper_body_rect is not None:
                target_width = upper_body_rect[2] - upper_body_rect[0]
                target_height = upper_body_rect[3] - upper_body_rect[1]
                cloth_processed, cloth_mask_processed = process_cloth_image(cloth_img, target_width, target_height)

                if cloth_processed is not None:
                    frame = overlay_cloth(frame, upper_body_rect, cloth_processed, cloth_mask_processed)

            # Encode frame to JPEG and base64
            ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            if not ret:
                await websocket.send(json.dumps({"type": "error", "message": "Failed to encode frame"}))
                continue

            frame_base64 = base64.b64encode(buffer).decode('utf-8')

            # Send frame as JSON
            await websocket.send(json.dumps({
                "type": "frame",
                "data": frame_base64,
                "timestamp": time.time()
            }))

            await asyncio.sleep(0.05)

    except websockets.ConnectionClosed:
        print(json.dumps({"type": "status", "message": "WebSocket connection closed"}))

async def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Ensure the WebSocket server is properly initialized
    server = await websockets.serve(
        lambda websocket, path: virtual_try_on_session(websocket, path, cloth_img),
        "0.0.0.0",  # Bind to all network interfaces
        args.port,
        ping_interval=None
    )

    logger.info(f"WebSocket server started on ws://0.0.0.0:{args.port}")

    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(json.dumps({"type": "status", "message": "stopping"}))
    finally:
        cap.release()
        cv2.destroyAllWindows()