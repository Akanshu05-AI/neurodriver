"""NeuroDriver — AI Driving Decision & XAI API Route."""
from flask import Blueprint, request, jsonify
from backend.services.ai_engine import AIEngineService
from backend.utils.validation import validate_json_payload, sanitize_float

decide_bp = Blueprint("decide", __name__)
ai_engine_service = AIEngineService()

@decide_bp.route("/api/decide", methods=["POST"])
def decide():
    data, err = validate_json_payload(request.json)
    if err:
        return jsonify({"error": err}), 400

    ego_state = data.get("ego_state", {})
    traffic = data.get("traffic", [])
    weather = data.get("weather", "clear")
    hazards = data.get("hazards", {})
    ear = sanitize_float(data.get("driver_ear", 0.32), default=0.32)

    result = ai_engine_service.process_driving_frame(
        ego_state=ego_state,
        traffic=traffic,
        weather=weather,
        hazards=hazards,
        driver_fatigue_ear=ear
    )

    return jsonify(result)
