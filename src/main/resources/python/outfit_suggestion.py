import random
from enum import Enum
import json
from typing import List, Dict, Tuple
from dataclasses import dataclass
import sys
import re

class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    UNISEX = "unisex"

class Season(Enum):
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    WINTER = "winter"
    ALL = "all"

class Occasion(Enum):
    CASUAL = "casual"
    FORMAL = "formal"
    BUSINESS = "business"
    SPORTS = "sports"
    PARTY = "party"
    DATE = "date"
    BEACH = "beach"
    TRADITIONAL = "traditional"
    OFFICE = "office"
    HIKING = "hiking"
    INTERVIEW = "interview"
    DATE_NIGHT = "date night"
    SHOPPING = "shopping"
    WEDDING = "wedding"
    OTHER = "other"

@dataclass
class ClothingItem:
    name: str
    colors: List[str]
    genders: List[Gender]
    seasons: List[Season]
    occasions: List[Occasion]
    layer: int

class OutfitGenerator:
    def __init__(self):
        self.clothing_items = self._initialize_clothing_items()
        self.color_rules = {
            'red': ['white', 'black', 'navy', 'gray'],
            'blue': ['white', 'gray', 'beige', 'khaki'],
            'green': ['brown', 'beige', 'white', 'navy'],
            'black': ['white', 'gray', 'red', 'pink'],
            'white': ['black', 'navy', 'red', 'pastel'],
            'gray': ['black', 'white', 'pink', 'blue'],
            'brown': ['beige', 'white', 'green', 'blue'],
            'beige': ['brown', 'white', 'navy', 'black'],
            'navy': ['white', 'beige', 'red', 'pink'],
            'pink': ['gray', 'white', 'navy', 'black'],
            'yellow': ['white', 'black', 'blue', 'gray'],
            'purple': ['white', 'black', 'gray', 'silver']
        }
        self.seasonal_colors = {
            Season.SPRING: ['pastel', 'light blue', 'pink', 'lilac', 'mint'],
            Season.SUMMER: ['white', 'navy', 'red', 'yellow', 'light blue'],
            Season.FALL: ['brown', 'orange', 'burgundy', 'olive', 'mustard'],
            Season.WINTER: ['black', 'gray', 'navy', 'red', 'white'],
            Season.ALL: list(self.color_rules.keys())
        }
        self.occasion_keywords = {
            Occasion.CASUAL: ['casual', 'relaxed', 'everyday'],
            Occasion.FORMAL: ['formal', 'gala', 'black tie'],
            Occasion.BUSINESS: ['business', 'office', 'work'],
            Occasion.SPORTS: ['sports', 'gym', 'workout'],
            Occasion.PARTY: ['party', 'club', 'night out'],
            Occasion.DATE: ['date', 'romantic'],
            Occasion.BEACH: ['beach', 'pool', 'swim'],
            Occasion.TRADITIONAL: ['traditional', 'cultural', 'ethnic'],
            Occasion.OFFICE: ['office', 'work', 'professional'],
            Occasion.HIKING: ['hiking', 'trek', 'outdoor'],
            Occasion.INTERVIEW: ['interview', 'job'],
            Occasion.DATE_NIGHT: ['date night', 'romantic'],
            Occasion.SHOPPING: ['shopping', 'mall'],
            Occasion.WEDDING: ['wedding', 'marriage']
        }

    def _initialize_clothing_items(self) -> List[ClothingItem]:
        items = [
            ClothingItem("t-shirt", ['white', 'black', 'gray', 'navy', 'red'],
                        [Gender.MALE, Gender.FEMALE, Gender.UNISEX],
                        [Season.SPRING, Season.SUMMER, Season.FALL],
                        [Occasion.CASUAL, Occasion.SPORTS], 1),
            ClothingItem("dress shirt", ['white', 'blue', 'pink', 'lavender'],
                        [Gender.MALE, Gender.FEMALE, Gender.UNISEX],
                        [Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER],
                        [Occasion.FORMAL, Occasion.BUSINESS, Occasion.DATE], 1),
            ClothingItem("blouse", ['white', 'black', 'pastel', 'floral'],
                        [Gender.FEMALE],
                        [Season.SPRING, Season.SUMMER, Season.FALL],
                        [Occasion.FORMAL, Occasion.BUSINESS, Occasion.DATE], 1),
            ClothingItem("sweater", ['navy', 'gray', 'black', 'burgundy'],
                        [Gender.MALE, Gender.FEMALE, Gender.UNISEX],
                        [Season.FALL, Season.WINTER],
                        [Occasion.CASUAL, Occasion.BUSINESS], 2),
            ClothingItem("cardigan", ['beige', 'gray', 'black', 'pastel'],
                        [Gender.FEMALE, Gender.UNISEX],
                        [Season.SPRING, Season.FALL],
                        [Occasion.CASUAL, Occasion.BUSINESS], 2),
            ClothingItem("hoodie", ['black', 'gray', 'navy', 'olive'],
                        [Gender.MALE, Gender.FEMALE, Gender.UNISEX],
                        [Season.SPRING, Season.FALL, Season.WINTER],
                        [Occasion.CASUAL, Occasion.SPORTS], 2),
            ClothingItem("trench coat", ['beige', 'black', 'navy'],
                        [Gender.MALE, Gender.FEMALE, Gender.UNISEX],
                        [Season.SPRING, Season.FALL],
                        [Occasion.FORMAL, Occasion.BUSINESS], 3),
            ClothingItem("parka", ['black', 'navy', 'olive'],
                        [Gender.MALE, Gender.FEMALE, Gender.UNISEX],
                        [Season.WINTER],
                        [Occasion.CASUAL], 3),
            ClothingItem("denim jacket", ['blue', 'black', 'white'],
                        [Gender.MALE, Gender.FEMALE, Gender.UNISEX],
                        [Season.SPRING, Season.SUMMER, Season.FALL],
                        [Occasion.CASUAL], 3),
            ClothingItem("jeans", ['blue', 'black', 'gray', 'white'],
                        [Gender.MALE, Gender.FEMALE, Gender.UNISEX],
                        [Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER],
                        [Occasion.CASUAL, Occasion.PARTY], 1),
            ClothingItem("dress pants", ['black', 'gray', 'navy', 'khaki'],
                        [Gender.MALE, Gender.FEMALE, Gender.UNISEX],
                        [Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER],
                        [Occasion.FORMAL, Occasion.BUSINESS], 1),
            ClothingItem("skirt", ['black', 'navy', 'gray', 'floral'],
                        [Gender.FEMALE],
                        [Season.SPRING, Season.SUMMER, Season.FALL],
                        [Occasion.FORMAL, Occasion.BUSINESS, Occasion.DATE], 1),
            ClothingItem("sneakers", ['white', 'black', 'gray', 'navy'],
                        [Gender.MALE, Gender.FEMALE, Gender.UNISEX],
                        [Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER],
                        [Occasion.CASUAL, Occasion.SPORTS], 1),
            ClothingItem("dress shoes", ['black', 'brown', 'oxblood'],
                        [Gender.MALE, Gender.FEMALE, Gender.UNISEX],
                        [Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER],
                        [Occasion.FORMAL, Occasion.BUSINESS], 1),
            ClothingItem("boots", ['black', 'brown', 'tan'],
                        [Gender.MALE, Gender.FEMALE, Gender.UNISEX],
                        [Season.FALL, Season.WINTER],
                        [Occasion.CASUAL, Occasion.FORMAL], 1),
            ClothingItem("scarf", ['red', 'blue', 'gray', 'black', 'patterned'],
                        [Gender.MALE, Gender.FEMALE, Gender.UNISEX],
                        [Season.FALL, Season.WINTER],
                        [Occasion.CASUAL, Occasion.FORMAL], 0),
            ClothingItem("tie", ['red', 'blue', 'silver', 'black', 'patterned'],
                        [Gender.MALE, Gender.UNISEX],
                        [Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER],
                        [Occasion.FORMAL, Occasion.BUSINESS], 0),
            ClothingItem("sari", ['red', 'blue', 'green', 'gold', 'purple'],
                        [Gender.FEMALE],
                        [Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER],
                        [Occasion.TRADITIONAL, Occasion.WEDDING], 1),
            ClothingItem("sherwani", ['white', 'gold', 'black', 'navy'],
                        [Gender.MALE],
                        [Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER],
                        [Occasion.TRADITIONAL, Occasion.WEDDING], 1),
            ClothingItem("hiking pants", ['green', 'brown', 'black', 'khaki'],
                        [Gender.MALE, Gender.FEMALE, Gender.UNISEX],
                        [Season.SPRING, Season.SUMMER, Season.FALL],
                        [Occasion.HIKING], 1)
        ]
        return items

    def _parse_prompt(self, prompt: str) -> Tuple[str, str, str]:
        prompt = prompt.lower().strip()
        gender = None
        season = None
        occasion = None

        gender_keywords = {
            Gender.MALE: ['male', 'man', 'gentleman', 'boy'],
            Gender.FEMALE: ['female', 'woman', 'lady', 'girl'],
            Gender.UNISEX: ['unisex', 'any', 'all']
        }

        season_keywords = {
            Season.SPRING: ['spring'],
            Season.SUMMER: ['summer'],
            Season.FALL: ['fall', 'autumn'],
            Season.WINTER: ['winter'],
            Season.ALL: ['all', 'any']
        }

        for g, keywords in gender_keywords.items():
            if any(k in prompt for k in keywords):
                gender = g.value
                break
        if not gender:
            gender = Gender.UNISEX.value

        for s, keywords in season_keywords.items():
            if any(k in prompt for k in keywords):
                season = s.value
                break
        if not season:
            season = Season.ALL.value

        for occ, keywords in self.occasion_keywords.items():
            if any(k in prompt for k in keywords):
                occasion = occ.value
                break
        if not occasion:
            occasion = Occasion.OTHER.value

        return (gender, season, occasion)

    def _filter_items(self, gender: Gender, season: Season, occasion: Occasion) -> List[ClothingItem]:
        return [item for item in self.clothing_items
                if gender in item.genders
                and season in item.seasons
                and occasion in item.occasions]

    def _get_color_palette(self, season: Season) -> List[str]:
        return self.seasonal_colors.get(season, self.seasonal_colors[Season.ALL])

    def _get_complementary_color(self, base_color: str) -> str:
        if base_color in self.color_rules:
            return random.choice(self.color_rules[base_color])
        return random.choice(['white', 'black', 'gray'])

    def _generate_outfit(self, gender: Gender, season: Season, occasion: Occasion) -> Dict:
        filtered_items = self._filter_items(gender, season, occasion)
        color_palette = self._get_color_palette(season)
        base_color = random.choice(color_palette)

        outfit = {
            "base_layer": None,
            "mid_layer": None,
            "outer_layer": None,
            "bottom": None,
            "footwear": None,
            "accessories": []
        }

        for layer in range(1, 4):
            layer_items = [item for item in filtered_items if item.layer == layer]
            if layer_items:
                item = random.choice(layer_items)
                color = base_color if layer == 1 else self._get_complementary_color(base_color)
                available_colors = [c for c in item.colors if c in color_palette]
                color = random.choice(available_colors) if available_colors else random.choice(item.colors)

                if layer == 1:
                    outfit["base_layer"] = f"{color} {item.name}"
                elif layer == 2:
                    outfit["mid_layer"] = f"{color} {item.name}"
                elif layer == 3:
                    outfit["outer_layer"] = f"{color} {item.name}"

        bottoms = [item for item in filtered_items
                  if "pants" in item.name or "jeans" in item.name or "skirt" in item.name]
        if bottoms:
            bottom = random.choice(bottoms)
            color = self._get_complementary_color(base_color)
            available_colors = [c for c in bottom.colors if c in color_palette]
            color = random.choice(available_colors) if available_colors else random.choice(bottom.colors)
            outfit["bottom"] = f"{color} {bottom.name}"

        footwear = [item for item in filtered_items
                   if "shoes" in item.name or "boots" in item.name or "sneakers" in item.name]
        if footwear:
            shoe = random.choice(footwear)
            color = random.choice(['black', 'brown', 'white'])
            outfit["footwear"] = f"{color} {shoe.name}"

        accessories = [item for item in filtered_items if item.layer == 0]
        if accessories:
            num_accessories = random.randint(0, 2)
            for _ in range(num_accessories):
                accessory = random.choice(accessories)
                color = random.choice(accessory.colors)
                outfit["accessories"].append(f"{color} {accessory.name}")

        return outfit

    def _format_outfit(self, outfit: Dict) -> str:
        parts = []
        if outfit["base_layer"]:
            parts.append(outfit["base_layer"])
        if outfit["mid_layer"]:
            parts.append(outfit["mid_layer"])
        if outfit["outer_layer"]:
            parts.append(outfit["outer_layer"])
        if outfit["bottom"]:
            parts.append(outfit["bottom"])
        if outfit["footwear"]:
            parts.append(outfit["footwear"])
        if outfit["accessories"]:
            parts.extend(outfit["accessories"])
        return " with ".join(parts)

    def generate_outfits(self, gender: str, season: str, occasion: str, count: int = 3) -> Dict:
        try:
            gender_enum = Gender(gender.lower())
            season_enum = Season(season.lower())
            occasion_enum = Occasion(occasion.lower())

            main_outfit = self._generate_outfit(gender_enum, season_enum, occasion_enum)
            alternatives = [
                self._format_outfit(self._generate_outfit(gender_enum, season_enum, occasion_enum))
                for _ in range(2)
            ]

            return {
                "status": "success",
                "outfitSuggestion": self._format_outfit(main_outfit),
                "alternatives": alternatives,
                "gender": gender_enum.value,
                "season": season_enum.value,
                "message": "Outfit recommendation successful",
                "confidence": round(random.uniform(0.7, 0.95), 2)
            }
        except ValueError as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def generate_from_prompt(self, prompt: str) -> Dict:
        gender, season, occasion = self._parse_prompt(prompt)
        return self.generate_outfits(gender, season, occasion)

def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "error",
            "message": "Please provide either a prompt or gender, season and occasion"
        }))
        sys.exit(1)

    generator = OutfitGenerator()

    if len(sys.argv) == 2:
        result = generator.generate_from_prompt(sys.argv[1])
    else:
        if len(sys.argv) < 4:
            print(json.dumps({
                "status": "error",
                "message": "Please provide gender, season and occasion as arguments"
            }))
            sys.exit(1)

        occasion = sys.argv[1]
        gender = sys.argv[2]
        season = sys.argv[3]
        result = generator.generate_outfits(gender, season, occasion)

    print(json.dumps(result))

if __name__ == "__main__":
    main()


#=========================Enhanced Code Functionality - Deployment===================================
"""import sys
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
        print(json.dumps(error_result), file=sys.stdout)
        sys.exit(1)

if __name__ == "__main__":
    main()"""