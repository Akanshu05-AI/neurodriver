"""
NeuroDriver — Unified AI Engine Service.
Orchestrates AEBS, DQN Reinforcement Learning Agent, Drowsiness Detector, Risk Engine, and Object Detector.
"""

import time
from ai_models.collision.aebs import CollisionAvoidanceSystem
from ai_models.dqn.agent import DQNAgent
from ai_models.dqn.state_encoder import StateEncoder
from ai_models.drowsiness.detector import DrowsinessDetector
from ai_models.detection.simulation_detector import SimulationDetector
from ai_models.risk.risk_engine import RiskEngine

class AIEngineService:
    """Unified service handling autonomous driving inference, AEBS, risk estimation, and XAI."""

    def __init__(self):
        self.aebs = CollisionAvoidanceSystem()
        self.dqn_agent = DQNAgent()
        self.drowsiness_detector = DrowsinessDetector()
        self.risk_engine = RiskEngine()
        self.object_detector = SimulationDetector()

    def process_driving_frame(
        self,
        ego_state: dict,
        traffic: list,
        weather: str = "clear",
        hazards: dict = None,
        driver_fatigue_ear: float = 0.32
    ) -> dict:
        t0 = time.time()
        hazards = hazards or {}

        # 1. AEBS Safety Evaluation
        aebs_eval = self.aebs.evaluate(ego_state, traffic)

        # 2. Drowsiness Monitoring
        fatigue_eval = self.drowsiness_detector.classify(driver_fatigue_ear)

        # 3. Object Detection & Ranging
        detected_objects = self.object_detector.detect(traffic)

        # 4. Risk Engine Assessment
        risk_eval = self.risk_engine.evaluate_risk(
            ego_speed_kmh=ego_state.get("speed", 0.0),
            ttc_seconds=aebs_eval.get("ttc_seconds"),
            lead_distance_m=aebs_eval.get("min_distance_m", 200.0),
            weather=weather,
            hazards=hazards,
            fatigue_info=fatigue_eval
        )

        # Update hazards with computed risk
        hazards["risk_score"] = risk_eval["risk_score"]
        hazards["emergency_brake"] = aebs_eval["emergency_brake"]

        # 5. State Vector Encoding
        state_vector = StateEncoder.encode(
            ego=ego_state,
            traffic=traffic,
            weather=weather,
            hazards=hazards,
            driver_fatigue=fatigue_eval["perclos"]
        )

        # 6. DQN Reinforcement Learning Action
        action_idx, action_name, q_val = self.dqn_agent.act(state_vector)

        # 7. Action Override based on AEBS Safety Tier
        final_action = action_name
        target_speed = float(ego_state.get("target_speed", 60.0))

        if aebs_eval["emergency_brake"]:
            final_action = "EMERGENCY_BRAKE"
            target_speed = 0.0
        elif aebs_eval["should_brake"]:
            final_action = "BRAKE"
            target_speed = max(0.0, target_speed * 0.4)
        elif hazards.get("wrong_side", False):
            final_action = "TURN_LEFT"  # Evasive swerve
            target_speed = max(20.0, target_speed * 0.6)

        # 8. Explainable AI (XAI) Explanation
        xai_explanation = self.dqn_agent.explain_decision(
            state=state_vector,
            action_name=final_action,
            risk_info=risk_eval
        )

        latency_ms = round((time.time() - t0) * 1000.0, 2)

        return {
            "action": final_action,
            "target_speed": round(target_speed, 1),
            "collision_risk": risk_eval["risk_level"],
            "risk_score": risk_eval["risk_score"],
            "top_risk_contributors": risk_eval["top_contributors"],
            "aebs_tier": aebs_eval["tier"],
            "ttc_seconds": aebs_eval["ttc_seconds"],
            "drowsiness_level": fatigue_eval["level"],
            "ear_score": fatigue_eval["ear"],
            "detected_objects": detected_objects[:6],
            "xai_explanation": xai_explanation,
            "response_time_ms": latency_ms
        }
