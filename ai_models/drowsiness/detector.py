"""
NeuroDriver — Driver Drowsiness & Fatigue Detector.
Uses Eye Aspect Ratio (EAR) + PERCLOS (Percentage of Eye Closure) algorithms to monitor driver alertness.
"""

import numpy as np
from collections import deque
from ai_models.common.constants import EAR_THRESHOLD, PERCLOS_THRESHOLD_SEVERE, PERCLOS_THRESHOLD_MODERATE

class DrowsinessDetector:
    """
    Fatigue state machine supporting 4 levels:
    - ALERT: Normal driver condition (EAR >= 0.25, PERCLOS < 0.15)
    - FATIGUED: Early signs of eyelid drop (PERCLOS >= 0.15)
    - DROWSY: Moderate drowsiness (PERCLOS >= 0.25)
    - SEVERE: Prolonged eye closure (PERCLOS >= 0.40 or EAR < 0.18 consecutive frames)
    """

    def __init__(self, ear_threshold: float = EAR_THRESHOLD, consecutive_frames_threshold: int = 20):
        self.ear_threshold = ear_threshold
        self.consecutive_frames_threshold = consecutive_frames_threshold
        self.consecutive_count = 0
        self.ear_history = deque(maxlen=60)  # rolling window of last 60 observations

    def compute_ear(self, eye_landmarks: np.ndarray) -> float:
        """
        Computes Eye Aspect Ratio (EAR) from 6 2D facial eye landmarks:
        EAR = (||p2 - p6|| + ||p3 - p5||) / (2 * ||p1 - p4||)
        """
        if len(eye_landmarks) < 6:
            return 0.35

        A = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        B = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
        C = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])

        if C < 1e-6:
            return 0.35

        ear = (A + B) / (2.0 * C)
        return float(ear)

    def classify(self, ear: float) -> dict:
        """
        Updates history, computes PERCLOS metric, and determines driver state.
        """
        self.ear_history.append(ear)

        if ear < self.ear_threshold:
            self.consecutive_count += 1
        else:
            self.consecutive_count = max(0, self.consecutive_count - 1)

        closed_count = sum(1 for e in self.ear_history if e < self.ear_threshold)
        perclos = closed_count / max(1, len(self.ear_history))

        if perclos >= PERCLOS_THRESHOLD_SEVERE or ear < 0.18 or self.consecutive_count >= self.consecutive_frames_threshold:
            level = "SEVERE"
            is_drowsy = True
            risk_increment = 40.0
        elif perclos >= PERCLOS_THRESHOLD_MODERATE or self.consecutive_count >= 10:
            level = "DROWSY"
            is_drowsy = True
            risk_increment = 25.0
        elif perclos >= 0.15:
            level = "FATIGUED"
            is_drowsy = False
            risk_increment = 10.0
        else:
            level = "ALERT"
            is_drowsy = False
            risk_increment = 0.0

        return {
            "is_drowsy": is_drowsy,
            "level": level,
            "ear": round(float(ear), 3),
            "perclos": round(float(perclos), 3),
            "consecutive_closed_frames": self.consecutive_count,
            "risk_increment": risk_increment
        }
