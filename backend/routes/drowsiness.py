"""NeuroDriver — Drowsiness Analysis API Route."""
from flask import Blueprint, request, jsonify
from ai_models.drowsiness.detector import DrowsinessDetector
from backend.utils.validation import validate_json_payload, sanitize_float

drowsiness_bp = Blueprint("drowsiness", __name__)
detector = DrowsinessDetector()

@drowsiness_bp.route("/api/drowsiness", methods=["POST"])
def drowsiness():
    data, err = validate_json_payload(request.json)
    if err:
        return jsonify({"error": err}), 400

    ear = sanitize_float(data.get("ear", 0.32), default=0.32)
    eval_result = detector.classify(ear)
    return jsonify(eval_result)
