"""NeuroDriver — Telemetry Stream API Route."""
from flask import Blueprint, jsonify
from datetime import datetime

telemetry_bp = Blueprint("telemetry", __name__)

@telemetry_bp.route("/api/telemetry", methods=["GET"])
def telemetry():
    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "status": "TELEMETRY_ONLINE",
        "buffer_frames": 120,
        "sample_rate_hz": 60
    })
