#===========================================Enhanced Updated code==============================================
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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'model')
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, 'enhanced_outfit_model.pkl')
DATA_PATH = os.path.join(BASE_DIR, 'enhanced_outfit_dataset.csv')

def preprocess_data(data):
    """Clean and preprocess the data"""
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

        data['input_text'] = data['occasion_text'] + ' ' + data['gender'] + ' ' + data['season']

        classes = np.unique(data['outfit'])
        weights = compute_class_weight('balanced', classes=classes, y=data['outfit'])
        class_weights = dict(zip(classes, weights))

        X_train, X_test, y_train, y_test = train_test_split(
            data['input_text'], data['outfit'],
            test_size=0.2,
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
        raise

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

        # Get top 5 predictions
        top_predictions = sorted(zip(classes, probas), key=lambda x: x[1], reverse=True)[:5]

        # Filter out the main prediction and get top 2 alternatives
        alternatives = []
        for outfit, prob in top_predictions:
            if outfit != prediction:
                # Ensure gender appropriateness
                if gender == 'unisex' or gender in outfit.lower() or 'unisex' in outfit.lower():
                    alternatives.append(outfit)
                    if len(alternatives) >= 2:
                        break

        # Prepare result with properly spelled 'alternatives' key
        result = {
            "status": "success",
            "outfitSuggestion": prediction,
            "alternatives": alternatives,  # Fixed the typo here
            "gender": gender,
            "season": season,
            "message": "Enhanced prediction successful",
            "confidence": float(max(probas))  # Add confidence score
        }

        print(json.dumps(result))

    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        error_result = {
            "status": "error",
            "message": str(e)
        }
        print(json.dumps(error_result))

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

        if len(sys.argv) < 3:
            raise ValueError("Please provide occasion and gender (optional: season)")

        occasion = sys.argv[1]
        gender = sys.argv[2].lower()
        season = sys.argv[3].lower() if len(sys.argv) > 3 else 'all'

        predict_outfit(occasion, gender, season)

    except Exception as e:
        error_result = {
            "status": "error",
            "message": str(e)
        }
        print(json.dumps(error_result))
        sys.exit(1)

if __name__ == "__main__":
    main()


#=========================================Old: currently using code================================
"""
import sys
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
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

MODEL_PATH = os.path.join(MODEL_DIR, 'enhanced_outfit_model.pkl')
VECTORIZER_PATH = os.path.join(MODEL_DIR, 'enhanced_vectorizer.pkl')
DATA_PATH = os.path.join(BASE_DIR, 'enhanced_outfit_dataset.csv')

def train_model():
    try:
        logger.info(f"Loading enhanced data from: {DATA_PATH}")
        data = pd.read_csv(DATA_PATH)
        logger.info(f"Loaded {len(data)} rows for processing")

        # Combine occasion and gender for training
        data['input_text'] = data['occasion_text'] + ' ' + data['season']

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            data['input_text'], data['outfit'], test_size=0.2, random_state=42
        )

        # Create pipeline
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                ngram_range=(1, 2),
                stop_words='english',
                max_features=10000
            )),
            ('clf', RandomForestClassifier(
                n_estimators=100,
                max_depth=15,
                random_state=42,
                n_jobs=-1
            ))
        ])

        # Train
        pipeline.fit(X_train, y_train)

        # Evaluate
        train_score = pipeline.score(X_train, y_train)
        test_score = pipeline.score(X_test, y_test)
        logger.info(f"Training accuracy: {train_score:.2f}, Test accuracy: {test_score:.2f}")

        # Save model
        joblib.dump(pipeline, MODEL_PATH)
        logger.info("Enhanced model training completed successfully")

    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise

def predict_outfit(prompt, gender, season='all'):
    try:
        pipeline = joblib.load(MODEL_PATH)

        input_text = f"{prompt} {gender} {season}"
        prediction = pipeline.predict([input_text])[0]

        # Get top 3 alternatives
        probas = pipeline.predict_proba([input_text])[0]
        classes = pipeline.classes_
        top_3 = sorted(zip(classes, probas), key=lambda x: x[1], reverse=True)[:3]
        alternatives = [outfit for outfit, prob in top_3 if outfit != prediction][:2]

        # Ensure proper JSON formatting
        result = {
            "status": "success",
            "outfitSuggestion": prediction,
            "alternatives": alternatives,
            "gender": gender,
            "season": season,
            "message": "Enhanced prediction successful"
        }

        # Convert to JSON string and print
        json_result = json.dumps(result)
        print(json_result)  # This will be read by Java

    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        error_result = {
            "status": "error",
            "message": str(e)
        }
        print(json.dumps(error_result))

def check_and_train_model():
    if not os.path.exists(MODEL_PATH):
        logger.info("Enhanced model not found. Starting training...")
        train_model()

def main():
    try:
        check_and_train_model()

        if len(sys.argv) < 3:
            raise ValueError("Please provide occasion and gender (optional: season)")

        occasion = sys.argv[1]
        gender = sys.argv[2]
        season = sys.argv[3] if len(sys.argv) > 3 else 'all'

        result = predict_outfit(occasion, gender, season)
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
    main()"""

#################################OLD CODE######################################################
"""import sys
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
    main()"""