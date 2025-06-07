import sys
import os
import time
import logging
import gc
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
    logger.info(f"Python version: {sys.version}")
    logger.info(f"System CPUs: {psutil.cpu_count()}")
    logger.info(f"Available RAM: {psutil.virtual_memory().available / (1024**3):.2f} GB")

def cleanup_resources():
    """Force cleanup of resources and memory"""
    gc.collect()
    if 'torch' in sys.modules:
        import torch
        torch.cuda.empty_cache()

def load_optimized_model(model_id="runwayml/stable-diffusion-v1-5"):
    """
    Load an optimized Stable Diffusion model for CPU inference using ONNX.
    """
    from diffusers import OnnxStableDiffusionPipeline, OnnxRuntimeModel, DDIMScheduler
    from transformers import CLIPTokenizer

    logger.info("Loading model components...")
    providers = ["CPUExecutionProvider"]

    scheduler = DDIMScheduler.from_pretrained(model_id, subfolder="scheduler")
    tokenizer = CLIPTokenizer.from_pretrained(model_id, subfolder="tokenizer")
    text_encoder = OnnxRuntimeModel.from_pretrained(model_id, subfolder="text_encoder", provider=providers[0])
    unet = OnnxRuntimeModel.from_pretrained(model_id, subfolder="unet", provider=providers[0])
    vae_decoder = OnnxRuntimeModel.from_pretrained(model_id, subfolder="vae_decoder", provider=providers[0])
    vae_encoder = OnnxRuntimeModel.from_pretrained(model_id, subfolder="vae_encoder", provider=providers[0])

    logger.info("Creating Stable Diffusion pipeline...")
    pipe = OnnxStableDiffusionPipeline(
        vae_encoder=vae_encoder,
        vae_decoder=vae_decoder,
        text_encoder=text_encoder,
        tokenizer=tokenizer,
        unet=unet,
        scheduler=scheduler,
        safety_checker=None,
        feature_extractor=None,
        requires_safety_checker=False
    )

    if hasattr(pipe, "enable_attention_slicing"):
        pipe.enable_attention_slicing()

    return pipe

def main():
    try:
        start_time = time.time()
        logger.info("=== New Generation Request ===")

        # Parse CLI arguments
        prompt = sys.argv[1].strip('"')
        style = sys.argv[2]
        gender = sys.argv[3]
        output_dir = sys.argv[4]
        logger.info(f"Prompt: '{prompt}' | Style: {style} | Gender: {gender}")

        log_hardware_info()
        print("PROGRESS:10", flush=True)

        logger.info("Loading optimized Stable Diffusion pipeline...")
        print("PROGRESS:20", flush=True)
        load_start = time.time()
        pipe = load_optimized_model()
        logger.info(f"Model loaded in {time.time() - load_start:.2f}s")
        print("PROGRESS:40", flush=True)

        # Generate image
        logger.info("Generating image (steps=15, size=384x384)...")
        print("PROGRESS:50", flush=True)
        gen_start = time.time()

        formatted_prompt = f"{prompt}, {gender} fashion, {style} style, high quality clothing texture"
        negative_prompt = "low quality, blurry, text, watermark, face, person, human, body"

        image = pipe(
            formatted_prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=15,
            height=384,
            width=384,
            guidance_scale=7.0
        ).images[0]

        logger.info(f"Image generated in {time.time() - gen_start:.2f}s")
        print("PROGRESS:80", flush=True)

        # Save to disk
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"design_{timestamp}_{abs(hash(prompt)) % 1000000}.png"
        output_path = os.path.join(output_dir, filename)
        image.save(output_path)

        # Upload to ImageKit
        logger.info("Uploading to ImageKit...")
        print("PROGRESS:90", flush=True)
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
        os.remove(output_path)
        print(image_url, flush=True)
        print("PROGRESS:100", flush=True)

        logger.info(f"Total execution time: {time.time() - start_time:.2f}s")

    except Exception as e:
        logger.error(f"Generation failed: {str(e)}", exc_info=True)
        print(f"ERROR: {str(e)}", flush=True)
        cleanup_resources()
        sys.exit(1)

if __name__ == "__main__":
    main()