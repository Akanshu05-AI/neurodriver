"""
NeuroDriver — Unified Risk Engine.
Calculates unified 0–100 collision and environmental risk score with explicit breakdown of top contributing factors.
"""

from ai_models.common.constants import WEATHER_CONFIG

class RiskEngine:
    """
    Evaluates total driving risk based on:
    1. Time-To-Collision (TTC) & Lead Vehicle Proximity
    2. Weather & Road Surface Friction
    3. Indian Road Hazards (Cattle, Potholes, Wrong-side driving, Overloaded vehicles)
    4. Driver Fatigue (EAR/PERCLOS)
    5. Traffic Density & Speed Variance
    """

    def evaluate_risk(
        self,
        ego_speed_kmh: float,
        ttc_seconds: float | None,
        lead_distance_m: float,
        weather: str = "clear",
        hazards: dict = None,
        fatigue_info: dict = None
    ) -> dict:
        hazards = hazards or {}
        fatigue_info = fatigue_info or {}

        score = 0.0
        contributors = []

        # 1. TTC & Proximity Risk (Max 40 pts)
        if ttc_seconds is not None:
            if ttc_seconds <= 1.0:
                score += 40.0
                contributors.append({"factor": "Critical TTC (<1.0s)", "weight": 40.0})
            elif ttc_seconds <= 2.0:
                score += 30.0
                contributors.append({"factor": "Imminent Collision Risk (TTC < 2.0s)", "weight": 30.0})
            elif ttc_seconds <= 3.5:
                score += 15.0
                contributors.append({"factor": "Short Headway (TTC < 3.5s)", "weight": 15.0})
        elif lead_distance_m < 20.0:
            score += 25.0
            contributors.append({"factor": "Close Following Distance (<20m)", "weight": 25.0})

        # 2. Weather & Visibility Risk (Max 25 pts)
        w_cfg = WEATHER_CONFIG.get(weather, WEATHER_CONFIG["clear"])
        w_risk = w_cfg["risk_weight"] * 25.0
        if w_risk > 0:
            score += w_risk
            contributors.append({"factor": f"Weather Severity ({weather.title()})", "weight": round(w_risk, 1)})

        # 3. Indian Road Hazards (Max 35 pts)
        cattle_dist = hazards.get("cattle_dist", float('inf'))
        wrong_side = hazards.get("wrong_side", False)
        pothole = hazards.get("pothole", False)
        overload = hazards.get("overload", False)

        if wrong_side:
            score += 35.0
            contributors.append({"factor": "Wrong-Side Oncoming Vehicle", "weight": 35.0})
        elif cattle_dist < 40.0:
            c_pts = 30.0 if cattle_dist < 20.0 else 15.0
            score += c_pts
            contributors.append({"factor": f"Stray Animal Hazard ({round(cattle_dist, 1)}m)", "weight": c_pts})

        if pothole:
            score += 10.0
            contributors.append({"factor": "Pothole Hazard Ahead", "weight": 10.0})

        if overload:
            score += 10.0
            contributors.append({"factor": "Overloaded Transport Vehicle Proximity", "weight": 10.0})

        # 4. Driver Fatigue (Max 30 pts)
        fatigue_level = fatigue_info.get("level", "ALERT")
        if fatigue_level == "SEVERE":
            score += 30.0
            contributors.append({"factor": "Severe Driver Fatigue (EAR < 0.25)", "weight": 30.0})
        elif fatigue_level == "DROWSY":
            score += 20.0
            contributors.append({"factor": "Moderate Driver Drowsiness", "weight": 20.0})
        elif fatigue_level == "FATIGUED":
            score += 10.0
            contributors.append({"factor": "Early Driver Fatigue", "weight": 10.0})

        # 5. Speed Hazard (Max 15 pts)
        if ego_speed_kmh > 100.0 and weather in ["rain", "heavy_rain", "fog", "storm"]:
            score += 15.0
            contributors.append({"factor": "Excessive Speed for Weather Conditions", "weight": 15.0})

        # Final score bounding [0, 100]
        final_score = round(min(100.0, max(0.0, score)), 1)

        if final_score >= 85.0:
            level = "CRITICAL"
        elif final_score >= 60.0:
            level = "HIGH"
        elif final_score >= 30.0:
            level = "MODERATE"
        else:
            level = "LOW"

        # Sort top contributors descending
        sorted_contributors = sorted(contributors, key=lambda x: x["weight"], reverse=True)

        return {
            "risk_score": final_score,
            "risk_level": level,
            "top_contributors": sorted_contributors[:4]
        }
