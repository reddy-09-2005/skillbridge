"""
app.py
SkillBridge AI - Flask application entry point.
Supports both decoupled API mode and unified frontend+backend serving.
Run with: python app.py or gunicorn "app:create_app()"
"""

import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from api import api_bp
from auth import auth_bp
from db import init_db


def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # Initialize JWT
    JWTManager(app)

    # Configure CORS
    cors_origins = Config.CORS_ORIGINS
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": cors_origins
            }
        },
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        supports_credentials=True if cors_origins != "*" else False
    )

    # Register API blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # Health check endpoint for cloud platforms (Render, Railway, Kubernetes, Docker)
    @app.route("/health", methods=["GET"])
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "healthy", "service": "SkillBridge AI API"}), 200

    # Serve static frontend files when frontend directory is present
    if Config.SERVE_FRONTEND and os.path.isdir(Config.FRONTEND_DIR):
        frontend_path = Config.FRONTEND_DIR

        @app.route("/", defaults={"filename": "index.html"})
        @app.route("/<path:filename>")
        def serve_frontend(filename):

            # Never let this catch-all swallow API requests.
            # If we get here for something under /api/, it means
            # no real API route matched — return a proper 404
            # instead of silently serving index.html.
            if filename.startswith("api/"):
                return jsonify({"error": f"API route /{filename} not found"}), 404

            file_target = os.path.join(frontend_path, filename)
            if os.path.isfile(file_target):
                return send_from_directory(frontend_path, filename)
            # Default to index.html if file doesn't exist
            return send_from_directory(frontend_path, "index.html")

    # Initialize database tables
    with app.app_context():
        try:
            init_db()
        except Exception as e:
            app.logger.warning(f"Database table auto-init skipped or deferred: {e}")

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=os.getenv("FLASK_DEBUG", "false").lower() in ("true", "1")
    )