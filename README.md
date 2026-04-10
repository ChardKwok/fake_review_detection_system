# Fake Product Review Detection System - Backend

## Project Overview

A web-based Fake Product Review Detection System that analyzes product reviews using **TF-IDF + Naive Bayes** machine learning model combined with **rule-based pattern detection** to determine whether a review is genuine or potentially fake.

### Tech Stack
- **Language**: Python 3.9+
- **Web Framework**: Flask 3.1
- **ML**: scikit-learn (TF-IDF + Multinomial Naive Bayes)
- **NLP**: NLTK (tokenization, stopwords, lemmatization)
- **Database**: SQLite (zero configuration, no MySQL needed)
- **CORS**: Flask-CORS (frontend-backend separation)

## Quick Start (Windows)

### Prerequisites
- Python 3.9 or higher installed
- pip (Python package manager)

### Step 1: Setup Environment

```bash
# Clone or copy the project
cd fake_review_backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Download Dataset

Download a fake reviews dataset CSV and place it in the `data/` folder:

**Recommended**: [Fake Reviews Dataset (40K reviews)](https://www.kaggle.com/datasets/mexwell/fake-reviews-dataset)
- Download `fake reviews dataset.csv`
- Place it in: `fake_review_backend/data/fake reviews dataset.csv`

Other compatible datasets:
- [Amazon Labeled Fake Reviews](https://www.kaggle.com/datasets/malikawaispy/amazon-labeled-fake-reviews)
- [Fake Reviews Detection Dataset](https://www.kaggle.com/datasets/syntheticprogrammer/fake-reviews-detection-dataset)

### Step 3: Train the Model

```bash
python train_model.py
```

This will:
- Load the CSV dataset from `data/` folder
- Preprocess text (lowercase, remove punctuation, remove stopwords, lemmatize)
- Train TF-IDF vectorizer + Multinomial Naive Bayes classifier
- Save trained model to `models/` folder
- Print accuracy metrics (~87-90% expected)

### Step 4: Start the Server

```bash
python run.py
```

Server starts at: **http://localhost:5000**

## API Endpoints

### Health Check
```
GET /api/health
```

### Review Analysis (Core Feature)
```
POST /api/reviews/analyze
Content-Type: application/json

{
    "review_text": "This product is amazing and works perfectly!"
}

Response:
{
    "success": true,
    "id": 1,
    "classification": "Likely Genuine" | "Possibly Fake" | "Uncertain",
    "credibility_score": 85.3,        // 0-100 scale
    "fake_probability": 0.147,         // 0.0-1.0
    "flags": [                         // Explanation reasons
        {
            "type": "promotional_language",
            "severity": "medium",
            "message": "Contains 2 overly promotional word(s): amazing, perfectly",
            "detail": "Fake reviews often use exaggerated positive language..."
        }
    ],
    "ml_prediction": {
        "fake_probability": 0.12,
        "genuine_probability": 0.88,
        "prediction": 0,
        "prediction_label": "Genuine"
    },
    "rule_analysis": {
        "suspicion_score": 0.15,
        "total_flags": 1
    },
    "model_available": true
}
```

### Batch Analysis
```
POST /api/reviews/batch-analyze
Content-Type: application/json

{
    "reviews": [
        "Great product, works well.",
        "AMAZING BEST EVER MUST BUY!!!!"
    ]
}
```

### Analysis History
```
GET  /api/history?page=1&per_page=20     # List history (paginated)
GET  /api/history/<id>                     # Get single record
DELETE /api/history/<id>                   # Delete a record
DELETE /api/history/clear                  # Clear all history
```

### Admin - Dashboard
```
GET /api/admin/dashboard

Response:
{
    "total_analyzed": 150,
    "total_genuine": 100,
    "total_fake": 50,
    "avg_credibility_score": 72.5,
    "recent_analyses": [...],
    "classification_distribution": {"Likely Genuine": 100, "Possibly Fake": 50}
}
```

### Admin - Detection Rules
```
GET    /api/admin/rules                    # List all rules
POST   /api/admin/rules                    # Create new rule
PUT    /api/admin/rules/<id>               # Update a rule
DELETE /api/admin/rules/<id>               # Delete a rule
```

### Admin - Model Management
```
GET  /api/admin/model/status               # Model status
POST /api/admin/model/train                # Retrain model
POST /api/admin/model/reload               # Reload model from disk
```

## Project Structure

```
fake_review_backend/
├── app/
│   ├── __init__.py              # Flask app factory
│   └── routes/
│       ├── __init__.py
│       ├── review_routes.py     # Review analysis API (Epic 1,2,3,4)
│       ├── history_routes.py    # Analysis history API
│       └── admin_routes.py      # Admin dashboard & rules API
├── utils/
│   ├── __init__.py
│   ├── database.py              # SQLite database operations
│   ├── ml_model.py              # TF-IDF + Naive Bayes model
│   ├── text_analyzer.py         # Rule-based pattern detection
│   └── review_service.py        # Core analysis service (combines ML + rules)
├── models/                      # Trained model files (auto-generated)
│   ├── fake_review_model.pkl
│   └── tfidf_vectorizer.pkl
├── data/                        # Dataset and SQLite database
│   ├── *.csv                    # Place dataset here
│   └── reviews.db               # SQLite database (auto-created)
├── tests/
│   └── test_api.py              # API test script
├── config.py                    # App configuration
├── run.py                       # Entry point - start server
├── train_model.py               # Model training script
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## How It Works

### Analysis Pipeline

1. **Input Validation** (Epic 5): Check for empty/too-short input
2. **ML Prediction** (70% weight): TF-IDF vectorization -> Naive Bayes classification
3. **Rule-based Analysis** (30% weight): Check for suspicious patterns
4. **Score Combination**: Weighted average of ML + rules = final fake probability
5. **Classification**: Based on thresholds:
   - `fake_prob >= 0.6` -> "Possibly Fake"
   - `fake_prob <= 0.4` -> "Likely Genuine"
   - Otherwise -> "Uncertain"
6. **Credibility Score**: `(1 - fake_probability) * 100`

### Suspicious Pattern Checks

| Check | Description |
|-------|-------------|
| Promotional Keywords | Detects "amazing", "best ever", "must buy", etc. |
| Negative Spam | Detects "worst", "terrible", "scam", etc. |
| Review Length | Flags very short reviews |
| Excessive Punctuation | Detects overuse of !!! and ??? |
| Excessive Caps | Detects ALL CAPS writing |
| Word Repetition | Detects repeated words/phrases |
| Generic Language | Detects vague, non-specific praise |

### User Story Mapping

| Epic | Story | Implementation |
|------|-------|----------------|
| Epic 1 | Submit review text | `POST /api/reviews/analyze` |
| Epic 2 | Detect suspicious patterns | `utils/text_analyzer.py` + `utils/ml_model.py` |
| Epic 3 | Show classification | Response: classification + credibility_score |
| Epic 4 | Explain the result | Response: flags array with reasons |
| Epic 5 | Input validation | `utils/review_service.py` -> `_validate_input()` |

## Testing

```bash
# Start the server first
python run.py

# In another terminal, run tests
python tests/test_api.py
```

## Development Notes

- **No MySQL required**: Uses SQLite which comes built-in with Python
- **No Docker required**: Runs directly on Windows with Python
- **CORS enabled**: Frontend can run on any port/domain
- **Model hot-reload**: Retrain and reload model without restarting server
- **Admin rules**: Detection rules are database-driven and can be modified at runtime
