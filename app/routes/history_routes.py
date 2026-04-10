"""
Review Analysis History API Routes
Handles review analysis history CRUD operations.
"""
from flask import Blueprint, request, jsonify
from utils.database import (
    get_analysis_history,
    get_analysis_by_id,
    delete_analysis_record,
    clear_analysis_history
)

history_bp = Blueprint("history", __name__)


@history_bp.route("", methods=["GET"])
def list_history():
    """
    GET /api/history?page=1&per_page=20

    Retrieve paginated analysis history.

    Query Parameters:
        page (int, optional): Page number (default: 1)
        per_page (int, optional): Results per page (default: 20, max: 100)

    Response (JSON):
        {
            "total": 150,
            "page": 1,
            "per_page": 20,
            "total_pages": 8,
            "results": [
                {
                    "id": 1,
                    "review_text": "...",
                    "classification": "Likely Genuine",
                    "credibility_score": 85.3,
                    "fake_probability": 0.147,
                    "flags": "[...]",
                    "analyzed_at": "2024-01-01 12:00:00"
                },
                ...
            ]
        }
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    # Validate pagination params
    page = max(1, page)
    per_page = min(max(1, per_page), 100)

    history = get_analysis_history(page=page, per_page=per_page)
    return jsonify(history), 200


@history_bp.route("/<int:record_id>", methods=["GET"])
def get_record(record_id):
    """
    GET /api/history/<id>

    Retrieve a single analysis record by ID.

    Response (JSON):
        {
            "id": 1,
            "review_text": "...",
            "classification": "Likely Genuine",
            "credibility_score": 85.3,
            ...
        }
    """
    record = get_analysis_by_id(record_id)
    if record is None:
        return jsonify({"error": "Record not found."}), 404
    return jsonify(record), 200


@history_bp.route("/<int:record_id>", methods=["DELETE"])
def delete_record(record_id):
    """
    DELETE /api/history/<id>

    Delete a single analysis record.

    Response (JSON):
        {"success": true, "message": "Record deleted successfully."}
    """
    success = delete_analysis_record(record_id)
    if not success:
        return jsonify({"error": "Record not found."}), 404
    return jsonify({"success": True, "message": "Record deleted successfully."}), 200


@history_bp.route("/clear", methods=["DELETE"])
def clear_history():
    """
    DELETE /api/history/clear

    Clear all analysis history records.

    Response (JSON):
        {"success": true, "message": "All history records cleared."}
    """
    clear_analysis_history()
    return jsonify({"success": True, "message": "All history records cleared."}), 200
