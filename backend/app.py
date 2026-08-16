""""
app.py
SkillBridge AI - Flask application entry point.
Run with: python app.py
"""

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from api import api_bp
from auth import auth_bp


def create_app():

    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # JWT
    JWTManager(app)

    # CORS
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    "http://10.109.94.10:5500",
                    "http://127.0.0.1:5500",
                    "http://localhost:5500"
                ]
            }
        },
        methods=[
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "OPTIONS"
        ],
        allow_headers=[
            "Content-Type",
            "Authorization"
        ],
        supports_credentials=True
    )

    # Register API routes
    app.register_blueprint(api_bp)

    # Register authentication routes
    app.register_blueprint(
        auth_bp,
        url_prefix="/api/auth"
    )

    return app


app = create_app()

print(app.url_map)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )