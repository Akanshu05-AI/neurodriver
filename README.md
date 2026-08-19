# NeuroDriver — AI-Powered Autonomous Driving Simulation Platform

> Advanced autonomous driving research, collision avoidance (AEBS), Deep Q-Network (DQN) reinforcement learning, and Explainable AI (XAI) platform tailored for high-risk Indian road environments.

---

## 🌟 Quick Start

### 1. Interactive Control Center (Browser)
Open [`frontend/index.html`](file:///c:/Desktop/Projects/python%20projects/neurodriver/frontend/index.html) or [`frontend/simulation.html`](file:///c:/Desktop/Projects/python%20projects/neurodriver/frontend/simulation.html) directly in any browser.

### 2. Launch Backend API Server
```bash
pip install -r requirements.txt
python backend/app.py   # → http://localhost:5000
```

### 3. Run Automated Test Suite
```bash
python -m pytest -v
```

---

## 📁 Repository Structure

```text
neurodriver/
├── frontend/
│   ├── index.html                 # Research Control Center & Dashboard
│   ├── simulation.html            # Standalone / Legacy compatible simulation
│   ├── css/                       # Modular CSS design system tokens
│   └── js/                        # Modular frontend scripts (API client, config)
├── backend/
│   ├── app.py                     # Flask REST server entrypoint
│   ├── config.py                  # Configuration & safety threshold limits
│   ├── routes/                    # API Blueprint endpoints (decide, health, scenarios, etc.)
│   ├── services/                  # AI engine & scenario benchmark services
│   └── utils/                     # Request validation & numerical guards
├── ai_models/
│   ├── collision/                 # 5-Tier AEBS system (TTC + IDM)
│   ├── dqn/                       # Deep Q-Network Agent & 16-element StateEncoder
│   ├── drowsiness/                # EAR & PERCLOS driver fatigue state machine
│   ├── detection/                 # ObjectDetector interface & Pinhole ranging
│   ├── risk/                      # Unified Risk Engine (0-100 score + top contributors)
│   └── common/                    # Physical constants & safety limits
├── tests/                         # Automated pytest test suite (100% pass)
├── docs/                          # System Architecture & API Specifications
├── requirements.txt               # Dependencies
├── .env.example                   # Environment configuration template
├── README.md                      # Comprehensive documentation
└── CHANGELOG.md                   # Release notes
```

---

## 🧠 AI Modules & Systems

| Module | Architecture / Algorithm | Operational Metric / Threshold |
|---|---|---|
| **Collision Avoidance (AEBS)** | Time-To-Collision (TTC) + IDM Stopping Distance | 5 Tiers: SAFE, CAUTION, WARNING, CRITICAL, EMERGENCY ($\text{TTC} \le 1.0\text{s}$) |
| **DQN RL Agent** | 3-Layer NN ($16 \rightarrow 128 \rightarrow 64 \rightarrow 5$) | Multi-factor reward (Speed match, lane center, crash penalty) |
| **Driver Drowsiness** | Eye Aspect Ratio (EAR) + PERCLOS | 4 States: ALERT, FATIGUED, DROWSY, SEVERE ($\text{EAR} < 0.25$) |
| **Object Detection & Ranging** | Pinhole Distance Ranging ($D = \frac{f \cdot H}{h}$) | Distance estimation for cars, trucks, buses, pedestrians, cattle |
| **Unified Risk Engine** | Weighted multi-factor risk model | 0–100 score with explicit top contributor breakdown |
| **Explainable AI (XAI)** | Decision Explainer | Real-time structured reasoning output for every action |

---

## 🇮🇳 12 Indian Road Safety Scenarios
1. **Normal Highway**: Multi-lane national highway driving.
2. **Dense Urban Traffic**: City congestion with auto-rickshaws, bikes, and stop-and-go.
3. **Village Road**: Rural road with stray cattle and unpaved shoulders.
4. **Monsoon Torrential Rain**: Reduced friction and visibility.
5. **Dense Fog Highway**: Under 40m visibility requiring cautious AEBS operation.
6. **Night Driving**: High-beam glare and low ambient illumination.
7. **Wrong-Side Driver Encounter**: Oncoming vehicle driving in your lane.
8. **Stray Cattle Crossing**: Cow crossing carriageway requiring evasive action.
9. **Sudden Pedestrian Dash**: Jaywalking pedestrian from blind spot.
10. **Pothole Avoidance**: Smooth deceleration and steering adjustments.
11. **Ambulance Priority Yield**: Yielding right-of-way to emergency vehicles.
12. **Aggressive Driver Overtaking**: Vehicle cutting in with minimal clearance.

---

## 📊 API Endpoints

```text
GET  /health                  → Server health & timestamp
POST /api/decide              → AI driving decision & XAI explanation
POST /api/drowsiness          → EAR / PERCLOS fatigue state analysis
POST /api/detect              → Object detection & distance ranging
GET  /api/analytics           → Session statistics
GET  /api/scenarios           → List 12 Indian road scenarios
POST /api/scenarios/benchmark → Automated 20-run evaluation benchmark
GET  /api/telemetry           → Live telemetry stream
```

---

## 🧪 Testing & Verification

All core modules are verified by an automated test suite:
```bash
python -m pytest -v
```
- `tests/test_aebs.py`: 5-tier safety logic & TTC edge cases.
- `tests/test_dqn.py`: State vector encoding & DQN action selection.
- `tests/test_risk_engine.py`: Unified risk bounds & top contributor breakdown.
- `tests/test_drowsiness.py`: EAR/PERCLOS fatigue state machine.
- `tests/test_api.py`: Flask REST API route integration tests.
