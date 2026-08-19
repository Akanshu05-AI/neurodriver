"""
NeuroDriver — Simulation Detector Implementation.
Uses pinhole camera distance estimation (D = (f * H_real) / h_bbox) and object classification.
"""

import random
from ai_models.detection.base import BaseObjectDetector
from ai_models.common.constants import INDIAN_HAZARDS

class SimulationDetector(BaseObjectDetector):
    """
    Simulation detector that converts ground-truth objects and bounding box dimensions
    into realistic sensor readings with pinhole geometry distance estimation.
    """

    FOCAL_LENGTH = 700.0  # Camera focal length in pixels

    REAL_HEIGHTS = {
        "car": 1.5,
        "sedan": 1.5,
        "truck": 3.5,
        "bus": 3.2,
        "bike": 1.2,
        "auto": 1.7,
        "pedestrian": 1.7,
        "cattle": 1.4,
        "dog": 0.6,
        "pothole": 0.1,
        "wrong_side_vehicle": 1.6
    }

    THREAT_LEVELS = {
        "cattle": "CRITICAL",
        "pedestrian": "CRITICAL",
        "wrong_side_vehicle": "CRITICAL",
        "dog": "HIGH",
        "truck": "HIGH",
        "bus": "MEDIUM",
        "sedan": "LOW",
        "car": "LOW",
        "bike": "MEDIUM",
        "auto": "MEDIUM",
        "pothole": "WARNING"
    }

    def estimate_distance(self, bbox_h: float, obj_type: str) -> float:
        """
        Pinhole geometry formula:
        Distance = (Focal Length * Real Height) / Bounding Box Height
        """
        real_h = self.REAL_HEIGHTS.get(obj_type, 1.5)
        h_px = max(4.0, float(bbox_h))
        return float((self.FOCAL_LENGTH * real_h) / h_px)

    def detect(self, objects: list) -> list[dict]:
        """Processes list of simulated objects."""
        results = []
        for obj in objects:
            obj_type = obj.get("type", "car")
            bbox_h = obj.get("h", 46)
            dist_m = self.estimate_distance(bbox_h, obj_type)

            threat = self.THREAT_LEVELS.get(obj_type, "MEDIUM")
            confidence = round(min(0.99, max(0.60, 0.85 + random.uniform(-0.1, 0.1))), 2)

            results.append({
                "class": obj_type,
                "distance_m": round(dist_m, 1),
                "threat": threat,
                "confidence": confidence,
                "bbox": [obj.get("x", 0), obj.get("y", 0), obj.get("w", 30), obj.get("h", 46)]
            })

        return results
