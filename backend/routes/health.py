"""NeuroDriver — Health Check API Route."""
from flask import Blueprint, jsonify
from datetime import datetime

health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "system": "NeuroDriver Autonomous Driving Engine",
        "version": "2.5.0",
        "timestamp": datetime.now().isoformat()
    })
