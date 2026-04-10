"""
Fake Product Review Detection System - Flask Application Factory
"""
from flask import Flask
from flask_cors import CORS
from config import Config


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS for frontend-backend separation
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Register blueprints
    from app.routes.review_routes import review_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.history_routes import history_bp

    app.register_blueprint(review_bp, url_prefix="/api/reviews")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(history_bp, url_prefix="/api/history")

    # Health check endpoint
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return {"status": "ok", "message": "Fake Review Detection API is running"}, 200

    return app
