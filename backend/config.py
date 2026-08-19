"""
NeuroDriver Backend Configuration.
Centralized settings, environment parameters, and safety threshold definitions.
"""

import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "neurodriver-production-secret-2026")
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    PORT = int(os.getenv("PORT", 5000))
    HOST = os.getenv("HOST", "0.0.0.0")

    # Safety limits
    MAX_SPEED_KMH = 140.0
    CRITICAL_TTC_SECONDS = 1.5
    EMERGENCY_BRAKE_DECEL = 8.0  # m/s^2

    # CORS settings
    CORS_ORIGINS = "*"
