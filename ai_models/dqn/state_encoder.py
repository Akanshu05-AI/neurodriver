"""
NeuroDriver — State Vector Encoder for Deep Q-Network Agent.
Encodes raw telemetry, weather, traffic, and Indian road hazard parameters into a normalized 16-element state vector.
"""

import numpy as np
from ai_models.common.constants import WEATHER_CONFIG

class StateEncoder:
    """
    Translates raw environment observations into a standardized 16-element normalized numpy array vector:
    [0]  ego_speed / 120
    [1]  ego_lane / 4
    [2]  weather_risk_weight
    [3]  front_vehicle_distance / 200
    [4]  front_vehicle_rel_speed / 120
    [5]  left_lane_clearance (0.0 - 1.0)
    [6]  right_lane_clearance (0.0 - 1.0)
    [7]  cattle_distance / 200
    [8]  pothole_distance / 200
    [9]  wrong_side_distance / 200
    [10] driver_fatigue_level (0.0 - 1.0)
    [11] visibility_meters / 300
    [12] road_friction_coefficient (0.0 - 1.0)
    [13] traffic_density_level / 5
    [14] collision_risk_score / 100
    [15] emergency_brake_flag (0 or 1)
    """

    STATE_SIZE = 16

    @staticmethod
    def encode(ego: dict, traffic: list, weather: str = "clear", hazards: dict = None, driver_fatigue: float = 0.1) -> np.ndarray:
        hazards = hazards or {}
        
        speed = min(120.0, float(ego.get("speed", 0.0))) / 120.0
        lane = float(ego.get("lane", 1)) / 4.0

        w_cfg = WEATHER_CONFIG.get(weather, WEATHER_CONFIG["clear"])
        weather_weight = w_cfg["risk_weight"]
        visibility = w_cfg["visibility_meters"] / 300.0
        friction = w_cfg["friction_coefficient"]

        # Front traffic dist & rel speed
        ego_lane = ego.get("lane", 1)
        lead_dist = 200.0
        lead_rel_speed = 0.0

        for v in traffic:
            if v.get("lane") == ego_lane:
                d = float(v.get("dist", 200.0))
                if d < lead_dist:
                    lead_dist = d
                    lead_rel_speed = float(ego.get("speed", 0)) - float(v.get("speed", 60))

        lead_dist_norm = min(200.0, max(0.0, lead_dist)) / 200.0
        lead_rel_speed_norm = np.clip(lead_rel_speed / 120.0, -1.0, 1.0)

        # Lane clearance
        left_lane_traffic = [v for v in traffic if v.get("lane") == ego_lane - 1]
        right_lane_traffic = [v for v in traffic if v.get("lane") == ego_lane + 1]

        left_clearance = min([v.get("dist", 200.0) for v in left_lane_traffic], default=200.0) / 200.0
        right_clearance = min([v.get("dist", 200.0) for v in right_lane_traffic], default=200.0) / 200.0

        # Indian Hazards
        cattle_dist = float(hazards.get("cattle_dist", 200.0)) / 200.0
        pothole_dist = float(hazards.get("pothole_dist", 200.0)) / 200.0
        wrong_side_dist = float(hazards.get("wrong_side_dist", 200.0)) / 200.0

        density = float(hazards.get("traffic_density", 3)) / 5.0
        risk_score = float(hazards.get("risk_score", 0.0)) / 100.0
        emergency_flag = 1.0 if hazards.get("emergency_brake", False) else 0.0

        state = np.array([
            speed,
            lane,
            weather_weight,
            lead_dist_norm,
            lead_rel_speed_norm,
            left_clearance,
            right_clearance,
            cattle_dist,
            pothole_dist,
            wrong_side_dist,
            np.clip(driver_fatigue, 0.0, 1.0),
            visibility,
            friction,
            density,
            risk_score,
            emergency_flag
        ], dtype=np.float32)

        return state
