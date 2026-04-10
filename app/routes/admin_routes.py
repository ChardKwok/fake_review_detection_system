"""
Admin API Routes
Handles admin interface for managing detection rules and dashboard.
"""
from flask import Blueprint, request, jsonify
from utils.database import (
    get_detection_rules,
    update_detection_rule,
    add_detection_rule,
    delete_detection_rule,
    get_dashboard_stats
)
from utils.ml_model import get_model, reload_model

admin_bp = Blueprint("admin", __name__)


# ============================================================
# Dashboard
# ============================================================

@admin_bp.route("/dashboard", methods=["GET"])
def dashboard():
    """
    GET /api/admin/dashboard

    Retrieve dashboard statistics and recent analysis results.

    Response (JSON):
        {
            "total_analyzed": 150,
            "total_genuine": 100,
            "total_fake": 50,
            "avg_credibility_score": 72.5,
            "recent_analyses": [...],
            "classification_distribution": {
                "Likely Genuine": 100,
                "Possibly Fake": 50
            }
        }
    """
    stats = get_dashboard_stats()
    return jsonify(stats), 200


# ============================================================
# Detection Rules Management
# ============================================================

@admin_bp.route("/rules", methods=["GET"])
def list_rules():
    """
    GET /api/admin/rules

    Retrieve all detection rules.

    Response (JSON):
        {
            "rules": [
                {
                    "id": 1,
                    "rule_name": "promotional_keywords",
                    "rule_type": "keyword_list",
                    "rule_value": "amazing,perfect,...",
                    "weight": 1.0,
                    "is_active": 1,
                    "description": "...",
                    "created_at": "...",
                    "updated_at": "..."
                },
                ...
            ]
        }
    """
    rules = get_detection_rules()
    return jsonify({"rules": rules}), 200


@admin_bp.route("/rules", methods=["POST"])
def create_rule():
    """
    POST /api/admin/rules

    Create a new detection rule.

    Request Body (JSON):
        {
            "rule_name": "string (required)",
            "rule_type": "keyword_list" | "threshold" (required),
            "rule_value": "string (required)",
            "weight": 1.0 (optional),
            "description": "string (optional)"
        }

    Response (JSON):
        {"success": true, "rule_id": 8}
    """
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    rule_name = data.get("rule_name", "").strip()
    rule_type = data.get("rule_type", "").strip()
    rule_value = data.get("rule_value", "").strip()
    weight = data.get("weight", 1.0)
    description = data.get("description", "")

    if not rule_name or not rule_type or not rule_value:
        return jsonify({"error": "rule_name, rule_type, and rule_value are required."}), 400

    if rule_type not in ("keyword_list", "threshold"):
        return jsonify({"error": "rule_type must be 'keyword_list' or 'threshold'."}), 400

    rule_id = add_detection_rule(rule_name, rule_type, rule_value, weight, description)
    if rule_id is None:
        return jsonify({"error": f"Rule with name '{rule_name}' already exists."}), 409

    return jsonify({"success": True, "rule_id": rule_id}), 201


@admin_bp.route("/rules/<int:rule_id>", methods=["PUT"])
def update_rule(rule_id):
    """
    PUT /api/admin/rules/<id>

    Update an existing detection rule.

    Request Body (JSON):
        {
            "rule_value": "string (optional)",
            "weight": 1.0 (optional),
            "is_active": 1 | 0 (optional),
            "description": "string (optional)"
        }

    Response (JSON):
        {"success": true, "message": "Rule updated successfully."}
    """
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    success = update_detection_rule(rule_id, data)
    if not success:
        return jsonify({"error": "Rule not found or no valid fields to update."}), 404

    return jsonify({"success": True, "message": "Rule updated successfully."}), 200


@admin_bp.route("/rules/<int:rule_id>", methods=["DELETE"])
def remove_rule(rule_id):
    """
    DELETE /api/admin/rules/<id>

    Delete a detection rule.

    Response (JSON):
        {"success": true, "message": "Rule deleted successfully."}
    """
    success = delete_detection_rule(rule_id)
    if not success:
        return jsonify({"error": "Rule not found."}), 404
    return jsonify({"success": True, "message": "Rule deleted successfully."}), 200


# ============================================================
# Model Management
# ============================================================

@admin_bp.route("/model/status", methods=["GET"])
def model_status():
    """
    GET /api/admin/model/status

    Get ML model status.
    """
    model = get_model()
    return jsonify(model.get_status()), 200


@admin_bp.route("/model/train", methods=["POST"])
def train_model():
    """
    POST /api/admin/model/train

    Retrain the ML model with a dataset.

    Request Body (JSON):
        {
            "dataset_path": "data/fake_reviews_dataset.csv" (optional, uses default if not provided)
        }

    Response (JSON):
        {
            "success": true,
            "accuracy": 0.87,
            "total_samples": 40000,
            ...
        }
    """
    import os
    from config import Config

    data = request.get_json(silent=True) or {}
    dataset_path = data.get("dataset_path", "")

    if not dataset_path:
        # Try to find dataset in data/ directory
        data_dir = os.path.join(os.path.dirname(Config.DATABASE_PATH))
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')] if os.path.exists(data_dir) else []
        if csv_files:
            dataset_path = os.path.join(data_dir, csv_files[0])
        else:
            return jsonify({
                "error": "No dataset found. Please place a CSV file in the data/ directory or provide a dataset_path."
            }), 400

    if not os.path.exists(dataset_path):
        return jsonify({"error": f"Dataset file not found: {dataset_path}"}), 404

    try:
        model = get_model()
        result = model.train(dataset_path)
        return jsonify({"success": True, **result}), 200
    except Exception as e:
        return jsonify({"error": f"Training failed: {str(e)}"}), 500


@admin_bp.route("/model/reload", methods=["POST"])
def reload_model_endpoint():
    """
    POST /api/admin/model/reload

    Reload the ML model from disk.
    """
    model = reload_model()
    return jsonify({
        "success": True,
        "message": "Model reloaded.",
        "is_loaded": model.is_loaded
    }), 200
