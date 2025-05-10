import sys
import pandas as pd
import joblib
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier
import json
import os
import logging
import numpy as np

# Configure logging to use stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]  # Changed to stderr
)
logger = logging.getLogger(__name__)

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'model')
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, 'outfit_model.pkl')
VECTORIZER_PATH = os.path.join(MODEL_DIR, 'vectorizer.pkl')
DATA_PATH = os.path.join(BASE_DIR, 'unique_outfit_data_large.csv')

def train_model():
    """Train model with memory-efficient techniques"""
    try:
        logger.info(f"Loading and limiting data to 1000 rows from: {DATA_PATH}")
        data = pd.read_csv(DATA_PATH, nrows=1000)
        logger.info(f"Loaded {len(data)} rows for processing")

        text_chunks = [data]

        vectorizer = HashingVectorizer(
            n_features=2**18,
            alternate_sign=False,
            ngram_range=(1, 2),
            stop_words='english'
        )

        model = SGDClassifier(
            loss='log_loss',
            penalty='l2',
            max_iter=1000,
            tol=1e-4,
            n_jobs=-1
        )

        logger.info("Identifying unique classes...")
        all_classes = sorted(data['outfit'].unique())

        logger.info("Starting incremental training...")
        for i, chunk in enumerate(text_chunks):
            logger.info(f"Processing chunk {i+1}")
            X = vectorizer.transform(chunk['occasion_text'])
            y = chunk['outfit']
            model.partial_fit(X, y, classes=all_classes)

        joblib.dump(model, MODEL_PATH)
        joblib.dump(vectorizer, VECTORIZER_PATH)
        logger.info(f"Model training completed successfully")

    except MemoryError as e:
        logger.error(f"MemoryError encountered: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise

def predict_outfit(prompt):
    """Make prediction with loaded model"""
    try:
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VECTORIZER_PATH)

        X = vectorizer.transform([prompt])
        prediction = model.predict(X)[0]

        return {
            "status": "success",
            "outfitSuggestion": prediction,
            "message": "Prediction successful"
        }
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "debug": {
                "model_path": MODEL_PATH,
                "vectorizer_path": VECTORIZER_PATH
            }
        }

def check_and_train_model():
    """Check if model exists, train if not"""
    if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
        logger.info("Model files not found. Starting training...")
        train_model()

def main():
    """Main entry point"""
    try:
        check_and_train_model()

        if len(sys.argv) < 2:
            raise ValueError("Please provide an occasion description")

        input_text = " ".join(sys.argv[1:])
        result = predict_outfit(input_text)

        # Ensure only JSON is printed to stdout
        sys.stdout.write(json.dumps(result) + "\n")
        sys.stdout.flush()

    except Exception as e:
        error_result = {
            "status": "error",
            "message": str(e),
            "debug": {
                "current_directory": os.getcwd(),
                "script_location": BASE_DIR
            }
        }
        sys.stdout.write(json.dumps(error_result) + "\n")
        sys.stdout.flush()
        sys.exit(1)

if __name__ == "__main__":
    main()