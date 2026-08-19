"""
NeuroDriver — API Request Validation & Numerical Safety Guards.
Prevents NaN, Infinite values, missing fields, or malformed inputs from crashing backend services.
"""

from flask import jsonify

def validate_json_payload(data: dict | None, required_keys: list[str] = None) -> tuple[dict | None, str | None]:
    """Validates that payload is non-null JSON dictionary and contains required keys."""
    if data is None or not isinstance(data, dict):
        return None, "Invalid or missing JSON payload"

    if required_keys:
        for key in required_keys:
            if key not in data:
                return None, f"Missing required field in payload: '{key}'"

    return data, None

def sanitize_float(value, default: float = 0.0, min_val: float = None, max_val: float = None) -> float:
    """Safely converts input to float and clamps within range."""
    try:
        val = float(value)
        if val != val or val == float('inf') or val == float('-inf'):  # NaN check
            val = default
    except (TypeError, ValueError):
        val = default

    if min_val is not None:
        val = max(min_val, val)
    if max_val is not None:
        val = min(max_val, val)

    return float(val)
