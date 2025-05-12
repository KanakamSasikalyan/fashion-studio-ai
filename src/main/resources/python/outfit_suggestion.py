import sys
import pandas as pd
import joblib
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier
import json
import os
import logging
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'model')
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, 'outfit_model.pkl')
VECTORIZER_PATH = os.path.join(MODEL_DIR, 'vectorizer.pkl')
DATA_PATH = os.path.join(BASE_DIR, 'unique_outfit_data_large.csv')

def train_model():
    try:
        logger.info(f"Loading data from: {DATA_PATH}")
        data = pd.read_csv(DATA_PATH)
        logger.info(f"Loaded {len(data)} rows for processing")

        # Combine occasion and gender for training
        data['input_text'] = data['occasion_text'] + ' ' + data['gender']

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

        all_classes = sorted(data['outfit'].unique())
        X = vectorizer.transform(data['input_text'])
        y = data['outfit']
        model.fit(X, y)

        joblib.dump(model, MODEL_PATH)
        joblib.dump(vectorizer, VECTORIZER_PATH)
        logger.info("Model training completed successfully")

    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise

def predict_outfit(prompt, gender):
    try:
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VECTORIZER_PATH)

        input_text = f"{prompt} {gender}"
        X = vectorizer.transform([input_text])
        prediction = model.predict(X)[0]

        return {
            "status": "success",
            "outfitSuggestion": prediction,
            "gender": gender,
            "message": "Prediction successful"
        }
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

def check_and_train_model():
    if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
        logger.info("Model files not found. Starting training...")
        train_model()

def main():
    try:
        check_and_train_model()

        if len(sys.argv) < 3:
            raise ValueError("Please provide occasion and gender")

        occasion = sys.argv[1]
        gender = sys.argv[2]
        result = predict_outfit(occasion, gender)

        sys.stdout.write(json.dumps(result) + "\n")
        sys.stdout.flush()

    except Exception as e:
        error_result = {
            "status": "error",
            "message": str(e)
        }
        sys.stdout.write(json.dumps(error_result) + "\n")
        sys.stdout.flush()
        sys.exit(1)

if __name__ == "__main__":
    main()