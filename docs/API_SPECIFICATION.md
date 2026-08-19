# NeuroDriver — Open REST API Specification

## 1. Health Endpoint
`GET /health`
* **Response**:
```json
{
  "status": "ok",
  "system": "NeuroDriver Autonomous Driving Engine",
  "version": "2.5.0",
  "timestamp": "2026-08-19T20:54:28+05:30"
}
```

---

## 2. AI Decision & XAI Endpoint
`POST /api/decide`
* **Request**:
```json
{
  "ego_state": { "speed": 60.0, "lane": 1, "target_speed": 60.0 },
  "traffic": [{ "lane": 1, "y": 200, "h": 46, "speed": 50.0 }],
  "weather": "clear",
  "hazards": { "cattle_dist": 150.0 },
  "driver_ear": 0.32
}
```
* **Response**:
```json
{
  "action": "CRUISE",
  "target_speed": 60.0,
  "collision_risk": "LOW",
  "risk_score": 10.0,
  "top_risk_contributors": [],
  "aebs_tier": "SAFE",
  "ttc_seconds": 5.4,
  "drowsiness_level": "ALERT",
  "ear_score": 0.32,
  "xai_explanation": {
    "selected_action": "CRUISE",
    "primary_reason": "Vehicle maintaining target speed on open road",
    "q_value": 0.85
  },
  "response_time_ms": 1.2
}
```

---

## 3. Scenario & Benchmark Endpoints
- `GET /api/scenarios` — List 12 Indian road scenarios.
- `POST /api/scenarios/benchmark` — Execute 20-run evaluation benchmark.
