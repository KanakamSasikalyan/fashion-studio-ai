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

# Initialize ImageKit with environment variables for security
imagekit = ImageKit(
    public_key=os.getenv('IMAGEKIT_PUBLIC_KEY', 'public_kFHuvOaiMWhxtEDbGKOGTBw9E9g='),
    private_key=os.getenv('IMAGEKIT_PRIVATE_KEY', 'private_bRat8BgH2PReRgIbtw8tp1pFze4='),
    url_endpoint=os.getenv('IMAGEKIT_URL_ENDPOINT', 'https://ik.imagekit.io/sp7ub8zm6/sp7ub8zm6')
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
        logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")

def main():
    try:
        start_time = time.time()
        logger.info("=== New Generation Request ===")

        # Validate arguments
        if len(sys.argv) < 5:
            raise ValueError("Insufficient arguments provided")

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

        from diffusers import StableDiffusionPipeline  # More specific import
        import torch

        pipe = StableDiffusionPipeline.from_pretrained(
            "CompVis/stable-diffusion-v1-4",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            safety_checker=None,
            use_auth_token=True if os.getenv('HF_AUTH_TOKEN') else False
        ).to("cuda" if torch.cuda.is_available() else "cpu")

        # Enable attention slicing if needed for memory
        if torch.cuda.is_available():
            pipe.enable_attention_slicing()

        logger.info(f"Model loaded in {time.time() - load_start:.2f}s")
        print("PROGRESS:30", flush=True)

        # Enhanced prompt engineering
        negative_prompt = (
            "human, person, face, head, hands, fingers, arms, legs, feet, "
            "body, skin, portrait, selfie, pose, gesture, "
            "deformed, blurry, bad anatomy, disfigured, poorly drawn, "
            "extra limbs, floating limbs, mutated hands, mutated fingers, "
            "text, watermark, mannequin, model, hanger, "
            "folded, wrinkled, crumpled, bent, twisted, "
            "multiple items, crowded, messy, "
            "shadow, dark lighting, poor lighting, "
            "background objects, pattern, texture"
        )

        enhanced_prompt = (
            f"Professional flat lay product photography of a single {prompt} for {gender}, "
            f"{style} style, "
            "perfectly laid flat at 90-degree angle, "
            "completely straight with no folds or bending, "
            "centered in the frame on pure white background, "
            "highly detailed, ultra high resolution, "
            "clean sharp focus, professional studio lighting, "
            "no humans, no body parts, no faces, no mannequins, "
            "only one single clothing item clearly visible, "
            "commercial product photo, e-commerce style"
        )

        # Image generation with better parameters
        logger.info("Generating image (steps=25, size=512x512)...")
        gen_start = time.time()

        with torch.inference_mode():  # More efficient inference
            image = pipe(
                prompt=enhanced_prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=25,
                guidance_scale=8.0,
                height=512,
                width=512
            ).images[0]

        logger.info(f"Generation completed in {time.time() - gen_start:.2f}s")
        print("PROGRESS:70", flush=True)

        # Save temporary file
        output_path = Path(output_dir) / f"design_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{abs(hash(prompt)) % 1000000}.png"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path)
        logger.info(f"Temporary image saved to: {output_path}")
        print("PROGRESS:80", flush=True)

        # Upload to ImageKit
        logger.info("Uploading to ImageKit...")
        with open(output_path, "rb") as file:
            upload = imagekit.upload_file(
                file=file,
                file_name=output_path.name,
                options=UploadFileRequestOptions(
                    folder="/fashion_designs/",
                    is_private_file=False,
                    use_unique_file_name=True  # Ensure unique filenames
                )
            )

        if upload.response_metadata.http_status_code != 200:
            raise Exception(f"ImageKit upload failed: {upload.response_metadata.raw}")

        image_url = upload.url
        logger.info(f"Image uploaded to ImageKit: {image_url}")
        print("PROGRESS:95", flush=True)

        # Clean up temporary file
        output_path.unlink()
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