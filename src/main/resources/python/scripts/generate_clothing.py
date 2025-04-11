import sys
import os
import time
import logging
from datetime import datetime
from pathlib import Path

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

def log_hardware_info():
    #Log system resources and GPU availability
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
        output_dir = sys.argv[3]
        logger.info(f"Prompt: '{prompt}' | Style: {style}")

        # Hardware check
        log_hardware_info()

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

        # Image generation
        logger.info(f"Generating image (steps=25, size=512x512)...")
        gen_start = time.time()

        image = pipe(
            prompt,
            num_inference_steps=25,
            height=512,
            width=512
        ).images[0]

        logger.info(f"Generation completed in {time.time() - gen_start:.2f}s")

        # Save output
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"design_{timestamp}_{abs(hash(prompt)) % 1000000}.png"
        output_path = os.path.join(output_dir, filename)

        image.save(output_path)
        logger.info(f"Image saved to: {output_path}")

        # Return path to Spring Boot
        print(output_path)

        # Save image path to database
        logger.info(f"Image path returned: {output_path}")

        logger.info(f"Total execution time: {time.time() - start_time:.2f}s")

    except Exception as e:
        logger.error(f"Generation failed: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()