# NeuroDriver — Version Changelog

## [2.5.1] - 2026-09-04

### ☁️ Cloud Deployment & Production Orchestration
- **Render Backend Deployment Support**: Added `render.yaml` Blueprint and `Procfile` targeting production Gunicorn WSGI workers with `/health` checks.
- **Vercel Frontend Deployment Support**: Added root and frontend `vercel.json` configurations with clean URL rewrites.
- **Dynamic In-App API Connector**: Added interactive connection manager popup to `#api-status` badge with live latency probing, `localStorage` persistence, and URL query parameter (`?api=...`) auto-detection.
- **Deployment Documentation**: Added comprehensive, step-by-step cloud deployment instructions to `README.md`.

## [2.5.0] - 2026-08-19

### 🚀 Major Architectural Refactoring & Upgrades
- **Modular Directory Architecture**: Separated monolithic files into modular Python packages (`ai_models/collision/`, `ai_models/dqn/`, `ai_models/drowsiness/`, `ai_models/detection/`, `ai_models/risk/`, `backend/services/`, `backend/routes/`) and frontend asset modules.
- **5-Tier AEBS Collision Avoidance**: Implemented 5 safety tiers (`SAFE`, `CAUTION`, `WARNING`, `CRITICAL`, `EMERGENCY`) with Time-To-Collision (TTC) and Intelligent Driver Model (IDM) stopping distance formulas.
- **DQN Reinforcement Learning Agent**: StateEncoder normalized 16-element vector, 3-layer neural network forward policy, experience replay memory buffer, multi-factor reward function, and explainable AI (XAI) output.
- **Unified Risk Engine**: 0–100 risk score calculation with explicit top contributor breakdown.
- **12 Indian Road Scenarios**: Highway, Urban, Village, Monsoon, Fog, Night, Wrong-side vehicle, Stray cattle, Pedestrians, Potholes, Ambulances, and Aggressive drivers.
- **Automated Research Benchmark Runner**: Multi-run evaluation mode measuring collision rate, mean TTC, emergency braking count, and overall safety scores.
- **Automated Unit & Integration Test Suite**: 100% passing `pytest` test suite (`tests/test_aebs.py`, `tests/test_dqn.py`, `tests/test_risk_engine.py`, `tests/test_drowsiness.py`, `tests/test_api.py`).
- **Research Control Center UI**: Glassmorphism control dashboard (`frontend/index.html`) with XAI panel, live telemetry, speedometer ring, and hazard controls.
- **Backward Compatibility**: Fully preserved existing Flask endpoints (`/health`, `/api/decide`, `/api/analytics`) and legacy standalone browser launcher (`frontend/simulation.html`).
