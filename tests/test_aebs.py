"""
Unit tests for Collision Avoidance & AEBS system.
"""

from ai_models.collision.aebs import CollisionAvoidanceSystem

def test_compute_ttc():
    aebs = CollisionAvoidanceSystem()
    # Ego speed = 100 km/h, Lead speed = 60 km/h -> relative speed = 40 km/h (11.11 m/s)
    # Dist = 33.33 m -> TTC = 3.0s
    ttc = aebs.compute_ttc(100.0, 60.0, 33.33)
    assert abs(ttc - 3.0) < 0.1

def test_aebs_tiers():
    aebs = CollisionAvoidanceSystem()
    ego = {"lane": 1, "speed": 80.0, "y": 500}

    # Obstacle ahead and close -> EMERGENCY (y=400, h=46 => distance = 500 - 446 = 54px = 16.2m)
    traffic_emergency = [{"lane": 1, "y": 400, "h": 46, "speed": 20.0, "type": "car"}]
    res_emergency = aebs.evaluate(ego, traffic_emergency)
    assert res_emergency["tier"] in ["EMERGENCY", "CRITICAL"]
    assert res_emergency["emergency_brake"] is True

    # Obstacle far away -> SAFE
    traffic_safe = [{"lane": 1, "y": 0, "h": 46, "speed": 80.0, "type": "car"}]
    res_safe = aebs.evaluate(ego, traffic_safe)
    assert res_safe["tier"] == "SAFE"
    assert res_safe["should_brake"] is False
