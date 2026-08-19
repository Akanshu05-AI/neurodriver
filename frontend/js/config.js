/**
 * NeuroDriver Frontend Configuration & Safety Parameters.
 */

window.NEURO_CONFIG = {
  API_BASE_URL: "http://localhost:5000",
  CANVAS_PIXEL_RATIO: window.devicePixelRatio || 1,
  ROAD_LANES: 4,
  PIXEL_TO_METER_SCALE: 0.3,
  
  TTC_TIERS: {
    EMERGENCY: 1.0,
    CRITICAL: 2.0,
    WARNING: 3.0,
    CAUTION: 5.0
  },
  
  DEFAULT_SPEED_KMH: 60,
  MAX_SPEED_KMH: 140
};
