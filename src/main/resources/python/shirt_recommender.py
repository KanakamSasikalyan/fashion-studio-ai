import argparse
import sys
import json
import cv2
import numpy as np
import spacy
import pandas as pd

nlp = spacy.load("en_core_web_sm")

PLATFORM_SCORES = {
    'Amazon': 0.9, 'Myntra': 0.95, 'Flipkart': 0.85,
    'Nykaa': 0.8, 'Ajio': 0.85, 'Meesho': 0.7, 'Snapdeal': 0.65
}

MATERIAL_SCORES = {
    'organic cotton': 1.0, 'cotton': 0.9, 'linen': 0.85,
    'silk': 0.95, 'polyester': 0.6, 'blend': 0.7
}

def extract_image_features(img_path):
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError(f"Could not read image at {img_path}")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (224, 224))
    pixels = img.reshape(-1, 3).astype(np.float32)
    _, labels, centers = cv2.kmeans(pixels, 3, None,
                                    (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.85),
                                    10, cv2.KMEANS_RANDOM_CENTERS)
    return {
        'dominant_colors': np.uint8(centers).tolist(),
        'avg_color': np.mean(img, axis=(0, 1)).tolist()
    }

def analyze_text(text):
    doc = nlp(text)
    quality_terms = [token.lemma_ for token in doc if token.pos_ in ['ADJ', 'NOUN'] and token.lemma_ in MATERIAL_SCORES]
    material_score = max([MATERIAL_SCORES.get(term, 0) for term in quality_terms] or [0.5])
    return {
        'material_score': material_score,
        'quality_terms': quality_terms,
        'description_length': len(doc)
    }

def build_shirt_features(id, image_path, platform, price, description):
    features = {}
    img_features = extract_image_features(image_path)
    text_features = analyze_text(description)
    platform_score = PLATFORM_SCORES.get(platform.title(), 0.7)
    price = float(price)
    price_norm = 1 - min(1, max(0, (price - 500) / 4500))

    features.update({
        'id': id,
        'image_path': image_path,
        'platform': platform,
        'platform_score': platform_score,
        'price': price,
        'price_norm': price_norm,
        'colors': img_features['dominant_colors'],
        'material': text_features['quality_terms'][0] if text_features['quality_terms'] else 'unknown',
        'material_score': text_features['material_score'],
        'description_score': min(1, text_features['description_length'] / 500),
        'avg_color': img_features['avg_color']
    })
    return features

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image1")
    parser.add_argument("--platform1")
    parser.add_argument("--price1")
    parser.add_argument("--description1")
    parser.add_argument("--image2")
    parser.add_argument("--platform2")
    parser.add_argument("--price2")
    parser.add_argument("--description2")
    parser.add_argument("--platform_weight", type=float)
    parser.add_argument("--price_weight", type=float)
    parser.add_argument("--color_weight", type=float)
    parser.add_argument("--material_weight", type=float)
    parser.add_argument("--description_weight", type=float)
    args = parser.parse_args()

    weights = {
        'platform': args.platform_weight,
        'price': args.price_weight,
        'color': args.color_weight,
        'material': args.material_weight,
        'description': args.description_weight
    }

    try:
        shirts_df = pd.DataFrame([
            build_shirt_features("shirt_1", args.image1, args.platform1, args.price1, args.description1),
            build_shirt_features("shirt_2", args.image2, args.platform2, args.price2, args.description2)
        ])

        shirts_df['score'] = (
            weights['platform'] * shirts_df['platform_score'] +
            weights['price'] * shirts_df['price_norm'] +
            weights['material'] * shirts_df['material_score'] +
            weights['description'] * shirts_df['description_score']
        )

        recommendations = shirts_df.sort_values(by="score", ascending=False)
        print(json.dumps({
            'status': 'success',
            'recommendations': recommendations.to_dict(orient='records'),
            'weights_used': weights
        }))
    except Exception as e:
        print(json.dumps({'status': 'error', 'message': str(e)}))
        sys.exit(1)
