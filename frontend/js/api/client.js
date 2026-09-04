/**
 * NeuroDriver API Client.
 * Handles backend REST requests (/api/decide, /api/scenarios, /health) with automatic offline fallback,
 * dynamic base URL configuration, and live health probing.
 */

class NeuroApiClient {
  constructor(baseUrl = window.NEURO_CONFIG.API_BASE_URL) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.isOnline = false;
    this.lastLatency = null;
    this.onStatusChange = null;
    
    // Auto-probe health on boot
    this.checkHealth();
  }

  setBaseUrl(newUrl) {
    if (!newUrl) return;
    this.baseUrl = newUrl.trim().replace(/\/$/, '');
    try {
      localStorage.setItem('neuro_api_base_url', this.baseUrl);
    } catch(e) {}
    window.NEURO_CONFIG.API_BASE_URL = this.baseUrl;
    return this.checkHealth();
  }

  async checkHealth() {
    const start = performance.now();
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3500);
      const res = await fetch(`${this.baseUrl}/health`, {
        signal: controller.signal,
        headers: { "Accept": "application/json" }
      });
      clearTimeout(timeoutId);

      if (res.ok) {
        this.isOnline = true;
        this.lastLatency = Math.round(performance.now() - start);
        const data = await res.json();
        if (typeof this.onStatusChange === 'function') {
          this.onStatusChange(true, this.lastLatency, data);
        }
        return { online: true, latency: this.lastLatency, data };
      }
    } catch (err) {
      // Failed to connect
    }
    this.isOnline = false;
    this.lastLatency = null;
    if (typeof this.onStatusChange === 'function') {
      this.onStatusChange(false, null, null);
    }
    return { online: false, latency: null, data: null };
  }

  async makeRequest(endpoint, method = "GET", payload = null) {
    try {
      const options = {
        method,
        headers: { "Content-Type": "application/json" }
      };
      if (payload) options.body = JSON.stringify(payload);

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);
      options.signal = controller.signal;

      const res = await fetch(`${this.baseUrl}${endpoint}`, options);
      clearTimeout(timeoutId);

      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      this.isOnline = true;
      return await res.json();
    } catch (err) {
      this.isOnline = false;
      return null;
    }
  }

  async getDecision(egoState, traffic, weather, hazards, earScore) {
    const data = await this.makeRequest("/api/decide", "POST", {
      ego_state: egoState,
      traffic,
      weather,
      hazards,
      driver_ear: earScore
    });

    if (data) return data;

    // Offline heuristic fallback
    const minDist = Math.min(...traffic.map(v => v.dist || 999), 999);
    let action = "CRUISE";
    let riskLevel = "SAFE";
    let riskScore = 10;
    let targetSpeed = egoState.target_speed || 60;

    if (minDist < 30) {
      action = "EMERGENCY_BRAKE";
      riskLevel = "CRITICAL";
      riskScore = 90;
      targetSpeed = 0;
    } else if (minDist < 70) {
      action = "BRAKE";
      riskLevel = "WARNING";
      riskScore = 55;
      targetSpeed = targetSpeed * 0.5;
    }

    return {
      action,
      target_speed: targetSpeed,
      collision_risk: riskLevel,
      risk_score: riskScore,
      top_risk_contributors: [{ factor: "Proximity to lead vehicle", weight: 40 }],
      aebs_tier: riskLevel === "CRITICAL" ? "EMERGENCY" : "SAFE",
      xai_explanation: {
        selected_action: action,
        primary_reason: "Client-side safety heuristic fallback (Render/Local backend offline)",
        q_value: 0.85
      },
      response_time_ms: 1.0
    };
  }

  async fetchScenarios() {
    return await this.makeRequest("/api/scenarios", "GET");
  }

  async runBenchmark(scenarioId, runs = 20) {
    return await this.makeRequest("/api/scenarios/benchmark", "POST", { scenario_id: scenarioId, runs });
  }
}

window.apiClient = new NeuroApiClient();
