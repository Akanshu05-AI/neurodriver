"""NeuroDriver — Telemetry Analytics & Session Stats API Route."""
from flask import Blueprint, jsonify
from datetime import datetime

analytics_bp = Blueprint("analytics", __name__)

session_stats = {
    "session_id": "session-live-01",
    "start_time": datetime.now().isoformat(),
    "total_collisions": 0,
    "total_near_misses": 0,
    "distance_km": 0.0,
    "average_speed_kmh": 58.4,
    "overall_drive_score": 92.5
}

@analytics_bp.route("/api/analytics", methods=["GET"])
def analytics():
    return jsonify(session_stats)
