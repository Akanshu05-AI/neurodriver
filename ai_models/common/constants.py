"""
NeuroDriver — Core Constants and Configuration Parameters.
Contains safety thresholds, physical constants, environmental modifiers, and Indian road hazard specifications.
"""

# ── SAFETY TIERS & TTC THRESHOLDS (Seconds) ──
TTC_TIERS = {
    "EMERGENCY": 1.0,
    "CRITICAL": 2.0,
    "WARNING": 3.0,
    "CAUTION": 5.0,
    "SAFE": float("inf")
}

# ── VEHICLE DIMENSIONS & SPEEDS (Meters & km/h) ──
VEHICLE_PROPERTIES = {
    "sedan": {"length": 4.5, "width": 1.8, "height": 1.5, "max_speed": 140},
    "truck": {"length": 8.0, "width": 2.5, "height": 3.5, "max_speed": 80},
    "bus": {"length": 10.0, "width": 2.6, "height": 3.2, "max_speed": 75},
    "bike": {"length": 2.0, "width": 0.8, "height": 1.2, "max_speed": 90},
    "auto": {"length": 2.6, "width": 1.3, "height": 1.7, "max_speed": 60},
    "pedestrian": {"length": 0.5, "width": 0.5, "height": 1.7, "max_speed": 5},
    "cattle": {"length": 2.2, "width": 1.0, "height": 1.4, "max_speed": 10},
    "dog": {"length": 0.8, "width": 0.4, "height": 0.6, "max_speed": 15}
}

# ── ENVIRONMENT WEATHER MODIFIERS ──
WEATHER_CONFIG = {
    "clear": {"speed_multiplier": 1.0, "visibility_meters": 300, "friction_coefficient": 1.0, "risk_weight": 0.0},
    "rain": {"speed_multiplier": 0.75, "visibility_meters": 150, "friction_coefficient": 0.7, "risk_weight": 0.25},
    "heavy_rain": {"speed_multiplier": 0.55, "visibility_meters": 80, "friction_coefficient": 0.5, "risk_weight": 0.45},
    "fog": {"speed_multiplier": 0.50, "visibility_meters": 40, "friction_coefficient": 0.85, "risk_weight": 0.50},
    "night": {"speed_multiplier": 0.85, "visibility_meters": 100, "friction_coefficient": 0.95, "risk_weight": 0.20},
    "storm": {"speed_multiplier": 0.40, "visibility_meters": 30, "friction_coefficient": 0.4, "risk_weight": 0.65}
}

# ── INDIA-SPECIFIC HAZARDS THREAT LEVEL ──
INDIAN_HAZARDS = {
    "cattle": {"threat": "CRITICAL", "evasive_priority": "HIGH", "action": "EMERGENCY_BRAKE_OR_SWERVE"},
    "pothole": {"threat": "WARNING", "evasive_priority": "MEDIUM", "action": "REDUCE_SPEED_SWERVE"},
    "wrong_side_vehicle": {"threat": "CRITICAL", "evasive_priority": "MAXIMUM", "action": "SWERVE_SAFETY_LANE"},
    "overloaded_truck": {"threat": "HIGH", "evasive_priority": "MEDIUM", "action": "INCREASE_FOLLOWING_DISTANCE"},
    "ambulance": {"threat": "HIGH", "evasive_priority": "HIGH", "action": "YIELD_RIGHT_OF_WAY"},
    "dog": {"threat": "HIGH", "evasive_priority": "HIGH", "action": "CONTROLLED_BRAKING"}
}

# ── DROWSINESS THRESHOLDS ──
EAR_THRESHOLD = 0.25
PERCLOS_THRESHOLD_SEVERE = 0.40
PERCLOS_THRESHOLD_MODERATE = 0.25

# ── DQN AGENT DISCRETE ACTIONS ──
ACTIONS = ["CRUISE", "ACCELERATE", "BRAKE", "TURN_LEFT", "TURN_RIGHT"]
