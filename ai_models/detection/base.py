"""
NeuroDriver — Abstract Base Object Detector.
Establishes clear API contract for extensible object detection implementations (SimulationDetector, YOLODetector).
"""

from abc import ABC, abstractmethod

class BaseObjectDetector(ABC):
    """Abstract interface for object detection & ranging modules."""

    @abstractmethod
    def detect(self, frame_or_objects: list | object) -> list[dict]:
        """
        Executes detection and returns structured list of object records:
        [{
            "class": str,
            "distance_m": float,
            "threat": str,
            "confidence": float,
            "bbox": [x, y, w, h]
        }]
        """
        pass
