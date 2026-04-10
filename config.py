"""
Application Configuration
Loads settings from .env file or uses defaults.
"""
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DATABASE_PATH = os.path.join(BASE_DIR, os.getenv("DATABASE_PATH", "data/reviews.db"))
    MODEL_PATH = os.path.join(BASE_DIR, os.getenv("MODEL_PATH", "models/fake_review_model.pkl"))
    VECTORIZER_PATH = os.path.join(BASE_DIR, os.getenv("VECTORIZER_PATH", "models/tfidf_vectorizer.pkl"))
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"

    # Analysis thresholds
    MIN_REVIEW_LENGTH = 10          # Minimum characters for a valid review
    SHORT_REVIEW_THRESHOLD = 50     # Reviews shorter than this get a warning
    FAKE_THRESHOLD = 0.6            # Probability threshold for "Possibly Fake"
    GENUINE_THRESHOLD = 0.4         # Below this is "Likely Genuine"
