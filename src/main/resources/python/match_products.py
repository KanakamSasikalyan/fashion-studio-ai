import os
import sys
import pandas as pd
import re
import logging
from difflib import SequenceMatcher
from typing import List, Dict

# Configure logging
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='[LOG] %(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)  # Log to stdout so Java can capture
        ]
    )

setup_logging()
logger = logging.getLogger(__name__)

class ProductMatcher:
    def __init__(self):
        try:
            # Load the CSV data
            csv_path = os.path.join(os.path.dirname(__file__), 'filtered_tshirts_shirts_data.csv')
            logger.info(f"Loading product data from: {csv_path}")

            # Read CSV with the correct column names
            self.df = pd.read_csv(csv_path, usecols=['image', 'description', 'display name', 'category'])
            logger.info(f"Successfully loaded {len(self.df)} products")

            # Rename columns to be consistent with our code
            self.df = self.df.rename(columns={
                'display name': 'displayName',
                'image': 'imageUrl'
            })

            # Preprocess data
            self.df['displayName'] = self.df['displayName'].fillna('').astype(str)
            self.df['category'] = self.df['category'].fillna('').astype(str)
            self.df['description'] = self.df['description'].fillna('').astype(str)
            self.df['imageUrl'] = self.df['imageUrl'].fillna('').astype(str)

            logger.debug("Data preprocessing completed")

        except Exception as e:
            logger.error(f"Error initializing ProductMatcher: {str(e)}")
            raise

    def match_products(self, query: str, gender: str = '') -> List[Dict]:
        """
        Match products based on query and gender
        Returns list of matched products with their scores
        """
        logger.info(f"Starting product matching for query: '{query}', gender: '{gender}'")

        try:
            query = query.lower().strip()
            gender = gender.lower().strip()

            # Extract color keywords from query (since we don't have a color column)
            color_keywords = self._extract_color_keywords(query)
            other_keywords = [word for word in query.split() if word not in color_keywords]

            logger.debug(f"Extracted color keywords: {color_keywords}")
            logger.debug(f"Other keywords: {other_keywords}")

            # Score each product
            scored_products = []
            logger.debug(f"Starting to score {len(self.df)} products...")

            for _, row in self.df.iterrows():
                score = 0

                # Gender matching
                if gender and not self._matches_gender(row['description'], gender):
                    continue

                # Color matching (from description since we don't have color column)
                for color in color_keywords:
                    if color in row['description'].lower():
                        score += 2  # Lower weight since we're matching in description only

                # Keyword matching
                for keyword in other_keywords:
                    # Exact matches
                    if keyword in row['displayName'].lower():
                        score += 5
                    if keyword in row['category'].lower():
                        score += 3
                    if keyword in row['description'].lower():
                        score += 1

                    # Partial matches
                    score += self._partial_match_score(keyword, row['displayName'].lower()) * 2
                    score += self._partial_match_score(keyword, row['category'].lower())
                    score += self._partial_match_score(keyword, row['description'].lower()) * 0.5

                # Category specific boosts
                if 'shirt' in query and 'shirt' in row['category'].lower():
                    score += 2
                if 'pant' in query and 'pant' in row['category'].lower():
                    score += 2
                if 'dress' in query and 'dress' in row['category'].lower():
                    score += 2

                if score > 0:
                    scored_products.append({
                        'displayName': row['displayName'],
                        'category': row['category'],
                        'description': row['description'],
                        'imageUrl': row['imageUrl'],
                        'score': score
                    })

            # Sort by score and return top 2
            scored_products.sort(key=lambda x: x['score'], reverse=True)

            logger.info(f"Found {len(scored_products)} matching products")

            # If no matches found, return some random products as fallback
            if not scored_products:
                logger.warning("No matches found, using fallback products")
                return self._get_fallback_products(gender)

            top_products = scored_products[:2]
            logger.info(f"Top products scores: {[p['score'] for p in top_products]}")

            return top_products

        except Exception as e:
            logger.error(f"Error during product matching: {str(e)}")
            raise

    def _extract_color_keywords(self, query: str) -> List[str]:
        """Extract color-related keywords from query"""
        colors = ['red', 'blue', 'green', 'yellow', 'black', 'white',
                  'pink', 'purple', 'orange', 'gray', 'grey', 'brown',
                  'navy', 'maroon', 'teal', 'cyan', 'magenta', 'lime',
                  'olive', 'silver', 'gold', 'beige', 'indigo', 'violet']

        found_colors = []
        for color in colors:
            if color in query:
                found_colors.append(color)
        return found_colors

    def _matches_gender(self, description: str, gender: str) -> bool:
        """Check if product matches gender filter"""
        description = description.lower()
        if gender == 'male':
            return ('men' in description or 'male' in description or
                    "men's" in description or 'man' in description)
        elif gender == 'female':
            return ('women' in description or 'female' in description or
                    "women's" in description or 'woman' in description)
        return True

    def _partial_match_score(self, keyword: str, text: str) -> float:
        """Calculate partial match score using sequence matching"""
        words = text.split()
        max_score = 0
        for word in words:
            score = SequenceMatcher(None, keyword, word).ratio()
            if score > max_score:
                max_score = score
        return max_score if max_score > 0.7 else 0

    def _get_fallback_products(self, gender: str) -> List[Dict]:
        """Get fallback products when no matches found"""
        filtered = self.df
        if gender:
            filtered = self.df[self.df['description'].apply(
                lambda x: self._matches_gender(x, gender)
            )]

        if len(filtered) == 0:
            filtered = self.df

        # Return 2 random products
        fallback = filtered.sample(min(2, len(filtered))).to_dict('records')
        logger.info(f"Selected fallback products: {[p['displayName'] for p in fallback]}")
        return fallback

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python match_products.py <query> [gender]")
        sys.exit(1)

    query = sys.argv[1]
    gender = sys.argv[2] if len(sys.argv) > 2 else ''

    try:
        logger.info("Starting product matching process")
        matcher = ProductMatcher()
        results = matcher.match_products(query, gender)

        # Output results in format that Java can parse
        for product in results:
            print(f"{product['displayName']}|||{product['category']}|||{product['description']}|||{product['imageUrl']}")

        logger.info("Product matching completed successfully")
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        sys.exit(1)