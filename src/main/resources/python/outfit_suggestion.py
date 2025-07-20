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

# ✅ Updated with completely public models that don't require authentication
FALLBACK_MODELS = [
    "gpt2",  # Always public and available
    "distilgpt2",  # Smaller, faster version
    "microsoft/DialoGPT-small"  # Keep as backup but may fail
]

# Construct headers WITHOUT authentication for public models
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Fashion-Studio-AI/1.0"
}
# Remove authentication header completely for public access
# if HF_TOKEN:
#     HEADERS["Authorization"] = f"Bearer {HF_TOKEN}"

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

def try_model_with_fallback(prompt, model_url, max_retries=1):  # Reduced retries
    """Try a model with retry logic"""
    for attempt in range(max_retries):
        try:
            # Simplified payload for public models
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 100,
                    "temperature": 0.8,
                    "do_sample": True
                },
                "options": {
                    "wait_for_model": True,
                    "use_cache": True
                }
            }

            logger.info(f"Attempting public API call to model (attempt {attempt + 1})")
            
            response = requests.post(
                model_url,
                headers=HEADERS,
                json=payload,
                timeout=30
            )

            logger.info(f"API response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result and (isinstance(result, list) or isinstance(result, dict)):
                    return result
                else:
                    logger.warning("Invalid response format received")
                    return None
            elif response.status_code == 503:
                logger.info("Model is loading, waiting 10 seconds...")
                time.sleep(10)
                continue
            elif response.status_code == 401:
                logger.info("Model requires authentication, skipping...")
                return None  # Skip this model immediately
            elif response.status_code == 429:
                logger.info("Rate limit hit, skipping model...")
                return None  # Don't wait, just skip
            else:
                error_msg = sanitize_for_logging(response.text)
                logger.warning(f"API error {response.status_code}: {error_msg}")
                return None
                
        except requests.exceptions.Timeout:
            logger.warning(f"Request timeout (attempt {attempt + 1})")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed (attempt {attempt + 1}): {sanitize_for_logging(str(e))}")
        except Exception as e:
            logger.warning(f"Unexpected error (attempt {attempt + 1}): {sanitize_for_logging(str(e))}")
    
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
    """Create a structured fallback response with more detailed suggestions"""
    occasion_lower = occasion.lower()
    season_lower = season.lower()
    
    # Enhanced outfit suggestions based on occasion and season
    if 'wedding' in occasion_lower:
        if gender.lower() in ['male', 'man', 'men']:
            if season_lower in ['summer', 'spring']:
                main = "Light gray or navy suit with white dress shirt, silk tie, and brown leather dress shoes"
                alternatives = ["Linen blend suit for comfort", "Add a boutonniere and pocket square"]
            else:
                main = "Charcoal or navy three-piece suit with white dress shirt, conservative tie, and black leather dress shoes"
                alternatives = ["Dark wool suit with matching vest", "Add cufflinks and dress watch"]
        else:
            if season_lower in ['summer', 'spring']:
                main = "Floral midi dress or elegant jumpsuit with block heels and delicate jewelry"
                alternatives = ["Pastel colored dress with nude heels", "Wrap dress with statement earrings"]
            else:
                main = "Sophisticated cocktail dress or dressy pantsuit with heels and classic jewelry"
                alternatives = ["Velvet dress with pumps", "Silk blouse with dress pants and blazer"]
    
    elif 'business' in occasion_lower or 'work' in occasion_lower or 'office' in occasion_lower:
        if gender.lower() in ['male', 'man', 'men']:
            main = "Navy or charcoal business suit with light blue dress shirt, conservative tie, and black leather dress shoes"
            alternatives = ["Blazer with dress pants and button-down", "Sweater vest with dress shirt and trousers"]
        else:
            main = "Professional blouse with tailored pants or pencil skirt, blazer, and closed-toe heels"
            alternatives = ["Sheath dress with cardigan", "Button-down shirt with A-line skirt"]
    
    elif 'casual' in occasion_lower or 'weekend' in occasion_lower:
        if gender.lower() in ['male', 'man', 'men']:
            main = "Polo shirt or casual button-down with chinos or dark jeans, and loafers or clean sneakers"
            alternatives = ["Henley shirt with jeans", "Casual blazer with polo and khakis"]
        else:
            main = "Comfortable blouse with jeans or casual dress with flats or comfortable sandals"
            alternatives = ["Cardigan with leggings", "Tunic with straight-leg pants"]
    
    elif 'dinner' in occasion_lower or 'restaurant' in occasion_lower:
        if gender.lower() in ['male', 'man', 'men']:
            main = "Dress shirt with dress pants or dark jeans, optional blazer, and leather shoes"
            alternatives = ["Sweater with chinos", "Button-down with blazer and loafers"]
        else:
            main = "Nice blouse with dress pants or knee-length dress with heels or dressy flats"
            alternatives = ["Wrap dress with accessories", "Silk top with skirt"]
    
    else:
        # General occasion
        if gender.lower() in ['male', 'man', 'men']:
            main = "Smart casual shirt with well-fitted pants and leather shoes or clean sneakers"
            alternatives = ["Polo shirt with chinos", "Casual blazer with jeans"]
        else:
            main = "Versatile blouse with jeans or casual dress with comfortable yet stylish shoes"
            alternatives = ["Cardigan with dress pants", "Tunic with leggings"]
    
    # Add seasonal considerations
    seasonal_tips = []
    if season_lower in ['winter', 'cold']:
        seasonal_tips.append("Add a warm coat or wool overcoat")
    elif season_lower in ['summer', 'hot']:
        seasonal_tips.append("Choose breathable fabrics like cotton or linen")
    elif season_lower in ['spring', 'fall', 'autumn']:
        seasonal_tips.append("Layer with a light jacket or cardigan")
    
    if seasonal_tips:
        alternatives = alternatives + seasonal_tips
    
    return {
        "main_suggestion": main,
        "alternatives": alternatives[:3],  # Limit to 3 alternatives
        "confidence_score": 0.8  # Higher confidence for curated responses
    }

def generate_outfit_suggestion(prompt, gender, season='all'):
    try:
        logger.info(f"Generating outfit for: {sanitize_for_logging(prompt)}, gender: {gender}, season: {season}")
        
        # Try a few public models quickly, but don't spend too much time
        full_prompt = create_fashion_prompt(prompt, gender, season)
        result_data = None
        successful_model = None
        
        # Only try 2 models quickly
        for i, model_name in enumerate(FALLBACK_MODELS[:2]):
            model_url = f"https://api-inference.huggingface.co/models/{model_name}"
            logger.info(f"Trying public model: {model_name}")
            
            result_data = try_model_with_fallback(full_prompt, model_url, max_retries=1)
            if result_data:
                successful_model = model_name
                logger.info(f"Successfully got response from: {successful_model}")
                break
            else:
                logger.info(f"Model {model_name} failed, trying next...")
        
        # Always use fallback for reliability (since API models are unreliable)
        if not result_data:
            logger.info("Using enhanced fallback response system")
            suggestion = create_fallback_response(prompt, gender, season)
            successful_model = "enhanced_fallback"
        else:
            try:
                suggestion = parse_model_response(result_data, prompt, gender, season)
            except Exception as parse_error:
                logger.warning(f"Failed to parse model response: {sanitize_for_logging(str(parse_error))}")
                suggestion = create_fallback_response(prompt, gender, season)
                successful_model = "fallback_after_parse_error"

        # Ensure we have valid data
        result = {
            "status": "success",
            "outfitSuggestion": suggestion.get("main_suggestion", f"Appropriate attire for {prompt}"),
            "alternatives": suggestion.get("alternatives", ["Consider seasonal appropriate clothing"]),
            "gender": gender,
            "season": season,
            "confidence": float(suggestion.get("confidence_score", 0.8)),
            "message": "Outfit suggestion generated successfully",
            "model_used": successful_model or "enhanced_fallback"
        }

        print(json.dumps(result, ensure_ascii=False, indent=None))

    except Exception as e:
        logger.error(f"Prediction failed: {sanitize_for_logging(str(e))}")
        # Even in error case, provide a basic outfit suggestion
        try:
            fallback_suggestion = create_fallback_response(prompt or "general", gender, season)
            result = {
                "status": "success",
                "outfitSuggestion": fallback_suggestion["main_suggestion"],
                "alternatives": fallback_suggestion["alternatives"],
                "gender": gender,
                "season": season,
                "confidence": 0.7,
                "message": "Outfit suggestion generated using fallback system",
                "model_used": "error_fallback"
            }
            print(json.dumps(result))
        except Exception as final_error:
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
