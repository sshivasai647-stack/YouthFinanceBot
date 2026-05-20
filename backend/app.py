# Purpose: Flask application factory and baseline app wiring for YouthFinanceBot.
# Existing module dependencies: backend.middleware.audit_logger, backend.routes.citizen (domain APIs).

"""Application factory for YouthFinanceBot backend."""

from __future__ import annotations

# ADD this import at the top of the file with the other imports
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))  # expose project root modules
from backend.comprehensive_routes import comprehensive_bp          # import the new blueprint

from flask import Flask, jsonify
from flask_cors import CORS

from backend.config import DevelopmentConfig, ProductionConfig
from backend.extensions import close_mongo, init_extensions
from backend.middleware.audit_logger import register_audit_logger
from backend.routes.admin import admin_bp
from backend.routes.auth import auth_bp
from backend.routes.citizen import citizen_bp
from backend.routes.counsellor import counsellor_bp
from backend.routes.guest import guest_bp


def create_app() -> Flask:
    """Create and configure the Flask app instance."""

    app = Flask(__name__)
    config_name = os.getenv("FLASK_ENV", "development").lower()
    app.config.from_object(ProductionConfig if config_name == "production" else DevelopmentConfig)
    app.secret_key = app.config["SECRET_KEY"]

    CORS(
        app,
        supports_credentials=True,
        resources={r"/api/*": {"origins": ["*"]}},  # Allow all origins for testing
    )
    init_extensions(app)
    app.teardown_appcontext(close_mongo)
    register_audit_logger(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(guest_bp)
    app.register_blueprint(citizen_bp)
    app.register_blueprint(counsellor_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(comprehensive_bp)  # register the new comprehensive blueprint
    @app.get("/api/health")
    def health_check():
        """Simple health endpoint for deployment checks."""

        return jsonify({"status": "ok", "service": "YouthFinanceBot API"})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")),use_reloader=False)