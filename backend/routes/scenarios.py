"""NeuroDriver — Scenario Management & Benchmark API Route."""
from flask import Blueprint, request, jsonify
from backend.services.scenario_service import ScenarioService
from backend.utils.validation import validate_json_payload

scenarios_bp = Blueprint("scenarios", __name__)

@scenarios_bp.route("/api/scenarios", methods=["GET"])
def list_scenarios():
    return jsonify({"scenarios": ScenarioService.list_scenarios()})

@scenarios_bp.route("/api/scenarios/<scenario_id>", methods=["GET"])
def get_scenario(scenario_id):
    scen = ScenarioService.get_scenario(scenario_id)
    if not scen:
        return jsonify({"error": f"Scenario '{scenario_id}' not found"}), 404
    return jsonify(scen)

@scenarios_bp.route("/api/scenarios/benchmark", methods=["POST"])
def run_benchmark():
    data, _ = validate_json_payload(request.json)
    data = data or {}
    scenario_id = data.get("scenario_id", "normal_highway")
    runs = int(data.get("runs", 20))

    result = ScenarioService.evaluate_benchmark(scenario_id, runs)
    return jsonify(result)
