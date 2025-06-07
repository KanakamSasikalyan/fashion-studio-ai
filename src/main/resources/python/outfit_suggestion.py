import sys
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import json
import os
import logging
import numpy as np
from sklearn.utils.class_weight import compute_class_weight

# Configure logging to stderr only
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]  # Only stderr for logs
)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'model')
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, 'enhanced_outfit_model.pkl')
DATA_PATH = os.path.join(BASE_DIR, 'enhanced_outfit_dataset.csv')

def preprocess_data(data):
    data = data.dropna()
    data = data[data['outfit'].str.strip() != '']
    data = data[data['gender'].isin(['male', 'female', 'unisex'])]
    return data

def train_model():
    try:
        logger.info(f"Loading enhanced data from: {DATA_PATH}")
        data = pd.read_csv(DATA_PATH)
        logger.info(f"Initial dataset size: {len(data)} rows")

        data = preprocess_data(data)
        logger.info(f"Dataset size after preprocessing: {len(data)} rows")

        # Remove classes with fewer than 2 samples
        class_counts = data['outfit'].value_counts()
        valid_classes = class_counts[class_counts >= 2].index
        data = data[data['outfit'].isin(valid_classes)]
        logger.info(f"Dataset size after removing rare classes: {len(data)} rows")

        # Check if we have enough samples per class
        min_samples_per_class = 2
        class_counts = data['outfit'].value_counts()
        if len(class_counts) == 0 or any(class_counts < min_samples_per_class):
            raise ValueError(f"Not enough samples per class. Need at least {min_samples_per_class} samples per class.")

        # Adjust test_size if dataset is too small
        test_size = 0.2
        min_test_size = len(class_counts)  # Need at least one sample per class in test set
        if len(data) * test_size < min_test_size:
            test_size = min_test_size / len(data)
            if test_size >= 1.0:
                raise ValueError("Dataset too small for proper training and testing")
            logger.info(f"Adjusting test_size to {test_size:.2f} due to small dataset")

        data['input_text'] = data['occasion_text'] + ' ' + data['gender'] + ' ' + data['season']

        classes = np.unique(data['outfit'])
        weights = compute_class_weight('balanced', classes=classes, y=data['outfit'])
        class_weights = dict(zip(classes, weights))

        X_train, X_test, y_train, y_test = train_test_split(
            data['input_text'], data['outfit'],
            test_size=test_size,
            random_state=42,
            stratify=data['outfit']
        )

        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                ngram_range=(1, 3),
                stop_words='english',
                max_features=15000,
                min_df=2,
                max_df=0.95
            )),
            ('clf', RandomForestClassifier(
                n_estimators=200,
                max_depth=20,
                min_samples_split=5,
                class_weight=class_weights,
                random_state=42,
                n_jobs=-1
            ))
        ])

        logger.info("Starting model training...")
        pipeline.fit(X_train, y_train)

        train_score = pipeline.score(X_train, y_train)
        test_score = pipeline.score(X_test, y_test)
        logger.info(f"Training accuracy: {train_score:.2f}, Test accuracy: {test_score:.2f}")

        y_pred = pipeline.predict(X_test)
        logger.info("Classification Report:\n" + classification_report(y_test, y_pred))

        joblib.dump(pipeline, MODEL_PATH)
        logger.info("Enhanced model training completed successfully")

    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        error_result = {
            "status": "error",
            "message": str(e)
        }
        print(json.dumps(error_result), file=sys.stdout)
        sys.exit(1)

# ... rest of the file remains the same ...

def predict_outfit(prompt, gender, season='all'):
    try:
        gender = gender.lower().strip()
        if gender not in ['male', 'female', 'unisex']:
            raise ValueError("Gender must be 'male', 'female', or 'unisex'")

        season = season.lower().strip()
        valid_seasons = ['spring', 'summer', 'fall', 'winter', 'all']
        if season not in valid_seasons:
            raise ValueError(f"Season must be one of: {', '.join(valid_seasons)}")

        pipeline = joblib.load(MODEL_PATH)

        input_text = f"{prompt.lower().strip()} {gender} {season}"

        prediction = pipeline.predict([input_text])[0]
        probas = pipeline.predict_proba([input_text])[0]
        classes = pipeline.classes_

        # Get top 2 alternatives excluding the main prediction
        top_predictions = sorted(zip(classes, probas), key=lambda x: x[1], reverse=True)[:5]
        alternatives = [outfit for outfit, _ in top_predictions if outfit != prediction][:2]

        result = {
            "status": "success",
            "outfitSuggestion": prediction,
            "alternatives": alternatives,
            "gender": gender,
            "season": season,
            "message": "Enhanced prediction successful",
            "confidence": float(max(probas))
        }

        # Print only the JSON to stdout
        print(json.dumps(result), file=sys.stdout)

    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        error_result = {
            "status": "error",
            "message": str(e)
        }
        print(json.dumps(error_result), file=sys.stdout)

def check_and_train_model():
    if not os.path.exists(MODEL_PATH):
        logger.info("Enhanced model not found. Starting training...")
        train_model()
    else:
        model_time = os.path.getmtime(MODEL_PATH)
        data_time = os.path.getmtime(DATA_PATH)
        if data_time > model_time:
            logger.info("Dataset has been updated. Retraining model...")
            train_model()

def main():
    try:
        check_and_train_model()

        # If only one argument (besides script name), treat as prompt
        if len(sys.argv) == 2:
            prompt = sys.argv[1]
            gender = 'unisex'
            season = 'all'
            predict_outfit(prompt, gender, season)
        elif len(sys.argv) >= 3:
            occasion = sys.argv[1]
            gender = sys.argv[2].lower()
            season = sys.argv[3].lower() if len(sys.argv) > 3 else 'all'
            predict_outfit(occasion, gender, season)
        else:
            raise ValueError("Please provide either a prompt or occasion and gender (optional: season)")

    except Exception as e:
        error_result = {
            "status": "error",
            "message": str(e)
        }
        print(json.dumps(error_result), file=sys.stdout)
        sys.exit(1)

if __name__ == "__main__":
    main()