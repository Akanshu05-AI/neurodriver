"""NeuroDriver — Object Detection & Ranging API Route."""
from flask import Blueprint, request, jsonify
from ai_models.detection.simulation_detector import SimulationDetector
from backend.utils.validation import validate_json_payload

detect_bp = Blueprint("detect", __name__)
detector = SimulationDetector()

@detect_bp.route("/api/detect", methods=["POST"])
def detect():
    data, err = validate_json_payload(request.json)
    if err:
        return jsonify({"error": err}), 400

    objects = data.get("objects", [])
    results = detector.detect(objects)
    return jsonify({"detections": results, "count": len(results)})
