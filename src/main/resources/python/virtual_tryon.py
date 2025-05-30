
##==================================================================OLD CODE=====================================================================

import cv2
import numpy as np
import sys
import os
import time
from datetime import datetime
import logging
from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize ImageKit
imagekit = ImageKit(
    private_key='private_bRat8BgH2PReRgIbtw8tp1pFze4=',
    public_key='public_kFHuvOaiMWhxtEDbGKOGTBw9E9g=',
    url_endpoint='https://ik.imagekit.io/sp7ub8zm6'
)

def detect_upper_body(image_path):
    try:
        # Load the image
        image = cv2.imread(image_path)
        if image is None:
            logger.error("Error: Could not read image")
            return None

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Load OpenCV's face and upper body detectors
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        upper_body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_upperbody.xml')

        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100)
        )

        if len(faces) == 0:
            logger.info("No face detected - trying upper body detection directly")
            # If no face detected, try detecting upper body directly
            upper_bodies = upper_body_cascade.detectMultiScale(
                gray,
                scaleFactor=1.05,
                minNeighbors=5,
                minSize=(100, 100)
            )
            if len(upper_bodies) == 0:
                logger.error("No upper body detected")
                return None
            # Use the first upper body detection with expanded width
            (x, y, w, h) = upper_bodies[0]
            # Adjust the rectangle to cover from neck to hips with more width expansion
            width_expansion = 0.6
            upper_body_rect = (
                max(0, x - int(w * width_expansion)),
                y + int(h * 0.3),
                min(image.shape[1]-1, x + w + int(w * width_expansion)),
                y + int(h * 1.2)
            )
        else:
            # Get the first face (assuming one person in the image)
            (x, y, w, h) = faces[0]

            # Detect upper body below the face
            upper_bodies = upper_body_cascade.detectMultiScale(
                gray[y+h//2:],  # Search below face
                scaleFactor=1.05,
                minNeighbors=5,
                minSize=(w, h))

            if len(upper_bodies) > 0:
                # Use the first upper body detection with expanded width
                (ub_x, ub_y, ub_w, ub_h) = upper_bodies[0]
                # Adjust coordinates relative to full image
                ub_y += y + h//2

                width_expansion = 0.4
                # Calculate upper body rectangle
                upper_body_rect = (
                    max(0, ub_x - int(ub_w * width_expansion)),
                    ub_y - int(ub_h * 0.2),
                    min(image.shape[1]-1, ub_x + ub_w + int(ub_w * width_expansion)),
                    ub_y + int(ub_h * 1.1)
                )
            else:
                # Fallback to face-based estimation with expanded width
                #logger.info("Upper body not detected - using face-based estimation")
                # Estimate neck position (below the face)
                neck_y = y + h

                # Estimate shoulder width with more expansion
                shoulder_expansion = 3.15
                shoulder_width = int(w * shoulder_expansion)
                left_shoulder_x = max(0, x - int((shoulder_width - w) / 2))
                right_shoulder_x = min(image.shape[1]-1, left_shoulder_x + shoulder_width)

                # Estimate hips position
                hips_y = neck_y + int(h * 3)

                upper_body_rect = (
                    left_shoulder_x,
                    neck_y,
                    right_shoulder_x,
                    min(image.shape[0]-1, hips_y)
                )

        # Verify the rectangle has valid dimensions
        if (upper_body_rect[2] <= upper_body_rect[0]) or (upper_body_rect[3] <= upper_body_rect[1]):
            logger.error("Invalid upper body dimensions")
            return None

        return image, upper_body_rect
    except Exception as e:
        logger.error(f"Error in detect_upper_body: {str(e)}")
        return None

def process_cloth_image(cloth_path, target_width, target_height):
    try:
        # Load the cloth image with alpha channel if available
        cloth = cv2.imread(cloth_path, cv2.IMREAD_UNCHANGED)
        if cloth is None:
            logger.error("Error: Could not read cloth image")
            return None

        # Configuration parameters
        LEFT_SHIFT_RATIO = 0.18
        RIGHT_SHIFT_AMOUNT = 40
        UPWARD_SHIFT = 15
        CLOTH_SCALE_FACTOR = 1.2
        NECK_CUT_SENSITIVITY = 0.35
        MIN_NECK_WIDTH_RATIO = 0.4

        # Load image and create mask
        if cloth.shape[2] == 4:
            cloth_rgb = cloth[:, :, :3]
            mask = cloth[:, :, 3]
        else:
            cloth_rgb = cloth.copy()
            gray = cv2.cvtColor(cloth_rgb, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
            kernel = np.ones((5,5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

        # Find main clothing contour
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            logger.error("No contours found")
            return None

        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        cloth_cropped = cloth_rgb[y:y+h, x:x+w]
        mask_cropped = mask[y:y+h, x:x+w]

        # Calculate scaling with 5% margin
        max_scale_width = (target_width * 0.95) / w
        max_scale_height = (target_height * 0.95) / h
        effective_scale = min(max_scale_width, max_scale_height) * CLOTH_SCALE_FACTOR
        new_w = int(w * effective_scale)
        new_h = int(h * effective_scale)

        # Resize images
        cloth_resized = cv2.resize(cloth_cropped, (new_w, new_h))
        mask_resized = cv2.resize(mask_cropped, (new_w, new_h))

        # Calculate dynamic left shift
        dynamic_left_shift = int(target_width * LEFT_SHIFT_RATIO)
        x_offset = max(0, (target_width - new_w) // 2 - dynamic_left_shift + RIGHT_SHIFT_AMOUNT)
        y_offset = max(0, (target_height - new_h) // 2 - UPWARD_SHIFT)

        # Create final images
        cloth_final = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        mask_final = np.zeros((target_height, target_width), dtype=np.uint8)

        # Calculate safe copy regions
        y_end = min(y_offset + new_h, target_height)
        x_end = min(x_offset + new_w, target_width)
        copy_height = y_end - y_offset
        copy_width = x_end - x_offset

        # Apply to final images
        cloth_final[y_offset:y_end, x_offset:x_end] = cloth_resized[:copy_height, :copy_width]
        mask_final[y_offset:y_end, x_offset:x_end] = mask_resized[:copy_height, :copy_width]

        return cloth_final, mask_final
    except Exception as e:
        logger.error(f"Error in process_cloth_image: {str(e)}")
        return None

def overlay_cloth(person_image, upper_body_rect, cloth_image, cloth_mask):
    try:
        x1, y1, x2, y2 = upper_body_rect
        upper_body_width = x2 - x1
        upper_body_height = y2 - y1

        mask = cv2.merge([cloth_mask, cloth_mask, cloth_mask]) / 255.0
        roi = person_image[y1:y2, x1:x2]

        cloth_resized = cv2.resize(cloth_image, (roi.shape[1], roi.shape[0]))
        mask_resized = cv2.resize(mask, (roi.shape[1], roi.shape[0]))

        blended_roi = (roi * (1 - mask_resized) + cloth_resized * mask_resized).astype(np.uint8)

        result = person_image.copy()
        result[y1:y2, x1:x2] = blended_roi

        return result
    except Exception as e:
        logger.error(f"Error in overlay_cloth: {str(e)}")
        return None

# def upload_to_imagekit(file_path):
#     try:
#         with open(file_path, 'rb') as file:
#             upload_response = imagekit.upload(
#                 file=file,
#                 file_name=os.path.basename(file_path),
#                 options=UploadFileRequestOptions(
#                     folder="/virtual_tryon_results/",
#                     is_private_file=False
#                 )
#             )
#
#             if hasattr(upload_response, 'response'):
#                 return upload_response.response.url
#             elif isinstance(upload_response, dict) and 'url' in upload_response:
#                 return upload_response['url']
#             else:
#                 raise Exception(f"Unexpected response format: {str(upload_response)}")
#     except Exception as e:
#         logger.error(f"Upload error: {str(e)}")
#         raise

def main():
    if len(sys.argv) < 4:
        logger.error("ERROR: Usage: python virtual_tryon.py <user_image_path> <cloth_image_path> <output_dir>")
        return

    user_image_path = sys.argv[1]
    cloth_image_path = sys.argv[2]
    output_dir = sys.argv[3]

    try:
        # Verify files exist
        if not os.path.exists(user_image_path):
            logger.error(f"ERROR: User image not found at {user_image_path}")
            return
        if not os.path.exists(cloth_image_path):
            logger.error(f"ERROR: Cloth image not found at {cloth_image_path}")
            return

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Step 1: Detect upper body
        result = detect_upper_body(user_image_path)
        if result is None:
            logger.error("ERROR: Failed to detect upper body")
            return

        person_image, upper_body_rect = result
        upper_body_width = upper_body_rect[2] - upper_body_rect[0]
        upper_body_height = upper_body_rect[3] - upper_body_rect[1]

        # Step 2: Process cloth image
        cloth_result = process_cloth_image(cloth_image_path, upper_body_width, upper_body_height)
        if cloth_result is None:
            logger.error("ERROR: Failed to process cloth image")
            return

        cloth_image, cloth_mask = cloth_result

        # Step 3: Overlay cloth on person
        result_image = overlay_cloth(person_image, upper_body_rect, cloth_image, cloth_mask)
        if result_image is None:
            logger.error("ERROR: Failed to overlay cloth")
            return

        # Save result
        #output_path = os.path.join(output_dir, "virtual_try_on_result.jpg")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filename = f"virtual_try_on_{timestamp}.jpg"
        output_path = os.path.join(output_dir, filename)
        cv2.imwrite(output_path, result_image)

        # Upload to ImageKit
        logger.info("Uploading to ImageKit...")
        upload = imagekit.upload_file(
        file=open(output_path, "rb"),
        file_name=filename,
            options=UploadFileRequestOptions(
            folder="/virtual_tryon_results/",
            is_private_file=False
           )
        )

        if upload.response_metadata.http_status_code != 200:
            raise Exception("ImageKit upload failed")

        image_url = upload.url
        logger.info(f"Image uploaded to ImageKit: {image_url}")

        # Clean up temporary file
        os.remove(output_path)
        logger.info(f"Temporary file removed: {output_path}")

        # Return just the URL to Java
        print(image_url)

    except Exception as e:
        logger.error(f"ERROR_MAIN: {str(e)}")
        return

if __name__ == "__main__":
    main()