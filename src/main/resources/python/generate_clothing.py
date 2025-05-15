import sys
import os
import time
import logging
from datetime import datetime
from pathlib import Path
from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('FashionAI')

# Initialize ImageKit
imagekit = ImageKit(
    public_key='public_kFHuvOaiMWhxtEDbGKOGTBw9E9g=',
    private_key='private_bRat8BgH2PReRgIbtw8tp1pFze4=',
    url_endpoint='https://ik.imagekit.io/sp7ub8zm6/sp7ub8zm6'
)

def log_hardware_info():
    import psutil
    import torch

    logger.info(f"Python version: {sys.version}")
    logger.info(f"System CPUs: {psutil.cpu_count()}")
    logger.info(f"Available RAM: {psutil.virtual_memory().available / (1024**3):.2f} GB")
    logger.info(f"CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
        logger.info(f"GPU Memory: {torch.cuda.mem_get_info()[1] / (1024**3):.2f} GB")

def main():
    try:
        # Start timing
        start_time = time.time()
        logger.info("=== New Generation Request ===")

        # Parse arguments
        prompt = sys.argv[1].strip('"')
        style = sys.argv[2]
        gender = sys.argv[3]
        output_dir = sys.argv[4]
        logger.info(f"Prompt: '{prompt}' | Style: {style} | Gender: {gender}")

        # Hardware check
        log_hardware_info()
        print("PROGRESS:10", flush=True)

        # Model loading
        logger.info("Loading Stable Diffusion pipeline...")
        load_start = time.time()

        from diffusers import DiffusionPipeline
        import torch

        pipe = DiffusionPipeline.from_pretrained(
            "CompVis/stable-diffusion-v1-4",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            safety_checker=None
        ).to("cuda" if torch.cuda.is_available() else "cpu")

        logger.info(f"Model loaded in {time.time() - load_start:.2f}s")
        print("PROGRESS:30", flush=True)

        # Image generation
        logger.info(f"Generating image (steps=25, size=512x512)...")
        gen_start = time.time()

        # Add gender to prompt for better results
        tempPrompt = f"{prompt}, for a {gender}, Note:strictly no human faces or gestures are to be included."

        image = pipe(
            tempPrompt,
            num_inference_steps=25,
            height=512,
            width=512
        ).images[0]

        logger.info(f"Generation completed in {time.time() - gen_start:.2f}s")
        print("PROGRESS:70", flush=True)

        # Save temporary file
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"design_{timestamp}_{abs(hash(prompt)) % 1000000}.png"
        output_path = os.path.join(output_dir, filename)
        image.save(output_path)
        logger.info(f"Temporary image saved to: {output_path}")
        print("PROGRESS:80", flush=True)

        # Upload to ImageKit
        logger.info("Uploading to ImageKit...")
        upload = imagekit.upload_file(
            file=open(output_path, "rb"),
            file_name=filename,
            options=UploadFileRequestOptions(
                folder="/fashion_designs/",
                is_private_file=False
            )
        )

        if upload.response_metadata.http_status_code != 200:
            raise Exception("ImageKit upload failed")

        image_url = upload.url
        logger.info(f"Image uploaded to ImageKit: {image_url}")
        print("PROGRESS:95", flush=True)

        # Clean up temporary file
        os.remove(output_path)
        logger.info(f"Temporary file removed: {output_path}")

        # Return just the URL to Java
        print(image_url, flush=True)
        print("PROGRESS:100", flush=True)

        logger.info(f"Total execution time: {time.time() - start_time:.2f}s")

    except Exception as e:
        logger.error(f"Generation failed: {str(e)}", exc_info=True)
        print(f"ERROR: {str(e)}", flush=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
