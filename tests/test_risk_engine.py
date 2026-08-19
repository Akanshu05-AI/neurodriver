"""
Unit tests for Unified Risk Engine.
"""

from ai_models.risk.risk_engine import RiskEngine

def test_risk_engine_clear():
    engine = RiskEngine()
    res = engine.evaluate_risk(ego_speed_kmh=60.0, ttc_seconds=10.0, lead_distance_m=100.0, weather="clear")
    assert res["risk_level"] == "LOW"
    assert res["risk_score"] < 30.0

def test_risk_engine_critical_wrong_side():
    engine = RiskEngine()
    res = engine.evaluate_risk(
        ego_speed_kmh=80.0,
        ttc_seconds=1.2,
        lead_distance_m=15.0,
        weather="heavy_rain",
        hazards={"wrong_side": True}
    )
    assert res["risk_level"] in ["HIGH", "CRITICAL"]
    assert res["risk_score"] >= 70.0
    assert len(res["top_contributors"]) > 0
