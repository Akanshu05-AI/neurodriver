"""
NeuroDriver Backend Application Entrypoint.
Modular Flask REST server powering AI driving inference, scenario benchmarking, risk engine, and telemetry.
"""

import sys
import os
# Ensure project root is in sys.path when running python backend/app.py directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, jsonify
from flask_cors import CORS
from backend.config import Config
from backend.routes.health import health_bp
from backend.routes.decide import decide_bp
from backend.routes.drowsiness import drowsiness_bp
from backend.routes.detect import detect_bp
from backend.routes.analytics import analytics_bp
from backend.routes.scenarios import scenarios_bp
from backend.routes.telemetry import telemetry_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources={r"/*": {"origins": Config.CORS_ORIGINS}})

    # Register Blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(decide_bp)
    app.register_blueprint(drowsiness_bp)
    app.register_blueprint(detect_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(scenarios_bp)
    app.register_blueprint(telemetry_bp)

    @app.route("/")
    def index():
        return jsonify({
            "system": "NeuroDriver Autonomous Driving REST API Server",
            "version": "2.5.0",
            "status": "online",
            "endpoints": {
                "health": "/health",
                "decide": "POST /api/decide",
                "drowsiness": "POST /api/drowsiness",
                "detect": "POST /api/detect",
                "analytics": "GET /api/analytics",
                "scenarios": "GET /api/scenarios",
                "benchmark": "POST /api/scenarios/benchmark",
                "telemetry": "GET /api/telemetry"
            },
            "frontend_ui": "Open frontend/index.html directly in your browser"
        })

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
