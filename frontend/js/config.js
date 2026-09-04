/**
 * NeuroDriver Frontend Configuration & Safety Parameters.
 * Dynamically resolves backend API endpoint for local development, Vercel, and Render deployments.
 */

(function() {
  const urlParams = new URLSearchParams(window.location.search);
  const paramApi = urlParams.get('api');
  if (paramApi) {
    try {
      localStorage.setItem('neuro_api_base_url', paramApi.replace(/\/$/, ''));
    } catch(e) {}
  }

  const storedApi = localStorage.getItem('neuro_api_base_url');
  const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

  let initialBaseUrl = "http://localhost:5000";
  if (paramApi) {
    initialBaseUrl = paramApi.replace(/\/$/, '');
  } else if (storedApi) {
    initialBaseUrl = storedApi.replace(/\/$/, '');
  } else if (!isLocalhost) {
    initialBaseUrl = "https://neurodriver-backend.onrender.com";
  }

  window.NEURO_CONFIG = {
    API_BASE_URL: initialBaseUrl,
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
})();
