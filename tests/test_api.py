"""
Integration tests for Flask REST API endpoints.
"""

from backend.app import create_app

def test_api_routes():
    app = create_app()
    client = app.test_client()

    # 1. GET /health
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json["status"] == "ok"

    # 2. POST /api/decide
    res_decide = client.post("/api/decide", json={
        "ego_state": {"speed": 60.0, "lane": 1, "target_speed": 60.0},
        "traffic": [{"lane": 1, "y": 200, "h": 46, "speed": 50.0}],
        "weather": "clear",
        "hazards": {"cattle_dist": 150.0}
    })
    assert res_decide.status_code == 200
    assert "action" in res_decide.json
    assert "risk_score" in res_decide.json
    assert "xai_explanation" in res_decide.json

    # 3. GET /api/scenarios
    res_scenarios = client.get("/api/scenarios")
    assert res_scenarios.status_code == 200
    assert len(res_scenarios.json["scenarios"]) == 12

    # 4. POST /api/scenarios/benchmark
    res_bench = client.post("/api/scenarios/benchmark", json={"scenario_id": "monsoon_rain", "runs": 10})
    assert res_bench.status_code == 200
    assert res_bench.json["status"] == "BENCHMARK_COMPLETED"
