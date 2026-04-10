"""
Fake Product Review Detection System - Entry Point
Run this file to start the Flask backend server.

Usage:
    python run.py

The server will start on http://localhost:5000
"""
from app import create_app
from utils.database import init_database
from config import Config


def main():
    """Initialize database and start the Flask application."""
    print("=" * 60)
    print("  Fake Product Review Detection System - Backend")
    print("=" * 60)

    # Initialize SQLite database
    print("\n[1/3] Initializing database...")
    init_database()
    print(f"  Database ready at: {Config.DATABASE_PATH}")

    # Check ML model status
    print("\n[2/3] Checking ML model...")
    from utils.ml_model import get_model
    model = get_model()
    if model.is_loaded:
        print("  ML model loaded successfully.")
    else:
        print("  WARNING: No trained ML model found.")
        print("  Run 'python train_model.py' to train the model first.")
        print("  The system will still work with rule-based analysis only.")

    # Start Flask server
    print(f"\n[3/3] Starting Flask server...")
    print(f"  Host: {Config.HOST}")
    print(f"  Port: {Config.PORT}")
    print(f"  Debug: {Config.DEBUG}")
    print(f"\n  API Base URL: http://localhost:{Config.PORT}/api")
    print(f"  Health Check: http://localhost:{Config.PORT}/api/health")
    print(f"  Analyze:      POST http://localhost:{Config.PORT}/api/reviews/analyze")
    print(f"  History:      GET  http://localhost:{Config.PORT}/api/history")
    print(f"  Dashboard:    GET  http://localhost:{Config.PORT}/api/admin/dashboard")
    print(f"  Rules:        GET  http://localhost:{Config.PORT}/api/admin/rules")
    print("=" * 60)

    app = create_app()
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)


if __name__ == "__main__":
    main()
