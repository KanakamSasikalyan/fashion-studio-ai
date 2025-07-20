import sys
import json
import logging
import requests
import os
import time
import re
from dotenv import load_dotenv

# Load Hugging Face token (optional)
load_dotenv()
HF_TOKEN = os.getenv("HF_API_KEY")  # Optional, can be left blank for public access

# Logger setup with safer configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

# ✅ Updated with more reliable free models (fallback chain)
FALLBACK_MODELS = [
    "microsoft/DialoGPT-small",  # Moved smaller model first for faster response
    "google/flan-t5-small",      # Changed to small version
    "facebook/blenderbot-400M-distill",
    "gpt2"  # Always available fallback
]

# Construct headers
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Fashion-Studio-AI/1.0"
}
if HF_TOKEN:
    HEADERS["Authorization"] = f"Bearer {HF_TOKEN}"

def sanitize_for_logging(text, max_length=100):
    """Sanitize text for safe logging by removing sensitive information"""
    if not text:
        return "[empty]"
    
    # Remove potential API keys, tokens, or sensitive data patterns
    sanitized = re.sub(r'Bearer\s+[\w\-\.]+', 'Bearer [REDACTED]', str(text))
    sanitized = re.sub(r'token["\s:]+[\w\-\.]+', 'token": "[REDACTED]"', sanitized)
    sanitized = re.sub(r'key["\s:]+[\w\-\.]+', 'key": "[REDACTED]"', sanitized)
    
    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "...[truncated]"
    
    return sanitized

def try_model_with_fallback(prompt, model_url, max_retries=2):
    """Try a model with retry logic"""
    for attempt in range(max_retries):
        try:
            # Simplified payload for better compatibility
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 150,  # Changed from max_new_tokens for compatibility
                    "temperature": 0.7,
                    "return_full_text": False
                },
                "options": {
                    "wait_for_model": True
                }
            }

            logger.info(f"Attempting API call to model (attempt {attempt + 1})")
            
            response = requests.post(
                model_url,
                headers=HEADERS,
                json=payload,
                timeout=45  # Increased timeout
            )

            logger.info(f"API response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                # Validate response format
                if result and (isinstance(result, list) or isinstance(result, dict)):
                    return result
                else:
                    logger.warning("Invalid response format received")
                    return None
            elif response.status_code == 503:
                # Model is loading, wait and retry
                logger.info("Model is loading, waiting 15 seconds...")
                time.sleep(15)
                continue
            elif response.status_code == 429:
                # Rate limit, wait longer
                logger.info("Rate limit hit, waiting 20 seconds...")
                time.sleep(20)
                continue
            else:
                # Log error safely without exposing sensitive data
                error_msg = sanitize_for_logging(response.text)
                logger.warning(f"API error {response.status_code}: {error_msg}")
                return None
                
        except requests.exceptions.Timeout:
            logger.warning(f"Request timeout (attempt {attempt + 1})")
            if attempt < max_retries - 1:
                time.sleep(10)
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed (attempt {attempt + 1}): {sanitize_for_logging(str(e))}")
            if attempt < max_retries - 1:
                time.sleep(5)
        except Exception as e:
            logger.warning(f"Unexpected error (attempt {attempt + 1}): {sanitize_for_logging(str(e))}")
            if attempt < max_retries - 1:
                time.sleep(5)
    
    return None

def create_fashion_prompt(occasion, gender, season):
    """Create a structured prompt for fashion advice"""
    # Simplified prompt for better model compatibility
    return f"Suggest a {gender} outfit for {occasion} in {season} season. Include top, bottom, shoes."

def parse_model_response(raw_output, occasion, gender, season):
    """Parse model response and create structured output"""
    try:
        # Handle different response formats
        response_text = ""
        
        if isinstance(raw_output, list) and len(raw_output) > 0:
            if isinstance(raw_output[0], dict):
                if "generated_text" in raw_output[0]:
                    response_text = raw_output[0]["generated_text"]
                elif "text" in raw_output[0]:
                    response_text = raw_output[0]["text"]
                else:
                    response_text = str(raw_output[0])
            else:
                response_text = str(raw_output[0])
        elif isinstance(raw_output, dict):
            if "generated_text" in raw_output:
                response_text = raw_output["generated_text"]
            elif "text" in raw_output:
                response_text = raw_output["text"]
            else:
                response_text = str(raw_output)
        else:
            response_text = str(raw_output)
        
        # Clean and extract meaningful content
        if response_text:
            # Remove the original prompt if it's echoed back
            prompt_text = f"Suggest a {gender} outfit for {occasion} in {season} season"
            if prompt_text in response_text:
                response_text = response_text.replace(prompt_text, "").strip()
            
            # Split into sentences and take meaningful ones
            sentences = [s.strip() for s in response_text.split('.') if s.strip()]
            meaningful_sentences = [s for s in sentences if len(s) > 10 and any(word in s.lower() for word in ['wear', 'dress', 'shirt', 'pants', 'shoes', 'jacket', 'outfit'])]
            
            if meaningful_sentences:
                main_suggestion = meaningful_sentences[0] + "."
                alternatives = [s + "." for s in meaningful_sentences[1:3]] if len(meaningful_sentences) > 1 else ["Add appropriate accessories", "Consider weather-appropriate layers"]
            else:
                # Create a basic response from the text
                main_suggestion = response_text[:100].strip() + "..." if len(response_text) > 100 else response_text.strip()
                alternatives = ["Consider adding accessories", "Choose weather-appropriate options"]
        else:
            raise ValueError("Empty response received")
        
        return {
            "main_suggestion": main_suggestion if main_suggestion else f"Smart casual attire for {occasion}",
            "alternatives": alternatives,
            "confidence_score": 0.75
        }
        
    except Exception as e:
        logger.warning(f"Response parsing failed: {sanitize_for_logging(str(e))}")
        # Return structured fallback response
        return create_fallback_response(occasion, gender, season)

def create_fallback_response(occasion, gender, season):
    """Create a structured fallback response"""
    occasion_lower = occasion.lower()
    
    # Basic outfit suggestions based on occasion
    if 'wedding' in occasion_lower:
        if gender.lower() in ['male', 'man', 'men']:
            main = "Dark suit with dress shirt, tie, and leather dress shoes"
            alternatives = ["Navy or charcoal suit with white shirt", "Add pocket square for elegance"]
        else:
            main = "Elegant dress or pantsuit with heels and minimal jewelry"
            alternatives = ["Midi dress with blazer", "Professional pantsuit with accessories"]
    elif 'business' in occasion_lower or 'work' in occasion_lower:
        if gender.lower() in ['male', 'man', 'men']:
            main = "Business suit with button-down shirt and tie"
            alternatives = ["Blazer with dress pants", "Polo shirt with chinos for casual Fridays"]
        else:
            main = "Professional blouse with dress pants or pencil skirt"
            alternatives = ["Blazer with midi dress", "Cardigan with professional trousers"]
    else:
        if gender.lower() in ['male', 'man', 'men']:
            main = "Smart casual shirt with chinos and casual shoes"
            alternatives = ["Polo shirt with jeans", "Sweater with dress pants"]
        else:
            main = "Blouse with jeans or casual dress with comfortable shoes"
            alternatives = ["Cardigan with leggings", "Casual dress with flats"]
    
    return {
        "main_suggestion": main,
        "alternatives": alternatives,
        "confidence_score": 0.6
    }

def generate_outfit_suggestion(prompt, gender, season='all'):
    try:
        # Sanitize inputs for logging
        logger.info(f"Generating outfit for: {sanitize_for_logging(prompt)}, gender: {gender}, season: {season}")
        
        full_prompt = create_fashion_prompt(prompt, gender, season)
        
        # Try models in fallback order
        result_data = None
        successful_model = None
        
        for model_name in FALLBACK_MODELS:
            model_url = f"https://api-inference.huggingface.co/models/{model_name}"
            logger.info(f"Trying model: {model_name}")
            
            result_data = try_model_with_fallback(full_prompt, model_url)
            if result_data:
                successful_model = model_name
                logger.info(f"Successfully got response from: {successful_model}")
                break
            else:
                logger.info(f"Model {model_name} failed, trying next...")
        
        if not result_data:
            # If all models fail, provide a fallback response
            logger.warning("All models failed, using fallback response")
            suggestion = create_fallback_response(prompt, gender, season)
            successful_model = "fallback"
        else:
            suggestion = parse_model_response(result_data, prompt, gender, season)

        # Ensure we have valid data
        result = {
            "status": "success",
            "outfitSuggestion": suggestion.get("main_suggestion", f"Appropriate attire for {prompt}"),
            "alternatives": suggestion.get("alternatives", ["Consider seasonal appropriate clothing"]),
            "gender": gender,
            "season": season,
            "confidence": float(suggestion.get("confidence_score", 0.7)),
            "message": "Outfit suggestion generated successfully",
            "model_used": successful_model or "fallback"
        }

        print(json.dumps(result, ensure_ascii=False, indent=None))

    except Exception as e:
        logger.error(f"Prediction failed: {sanitize_for_logging(str(e))}")
        error_result = {
            "status": "error",
            "message": "Unable to generate outfit suggestion. Please try again.",
            "error_type": "generation_error"
        }
        print(json.dumps(error_result))
        sys.exit(1)

def main():
    try:
        if len(sys.argv) == 2:
            generate_outfit_suggestion(sys.argv[1], 'unisex')
        elif len(sys.argv) >= 3:
            occasion = sys.argv[1]
            gender = sys.argv[2].lower()
            season = sys.argv[3].lower() if len(sys.argv) > 3 else 'all'
            generate_outfit_suggestion(occasion, gender, season)
        else:
            raise ValueError("Please provide either a prompt or occasion and gender (optional: season)")

    except Exception as e:
        error_result = {
            "status": "error",
            "message": str(e)
        }
        print(json.dumps(error_result))
        sys.exit(1)

if __name__ == "__main__":
    main()
