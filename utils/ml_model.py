"""
Machine Learning Model Module
TF-IDF + Naive Bayes classifier for fake review detection.
Handles model training, saving, loading, and prediction.
"""
import os
import re
import string
import joblib
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd
import numpy as np
from config import Config


# Download required NLTK data
def download_nltk_data():
    """Download required NLTK resources."""
    resources = ['stopwords', 'wordnet', 'punkt', 'punkt_tab']
    for resource in resources:
        try:
            nltk.download(resource, quiet=True)
        except Exception as e:
            print(f"Warning: Could not download NLTK resource '{resource}': {e}")


# Initialize NLTK data
download_nltk_data()


class FakeReviewModel:
    """
    TF-IDF + Naive Bayes model for fake review classification.
    """

    def __init__(self):
        self.vectorizer = None
        self.model = None
        self.is_loaded = False
        self.accuracy = None
        self.lemmatizer = WordNetLemmatizer()

        # Try to load existing model
        self._load_model()

    def _preprocess_text(self, text):
        """
        Preprocess review text for ML analysis.
        Steps: lowercase -> remove punctuation -> tokenize -> remove stopwords -> lemmatize
        """
        # Lowercase
        text = text.lower()
        # Remove punctuation
        text = text.translate(str.maketrans("", "", string.punctuation))
        # Remove numbers
        text = re.sub(r'\d+', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        # Tokenize
        words = text.split()
        # Remove stopwords and lemmatize
        try:
            stop_words = set(stopwords.words('english'))
        except LookupError:
            download_nltk_data()
            stop_words = set(stopwords.words('english'))

        words = [self.lemmatizer.lemmatize(w) for w in words if w not in stop_words and len(w) > 2]
        return ' '.join(words)

    def train(self, csv_path):
        """
        Train the model using a CSV dataset.

        Expected CSV format:
        - Column 'text_' or 'text': the review text
        - Column 'label': 'CG' (Computer Generated/Fake) or 'OR' (Original/Genuine)
          OR 0 (Genuine) / 1 (Fake)

        Args:
            csv_path (str): Path to the CSV dataset file.

        Returns:
            dict: Training results including accuracy and classification report.
        """
        print(f"Loading dataset from: {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"Dataset loaded: {len(df)} rows")

        # Detect column names (support multiple CSV formats)
        text_col = None
        label_col = None

        for col in ['text_', 'text', 'review', 'review_text', 'content']:
            if col in df.columns:
                text_col = col
                break

        for col in ['label', 'Label', 'fake', 'is_fake', 'class']:
            if col in df.columns:
                label_col = col
                break

        if text_col is None or label_col is None:
            raise ValueError(f"Cannot find text or label columns. Available columns: {list(df.columns)}")

        print(f"Using columns: text='{text_col}', label='{label_col}'")

        # Drop null values
        df = df.dropna(subset=[text_col, label_col])
        print(f"After dropping nulls: {len(df)} rows")

        # Standardize labels to binary (0 = Genuine, 1 = Fake)
        unique_labels = df[label_col].unique()
        print(f"Unique labels: {unique_labels}")

        if set(unique_labels) <= {0, 1}:
            # Already binary
            df['target'] = df[label_col].astype(int)
        elif set(unique_labels) <= {'CG', 'OR'}:
            # CG = Computer Generated (Fake), OR = Original (Genuine)
            df['target'] = df[label_col].map({'CG': 1, 'OR': 0})
        elif set(unique_labels) <= {'fake', 'genuine', 'Fake', 'Genuine', 'FAKE', 'GENUINE'}:
            df['target'] = df[label_col].str.lower().map({'fake': 1, 'genuine': 0})
        else:
            raise ValueError(f"Unknown label format: {unique_labels}. Expected 'CG'/'OR', 0/1, or 'fake'/'genuine'.")

        df = df.dropna(subset=['target'])
        print(f"Label distribution:\n{df['target'].value_counts()}")

        # Preprocess text
        print("Preprocessing text...")
        df['processed'] = df[text_col].astype(str).apply(self._preprocess_text)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            df['processed'], df['target'],
            test_size=0.2,
            random_state=42,
            stratify=df['target']
        )
        print(f"Training set: {len(X_train)}, Test set: {len(X_test)}")

        # TF-IDF Vectorization
        print("Training TF-IDF vectorizer...")
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2),    # Unigrams and bigrams
            min_df=2,              # Minimum document frequency
            max_df=0.95,           # Maximum document frequency
            sublinear_tf=True      # Apply sublinear tf scaling
        )
        X_train_tfidf = self.vectorizer.fit_transform(X_train)
        X_test_tfidf = self.vectorizer.transform(X_test)

        # Train Naive Bayes
        print("Training Multinomial Naive Bayes classifier...")
        self.model = MultinomialNB(alpha=0.1)  # Laplace smoothing
        self.model.fit(X_train_tfidf, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test_tfidf)
        self.accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, target_names=["Genuine", "Fake"], output_dict=True)

        print(f"\nModel Accuracy: {self.accuracy:.4f}")
        print(classification_report(y_test, y_pred, target_names=["Genuine", "Fake"]))

        # Save model
        self._save_model()
        self.is_loaded = True

        return {
            "accuracy": round(self.accuracy, 4),
            "total_samples": len(df),
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "classification_report": report
        }

    def predict(self, text):
        """
        Predict whether a review is fake or genuine.

        Args:
            text (str): The review text to analyze.

        Returns:
            dict: {
                "fake_probability": float (0.0 to 1.0),
                "genuine_probability": float (0.0 to 1.0),
                "prediction": int (0 = Genuine, 1 = Fake),
                "prediction_label": str
            }
        """
        if not self.is_loaded:
            return None

        # Preprocess
        processed = self._preprocess_text(text)

        # Vectorize
        text_tfidf = self.vectorizer.transform([processed])

        # Predict probabilities
        probabilities = self.model.predict_proba(text_tfidf)[0]
        prediction = self.model.predict(text_tfidf)[0]

        # Index 0 = Genuine, Index 1 = Fake
        genuine_prob = probabilities[0]
        fake_prob = probabilities[1]

        return {
            "fake_probability": round(float(fake_prob), 4),
            "genuine_probability": round(float(genuine_prob), 4),
            "prediction": int(prediction),
            "prediction_label": "Fake" if prediction == 1 else "Genuine"
        }

    def _save_model(self):
        """Save trained model and vectorizer to disk."""
        os.makedirs(os.path.dirname(Config.MODEL_PATH), exist_ok=True)
        os.makedirs(os.path.dirname(Config.VECTORIZER_PATH), exist_ok=True)
        joblib.dump(self.model, Config.MODEL_PATH)
        joblib.dump(self.vectorizer, Config.VECTORIZER_PATH)
        print(f"Model saved to: {Config.MODEL_PATH}")
        print(f"Vectorizer saved to: {Config.VECTORIZER_PATH}")

    def _load_model(self):
        """Load trained model and vectorizer from disk."""
        if os.path.exists(Config.MODEL_PATH) and os.path.exists(Config.VECTORIZER_PATH):
            try:
                self.model = joblib.load(Config.MODEL_PATH)
                self.vectorizer = joblib.load(Config.VECTORIZER_PATH)
                self.is_loaded = True
                print("ML model loaded successfully.")
            except Exception as e:
                print(f"Error loading model: {e}")
                self.is_loaded = False
        else:
            print("No trained model found. Please train the model first.")
            self.is_loaded = False

    def get_status(self):
        """Get model status information."""
        return {
            "is_loaded": self.is_loaded,
            "model_path": Config.MODEL_PATH,
            "vectorizer_path": Config.VECTORIZER_PATH,
            "model_exists": os.path.exists(Config.MODEL_PATH),
            "vectorizer_exists": os.path.exists(Config.VECTORIZER_PATH),
            "accuracy": self.accuracy
        }


# Singleton instance
_model_instance = None


def get_model():
    """Get or create the singleton model instance."""
    global _model_instance
    if _model_instance is None:
        _model_instance = FakeReviewModel()
    return _model_instance


def reload_model():
    """Force reload the model (after retraining)."""
    global _model_instance
    _model_instance = FakeReviewModel()
    return _model_instance
