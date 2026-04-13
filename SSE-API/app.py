import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

from routes.auth_routes import auth_bp
from routes.application_routes import applications_bp
from routes.artist_routes import artists_bp
from routes.release_routes import releases_bp
from routes.request_routes import requests_bp
from routes.news_routes import news_bp
from routes.admin_routes import admin_bp
from routes.dev_routes import dev_bp
from routes.mail_routes import  test_bp

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    app.config["SESSION_COOKIE_SECURE"] = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTENT_LENGTH", 1024 * 1024 * 500))  # 500 MB

    frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://127.0.0.1:5500")

    CORS(
        app,
        supports_credentials=True,
        resources={
            r"/api/*": {
                "origins": [frontend_origin]
            }
        },
    )

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(applications_bp, url_prefix="/api/applications")
    app.register_blueprint(artists_bp, url_prefix="/api/artists")
    app.register_blueprint(releases_bp, url_prefix="/api/releases")
    app.register_blueprint(requests_bp, url_prefix="/api/requests")
    app.register_blueprint(news_bp, url_prefix="/api/news")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(dev_bp, url_prefix="/api/dev")
    app.register_blueprint(test_bp, url_prefix="/api")

    @app.get("/")
    def root():
        return jsonify({
            "status": "ok",
            "service": "sse-api"
        }), 200

    @app.get("/health")
    def health():
        return jsonify({
            "status": "healthy"
        }), 200

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Route not found."}), 404

    @app.errorhandler(413)
    def payload_too_large(_error):
        return jsonify({"error": "Uploaded file is too large."}), 413

    @app.errorhandler(500)
    def internal_error(_error):
        return jsonify({"error": "Internal server error."}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)