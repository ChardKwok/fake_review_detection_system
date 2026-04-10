"""
Review Analysis API Routes
Handles Epic 1 (Review Submission), Epic 2 (Review Analysis),
Epic 3 (Credibility Result), and Epic 4 (Explain the Result).
"""
from flask import Blueprint, request, jsonify
from utils.review_service import ReviewService

review_bp = Blueprint("reviews", __name__)
review_service = ReviewService()


@review_bp.route("/analyze", methods=["POST"])
def analyze_review():
    """
    POST /api/reviews/analyze

    Analyze a product review for fake/genuine classification.

    Request Body (JSON):
        {
            "review_text": "string (required) - The review text to analyze"
        }

    Response (JSON):
        Success (200):
        {
            "success": true,
            "id": 1,
            "classification": "Likely Genuine" | "Possibly Fake" | "Uncertain",
            "credibility_score": 85.3,
            "fake_probability": 0.147,
            "flags": [...],
            "ml_prediction": {...},
            "rule_analysis": {...},
            "review_text": "...",
            "review_length": 150,
            "model_available": true
        }

        Validation Error (400):
        {
            "success": false,
            "error": "Error message",
            "error_type": "empty_input" | "too_short" | "missing_input"
        }
    """
    # Parse request
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({
            "success": False,
            "error": "Request body must be valid JSON with Content-Type: application/json",
            "error_type": "invalid_json"
        }), 400

    review_text = data.get("review_text", "")

    # Perform analysis
    result = review_service.analyze_review(review_text)

    if not result.get("success"):
        return jsonify(result), 400

    return jsonify(result), 200


@review_bp.route("/batch-analyze", methods=["POST"])
def batch_analyze():
    """
    POST /api/reviews/batch-analyze

    Analyze multiple reviews at once.

    Request Body (JSON):
        {
            "reviews": ["review text 1", "review text 2", ...]
        }

    Response (JSON):
        {
            "success": true,
            "total": 3,
            "results": [...]
        }
    """
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({
            "success": False,
            "error": "Request body must be valid JSON."
        }), 400

    reviews = data.get("reviews", [])
    if not isinstance(reviews, list) or len(reviews) == 0:
        return jsonify({
            "success": False,
            "error": "Please provide a non-empty list of reviews."
        }), 400

    if len(reviews) > 50:
        return jsonify({
            "success": False,
            "error": "Maximum 50 reviews per batch."
        }), 400

    results = []
    for review_text in reviews:
        result = review_service.analyze_review(review_text)
        results.append(result)

    return jsonify({
        "success": True,
        "total": len(results),
        "results": results
    }), 200


@review_bp.route("/model-status", methods=["GET"])
def model_status():
    """
    GET /api/reviews/model-status

    Check the status of the ML model.

    Response (JSON):
        {
            "is_loaded": true,
            "model_path": "...",
            "accuracy": 0.87
        }
    """
    from utils.ml_model import get_model
    model = get_model()
    return jsonify(model.get_status()), 200
