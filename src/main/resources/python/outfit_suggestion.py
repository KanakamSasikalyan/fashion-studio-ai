import sys
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_base_path():
    """Get the base path of the script, handling both development and packaged execution"""
    try:
        # When running as a script
        base_path = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        # When running in some environments where __file__ isn't defined
        base_path = os.getcwd()
    return base_path

# Path configuration
BASE_DIR = get_base_path()
MODEL_DIR = os.path.join(BASE_DIR, 'model')
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, 'outfit_model.pkl')
VECTORIZER_PATH = os.path.join(MODEL_DIR, 'vectorizer.pkl')
DATA_PATH = os.path.join(BASE_DIR, 'src\\main\\resources\\data', 'unique_outfit_data_large.csv')

def train_model():
    """Train and save the outfit suggestion model"""
    try:
        logger.info(f"Looking for data at: {DATA_PATH}")

        if not os.path.exists(DATA_PATH):
            raise FileNotFoundError(f"Data file not found at: {DATA_PATH}")

        logger.info("Training the model...")

        # Load and prepare data
        df = pd.read_csv(DATA_PATH)
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(df['occasion_text'])
        y = df['outfit']

        # Train model
        model = LogisticRegression(max_iter=1000)
        model.fit(X, y)

        # Save artifacts
        joblib.dump(model, MODEL_PATH)
        joblib.dump(vectorizer, VECTORIZER_PATH)
        logger.info(f"Model saved to: {MODEL_PATH}")

    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        raise

def predict_outfit(prompt):
    """Predict outfit based on occasion text"""
    try:
        # Verify model files exist
        if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
            raise FileNotFoundError("Model files not found. Please train the model first.")

        # Load model and vectorizer
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VECTORIZER_PATH)

        # Transform input and predict
        vec = vectorizer.transform([prompt])
        prediction = model.predict(vec)[0]

        return {
            "status": "success",
            "outfitSuggestion": prediction,
            "message": "Prediction successful"
        }

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "debug": {
                "model_path": MODEL_PATH,
                "vectorizer_path": VECTORIZER_PATH,
                "data_path": DATA_PATH
            }
        }

def check_and_train_model():
    """Check if model exists, train if not"""
    if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
        logger.info("Model files not found. Starting training...")
        train_model()

def main():
    """Main entry point for command line execution"""
    try:
        # Initialize model
        check_and_train_model()

        # Get input from command line arguments
        if len(sys.argv) < 2:
            raise ValueError("Please provide an occasion description as input")

        input_text = " ".join(sys.argv[1:])
        result = predict_outfit(input_text)

        # Output JSON for the Java service to read
        print(json.dumps(result, indent=2))
        sys.stdout.flush()

    except Exception as e:
        error_result = {
            "status": "error",
            "message": str(e),
            "debug": {
                "current_directory": os.getcwd(),
                "script_location": get_base_path(),
                "data_path": DATA_PATH
            }
        }
        print(json.dumps(error_result, indent=2))
        sys.stdout.flush()
        sys.exit(1)

if __name__ == "__main__":
    main()