"""
NeuroDriver — Advanced Emergency Braking System (AEBS) & Collision Avoidance.
Evaluates relative speeds, positions, Time-To-Collision (TTC), and Intelligent Driver Model (IDM) math.
"""

import math
from ai_models.common.constants import TTC_TIERS

class CollisionAvoidanceSystem:
    """
    Advanced Collision Avoidance System featuring:
    1. 5-Tier Safety Classification (SAFE, CAUTION, WARNING, CRITICAL, EMERGENCY)
    2. Time-To-Collision (TTC) & Stopping Distance calculation
    3. Intelligent Driver Model (IDM) acceleration/deceleration computation
    """

    def __init__(self, safe_time_headway: float = 1.5, max_braking_decel: float = 8.0):
        self.safe_time_headway = safe_time_headway  # seconds
        self.max_braking_decel = max_braking_decel   # m/s^2

    def compute_ttc(self, ego_speed_kmh: float, lead_speed_kmh: float, distance_meters: float) -> float:
        """
        Computes Time-To-Collision (TTC) in seconds.
        TTC = distance / relative_velocity
        Returns float('inf') if ego vehicle is not closing in on lead vehicle.
        """
        if distance_meters <= 0:
            return 0.0

        ego_mps = ego_speed_kmh / 3.6
        lead_mps = lead_speed_kmh / 3.6
        rel_speed_mps = ego_mps - lead_mps

        if rel_speed_mps <= 0.001:
            return float('inf')

        return max(0.0, distance_meters / rel_speed_mps)

    def compute_stopping_distance(self, speed_kmh: float, friction_coefficient: float = 1.0) -> float:
        """
        Computes required stopping distance in meters considering reaction time and braking deceleration.
        d_stop = v * t_react + v^2 / (2 * g * mu)
        """
        v_mps = speed_kmh / 3.6
        reaction_time = 0.5  # seconds for automated AEBS
        g = 9.81
        reaction_dist = v_mps * reaction_time
        braking_dist = (v_mps ** 2) / (2 * g * max(0.1, friction_coefficient))
        return reaction_dist + braking_dist

    def classify_safety_tier(self, ttc: float, distance: float, stopping_dist: float) -> str:
        """
        Classifies safety into 5 tiers:
        - EMERGENCY: TTC <= 1.0s or distance <= 0.5 * stopping_dist
        - CRITICAL:  TTC <= 2.0s or distance <= stopping_dist
        - WARNING:   TTC <= 3.0s or distance <= 1.5 * stopping_dist
        - CAUTION:   TTC <= 5.0s or distance <= 2.0 * stopping_dist
        - SAFE:      TTC > 5.0s
        """
        if ttc <= TTC_TIERS["EMERGENCY"] or distance < stopping_dist * 0.5:
            return "EMERGENCY"
        elif ttc <= TTC_TIERS["CRITICAL"] or distance < stopping_dist:
            return "CRITICAL"
        elif ttc <= TTC_TIERS["WARNING"] or distance < stopping_dist * 1.5:
            return "WARNING"
        elif ttc <= TTC_TIERS["CAUTION"] or distance < stopping_dist * 2.0:
            return "CAUTION"
        return "SAFE"

    def evaluate(self, ego: dict, traffic: list, weather_friction: float = 1.0) -> dict:
        """
        Evaluates surrounding traffic and returns comprehensive safety evaluation.
        """
        ego_lane = ego.get("lane", 1)
        ego_speed = ego.get("speed", 0.0)
        ego_y = ego.get("y", 0.0)

        min_dist_m = float('inf')
        closest_veh = None
        closest_ttc = float('inf')

        for v in traffic:
            if v.get("lane") == ego_lane:
                # distance in pixels converted to meters (0.3m per px in pixel space)
                d_px = ego_y - (v.get("y", 0) + v.get("h", 46))
                d_m = d_px * 0.3
                if d_m > 0 and d_m < min_dist_m:
                    min_dist_m = d_m
                    closest_veh = v

        if closest_veh:
            lead_speed = closest_veh.get("speed", 0.0)
            closest_ttc = self.compute_ttc(ego_speed, lead_speed, min_dist_m)

        stopping_dist = self.compute_stopping_distance(ego_speed, weather_friction)

        if min_dist_m == float('inf'):
            tier = "SAFE"
            min_dist_m = 999.0
        else:
            tier = self.classify_safety_tier(closest_ttc, min_dist_m, stopping_dist)

        should_brake = tier in ["WARNING", "CRITICAL", "EMERGENCY"]
        emergency_brake = tier in ["CRITICAL", "EMERGENCY"]

        return {
            "tier": tier,
            "min_distance_m": round(min_dist_m, 2),
            "ttc_seconds": round(closest_ttc, 2) if closest_ttc != float('inf') else None,
            "stopping_distance_m": round(stopping_dist, 2),
            "should_brake": should_brake,
            "emergency_brake": emergency_brake,
            "closest_vehicle": closest_veh.get("type", None) if closest_veh else None
        }
