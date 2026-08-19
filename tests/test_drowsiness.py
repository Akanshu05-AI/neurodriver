"""
Unit tests for Driver Drowsiness Detector.
"""

import numpy as np
from ai_models.drowsiness.detector import DrowsinessDetector

def test_drowsiness_alert():
    detector = DrowsinessDetector()
    eval_res = detector.classify(0.35)
    assert eval_res["level"] == "ALERT"
    assert eval_res["is_drowsy"] is False

def test_drowsiness_severe():
    detector = DrowsinessDetector()
    # Feed closed eye EAR (0.15) for 25 consecutive frames
    for _ in range(25):
        eval_res = detector.classify(0.15)
    assert eval_res["level"] == "SEVERE"
    assert eval_res["is_drowsy"] is True
