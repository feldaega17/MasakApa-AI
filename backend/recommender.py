import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from typing import List, Dict, Any

# Synonym dictionary for normalization
SYNONYMS = {
    "cabai merah": "cabai",
    "cabe": "cabai",
    "bawang merah": "bawang",
    "bawang putih": "bawang putih",
    "ayam broiler": "ayam",
    "daging ayam": "ayam",
}

class RecommendationEngine:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.df = None
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = None
        self.load_data()

    def clean_text(self, text: str) -> str:
        """Basic cleaning and synonym replacement."""
        if not isinstance(text, str):
            return ""
        text = text.lower()
        for k, v in SYNONYMS.items():
            text = text.replace(k, v)
        return text

    def extract_ingredient_list(self, text: str) -> List[str]:
        """Extract a list of ingredients from a comma-separated string."""
        cleaned = self.clean_text(text)
        items = cleaned.split(',')
        processed_items = []
        for item in items:
            # Remove unnecessary symbols
            item = re.sub(r'[^\w\s]', ' ', item)
            # Normalize spaces and strip whitespace
            item = " ".join(item.split())
            if item:
                processed_items.append(item)
        return processed_items

    def preprocess_ingredients(self, text: str) -> str:
        """String representation of ingredients for TF-IDF."""
        items = self.extract_ingredient_list(text)
        return " ".join(items)

    def load_data(self) -> None:
        """Load pre-trained models from disk, or fallback to training on the fly."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        models_dir = os.path.join(base_dir, "models")
        
        vectorizer_path = os.path.join(models_dir, "vectorizer.pkl")
        matrix_path = os.path.join(models_dir, "tfidf_matrix.pkl")
        df_path = os.path.join(models_dir, "df_recipes.pkl")
        
        if os.path.exists(vectorizer_path) and os.path.exists(matrix_path) and os.path.exists(df_path):
            import joblib
            print("INFO: Loading pre-trained TF-IDF model from /models directory...")
            self.vectorizer = joblib.load(vectorizer_path)
            self.tfidf_matrix = joblib.load(matrix_path)
            self.df = pd.read_pickle(df_path)
        else:
            print("INFO: Models not found in /models. Training on the fly...")
            self._train_on_the_fly()

    def _train_on_the_fly(self) -> None:
        """Original on-the-fly training logic as fallback."""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Dataset not found at {self.data_path}")
            
        self.df = pd.read_csv(self.data_path)
        
        # Fill NA values
        self.df['Ingredients Cleaned'] = self.df['Ingredients Cleaned'].fillna("")
        self.df['Ingredients'] = self.df['Ingredients'].fillna("")
        self.df['Steps'] = self.df['Steps'].fillna("")
        self.df['Category'] = self.df['Category'].fillna("")
        self.df['URL'] = self.df['URL'].fillna("")
        self.df['Loves'] = self.df['Loves'].fillna(0).astype(int)
        
        # Preprocess ingredients for TF-IDF
        self.df['Processed_Ingredients'] = self.df['Ingredients Cleaned'].apply(self.preprocess_ingredients)
        
        # Fit TF-IDF
        self.tfidf_matrix = self.vectorizer.fit_transform(self.df['Processed_Ingredients'])

    def get_recommendations(self, user_ingredients: str, top_n: int = 5, category: str = None, sort_by: str = "relevance") -> List[Dict[str, Any]]:
        """Get top recipe recommendations based on user ingredients."""
        if self.df is None or self.tfidf_matrix is None:
            raise RuntimeError("Data not loaded properly.")
            
        # Extract list for matching later
        user_ingred_list = set(self.extract_ingredient_list(user_ingredients))
        
        # Preprocess string for TF-IDF prediction
        processed_user_input = self.preprocess_ingredients(user_ingredients)
        
        if not processed_user_input:
            return []

        # Convert user ingredients into TF-IDF vector
        user_vector = self.vectorizer.transform([processed_user_input])
        
        # Compute cosine similarity against all recipes
        similarities = cosine_similarity(user_vector, self.tfidf_matrix).flatten()
        
        # Add similarity score to a copy of dataframe
        results_df = self.df.copy()
        results_df['similarity_score'] = similarities
        
        # Filter recipes with > 0 similarity
        results_df = results_df[results_df['similarity_score'] > 0]
        
        if results_df.empty:
            return []
            
        # Optional: Filter by Category
        if category and category != "Semua Kategori":
            results_df = results_df[results_df['Category'].str.contains(category, case=False, na=False)]
            if results_df.empty:
                return []
                
        # Sort logic based on user preference
        if sort_by == "practicality" and 'Total Steps' in results_df.columns:
            results_df = results_df.sort_values(by=['similarity_score', 'Total Steps'], ascending=[False, True])
        else:
            results_df = results_df.sort_values(by=['similarity_score', 'Loves'], ascending=[False, False])
        
        # Remove duplicate recipe titles (Aligning with Project Plan: use Title Cleaned)
        dup_col = 'Title Cleaned' if 'Title Cleaned' in results_df.columns else 'Title'
        results_df = results_df.drop_duplicates(subset=[dup_col], keep='first')
        
        # Return Top recommendations
        top_recommendations = results_df.head(top_n)
        
        results = []
        for _, row in top_recommendations.iterrows():
            recipe_ingred_list = self.extract_ingredient_list(row['Ingredients Cleaned'])
            
            # Calculate Matched & Missing Ingredients using word subset matching
            matched = []
            missing = []
            for r_item in recipe_ingred_list:
                r_words = set(r_item.split())
                is_match = False
                for u_item in user_ingred_list:
                    u_words = set(u_item.split())
                    if u_words and u_words.issubset(r_words):
                        is_match = True
                        break
                
                if is_match:
                    matched.append(r_item)
                else:
                    missing.append(r_item)
            
            results.append({
                "title": str(row['Title']),
                "category": str(row['Category']),
                "similarity_score": round(float(row['similarity_score']), 4),
                "matched_ingredients": matched,
                "missing_ingredients": missing,
                "ingredients": str(row['Ingredients']),
                "steps": str(row['Steps']),
                "url": str(row['URL']),
                "loves": int(row['Loves'])
            })
            
        return results

# Determine the absolute path to the data file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "Indonesian_Food_Recipes.csv")

# Initialize singleton engine
recommender_engine = RecommendationEngine(DATA_PATH)
