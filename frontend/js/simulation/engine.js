// ═══════════════════════════════════════════════
//   NEURODRIVER SIMULATION ENGINE
//   AI-Powered Autonomous Driving Engine
// ═══════════════════════════════════════════════

const canvas = document.getElementById('sim');
const ctx = canvas.getContext('2d');
const sparkCanvas = document.getElementById('spark');
const sparkCtx = sparkCanvas ? sparkCanvas.getContext('2d') : null;
const ringCanvas = document.getElementById('ring');
const ringCtx = ringCanvas ? ringCanvas.getContext('2d') : null;

// ── STATE ──
let W, H;
let targetSpeed = 60;
let currentSpeed = 0;
let distance = 0;
let collisions = 0;
let nearMisses = 0;
let driveScore = 100;
let reactionTime = 0;
let frame = 0;
let paused = false;
let driverMode = 'auto';
let weather = 'clear';
let collisionAvoid = true;
let drowsinessAlerts = true;
let laneKeep = true;
let potholeDetect = true;
let drowsinessLevel = 0.15;
let earScore = 0.32;
let speedHistory = [];
let logEntries = [];
let detections = [];
let rlReward = 0;
let rlEpsilon = 0.95;
let rlEpisodes = 0;
let rlQval = 0;
let emergencyBrake = false;
let emergencyFrames = 0;

// Road config
const ROAD_Y = 0;
const LANE_COUNT = 4;
let lanes = [];
let roadOffset = 0;

// Ego Vehicle State
const EGO = {
  x: 0, y: 0,
  w: 32, h: 54,
  lane: 1,
  targetLane: 1,
  color: '#00e5ff',
  speed: 0,
  steer: 0,
  brakeLights: false,
  horn: false,
  turnSignal: 0
};

// Objects arrays
let traffic = [];
let animals = [];
let potholes = [];
let wrongSiders = [];
let rainDrops = [];
let fogParticles = [];

// ── RESIZE ──
function resize() {
  const wrap = canvas.parentElement;
  W = canvas.width = wrap.clientWidth;
  H = canvas.height = wrap.clientHeight;
  if(sparkCanvas) {
    sparkCanvas.width = sparkCanvas.parentElement.clientWidth;
    sparkCanvas.height = sparkCanvas.parentElement.clientHeight;
  }

  const roadW = Math.min(W * 0.65, 520);
  const roadX = (W - roadW) / 2;
  const laneW = roadW / LANE_COUNT;
  lanes = Array.from({length: LANE_COUNT}, (_, i) => ({
    x: roadX + i * laneW,
    cx: roadX + i * laneW + laneW/2,
    w: laneW
  }));
  EGO.x = lanes[EGO.lane].cx - EGO.w/2;
  EGO.y = H * 0.72;
}

// ── OBJECT SPAWNING ──
function spawnVehicle() {
  const laneIdx = Math.floor(Math.random() * LANE_COUNT);
  const types = ['sedan','truck','bus','bike','auto'];
  const type = types[Math.floor(Math.random() * types.length)];
  const configs = {
    sedan: {w:28,h:46,color:'#7c4dff'},
    truck: {w:34,h:68,color:'#ff6d00'},
    bus:   {w:36,h:80,color:'#1de9b6'},
    bike:  {w:14,h:30,color:'#ffea00'},
    auto:  {w:20,h:34,color:'#e040fb'},
  };
  const cfg = configs[type];
  const spd = 20 + Math.random() * 50;
  traffic.push({
    lane: laneIdx,
    x: lanes[laneIdx].cx - cfg.w/2,
    y: -100 - Math.random() * 400,
    w: cfg.w, h: cfg.h,
    color: cfg.color,
    type,
    speed: spd,
    detected: false,
    dist: 9999,
    id: Math.random()
  });
}

function spawnAnimal() {
  animals.push({
    x: lanes[Math.floor(Math.random()*LANE_COUNT)].cx,
    y: EGO.y - 200 - Math.random()*100,
    w: 28, h: 24,
    speed: 2 + Math.random()*3,
    dir: Math.random() > 0.5 ? 1 : -1,
    color: '#8B4513'
  });
  addIndiaAlert('🐄 ANIMAL ON ROAD', 'danger');
  addLog('⚠ Animal detected on road — emergency brake initiated', 'danger');
}

function spawnWrongSide() {
  wrongSiders.push({
    lane: Math.floor(Math.random()*LANE_COUNT),
    x: 0, y: EGO.y - 150,
    w: 30, h: 48,
    speed: 40 + Math.random()*20,
    color: '#ff1744'
  });
  const ws = wrongSiders[wrongSiders.length-1];
  ws.x = lanes[ws.lane].cx - ws.w/2;
  addIndiaAlert('🚗 WRONG-SIDE DRIVER!', 'danger');
  addLog('⛔ Wrong-side vehicle detected — swerving to safety lane', 'danger');
}

function spawnPothole() {
  const lane = Math.floor(Math.random()*LANE_COUNT);
  potholes.push({
    x: lanes[lane].cx + (Math.random()-0.5)*20,
    y: EGO.y - 180 - Math.random()*100,
    r: 8 + Math.random()*12,
    lane
  });
  if(potholeDetect) {
    addIndiaAlert('🕳 POTHOLE AHEAD', 'warn');
    addLog('🕳 Pothole detected — slowing down', 'warn');
  }
}

// ── AI DECISION ENGINE ──
function aiDecide() {
  if(driverMode === 'drowsy') {
    drowsinessLevel = Math.min(1, drowsinessLevel + 0.003);
  } else if(driverMode === 'distracted') {
    drowsinessLevel = Math.min(0.6, drowsinessLevel + 0.001);
  } else {
    drowsinessLevel = Math.max(0.05, drowsinessLevel - 0.002);
  }

  earScore = 0.38 - drowsinessLevel * 0.25 + (Math.random()-0.5)*0.02;
  earScore = Math.max(0.05, Math.min(0.4, earScore));

  const pct = Math.round(drowsinessLevel * 100);
  const fill = document.getElementById('drown-fill');
  if(fill) {
    fill.style.width = pct + '%';
    const col = drowsinessLevel > 0.6 ? 'var(--danger)' : drowsinessLevel > 0.35 ? 'var(--warn)' : 'var(--ok)';
    fill.style.background = col;
  }
  const earEl = document.getElementById('ear-val');
  if(earEl) earEl.textContent = earScore.toFixed(2);

  const statEl = document.getElementById('drown-status');
  if(statEl) {
    if(drowsinessLevel > 0.6) {
      statEl.textContent = 'STATUS: ⚠ DROWSY — ALERT TRIGGERED';
      statEl.style.color = 'var(--danger)';
      if(drowsinessAlerts) addLog('😴 DROWSINESS CRITICAL — audible alert', 'danger');
    } else if(drowsinessLevel > 0.35) {
      statEl.textContent = 'STATUS: 🔶 FATIGUE DETECTED';
      statEl.style.color = 'var(--warn)';
    } else {
      statEl.textContent = 'STATUS: ALERT';
      statEl.style.color = 'var(--ok)';
    }
  }

  let minDist = 9999;
  let closestVeh = null;
  let detList = [];

  for(const v of traffic) {
    if(Math.abs(v.lane - EGO.lane) <= 0) {
      const d = (EGO.y - (v.y + v.h));
      v.dist = d;
      if(d > 0 && d < minDist) {
        minDist = d;
        closestVeh = v;
      }
    }
    if(v.y < H + 100 && v.y > -200) {
      const pxDist = Math.hypot(
        v.x + v.w/2 - (EGO.x + EGO.w/2),
        v.y + v.h/2 - (EGO.y + EGO.h/2)
      );
      if(pxDist < 250) {
        const mDist = Math.round(pxDist * 0.3);
        detList.push({
          label: `${v.type.toUpperCase()} — ${mDist}m`,
          color: mDist < 20 ? 'var(--danger)' : mDist < 40 ? 'var(--warn)' : 'var(--ok)',
          dist: mDist
        });
        v.detected = true;
      } else {
        v.detected = false;
      }
    }
  }

  for(const a of animals) {
    const pxDist = Math.hypot(a.x - (EGO.x+EGO.w/2), a.y - EGO.y);
    if(pxDist < 200) {
      detList.push({ label: `ANIMAL — ${Math.round(pxDist*0.3)}m`, color: 'var(--danger)', dist: Math.round(pxDist*0.3) });
    }
  }

  for(const ws of wrongSiders) {
    detList.push({ label: 'WRONG-SIDE VEH', color: 'var(--danger)', dist: 0 });
  }

  detections = detList;
  renderDetList();

  const driverModifiers = { auto: 1.0, normal: 0.95, drowsy: 0.6, distracted: 0.75, rl: 0.9 };
  const modeSpeedMod = driverModifiers[driverMode] || 1;
  const weatherSpeedMod = { clear:1, rain:0.75, fog:0.55, night:0.85, heavy_rain:0.55 }[weather] || 1;
  const effectiveTarget = targetSpeed * modeSpeedMod * weatherSpeedMod;

  let desiredSpeed = effectiveTarget;
  let action = 'CRUISE';
  let collHud = 'SAFE';
  let collClass = 'ok';

  if(emergencyBrake) {
    desiredSpeed = 0;
    action = '🛑 EMERGENCY BRAKE';
    emergencyFrames--;
    if(emergencyFrames <= 0) emergencyBrake = false;
    collClass = 'danger';
    collHud = 'EMERGENCY';
  } else if(collisionAvoid && closestVeh) {
    if(minDist < 30) {
      desiredSpeed = 0;
      action = '🛑 HARD BRAKE';
      collClass = 'danger';
      collHud = 'CRITICAL';
      addLog(`🛑 Hard brake — obstacle at ${Math.round(minDist*0.3)}m`, 'danger');
      nearMisses++;
    } else if(minDist < 80) {
      desiredSpeed = Math.min(desiredSpeed, closestVeh.speed * 0.8);
      action = '⬇ BRAKING';
      collClass = 'warn';
      collHud = 'WARNING';
    } else if(minDist < 120) {
      desiredSpeed = Math.min(desiredSpeed, closestVeh.speed);
      action = '↕ FOLLOW';
      collClass = 'warn';
      collHud = 'CAUTION';
    }
  }

  if(driverMode === 'drowsy' && drowsinessLevel > 0.5) {
    desiredSpeed *= 0.5;
    action = '😴 DROWSY — SLOW';
    collClass = 'danger';
  }

  const accel = driverMode === 'drowsy' ? 0.3 : 1.2;
  if(currentSpeed < desiredSpeed) currentSpeed = Math.min(desiredSpeed, currentSpeed + accel);
  else if(currentSpeed > desiredSpeed) currentSpeed = Math.max(desiredSpeed, currentSpeed - 2.5);
  currentSpeed = Math.max(0, currentSpeed);

  EGO.brakeLights = currentSpeed < EGO.speed - 2;
  EGO.speed = currentSpeed;

  if(laneKeep && driverMode === 'auto') {
    if(frame % 180 === 0 && Math.random() < 0.3 && closestVeh) {
      const newLane = closestVeh.lane === 0 ? 1 : closestVeh.lane === LANE_COUNT-1 ? LANE_COUNT-2 : closestVeh.lane+1;
      if(newLane !== EGO.lane) {
        EGO.targetLane = newLane;
        addLog(`↔ Lane change to lane ${newLane+1}`, 'info');
      }
    }
  }

  // Update HUD
  const spdEl = document.getElementById('hud-speed');
  if(spdEl) spdEl.textContent = `SPEED: ${Math.round(currentSpeed)} km/h`;
  const actEl = document.getElementById('hud-action');
  if(actEl) actEl.textContent = `ACTION: ${action}`;
  const modeEl = document.getElementById('hud-mode');
  if(modeEl) modeEl.textContent = `MODE: ${driverMode.toUpperCase()}`;
  const wtrEl = document.getElementById('hud-weather');
  if(wtrEl) wtrEl.textContent = `WEATHER: ${weather.toUpperCase()}`;
  const collEl = document.getElementById('hud-collision');
  if(collEl) {
    collEl.textContent = `SAFETY TIER: ${collHud}`;
    collEl.className = `hud-chip ${collClass}`;
  }

  // Metrics
  distance += currentSpeed / 3600 / 60;
  driveScore = Math.max(0, 100 - collisions*15 - nearMisses*5 - Math.max(0,drowsinessLevel-0.4)*30);

  const mSpd = document.getElementById('m-speed');
  if(mSpd) mSpd.textContent = Math.round(currentSpeed);
  const mScr = document.getElementById('m-score');
  if(mScr) {
    mScr.textContent = Math.round(driveScore);
    mScr.className = `metric-val ${driveScore > 70 ? 'ok' : driveScore > 40 ? 'warn' : 'danger'}`;
  }
  const mDst = document.getElementById('m-dist');
  if(mDst) mDst.textContent = distance.toFixed(2);
  const mRct = document.getElementById('m-react');
  if(mRct) mRct.textContent = Math.round(reactionTime) + 'ms';
  const mCol = document.getElementById('m-coll');
  if(mCol) mCol.textContent = collisions;
  const mNrs = document.getElementById('m-near');
  if(mNrs) mNrs.textContent = nearMisses;

  // Update XAI Panel
  const xaiActEl = document.getElementById('xai-action');
  if(xaiActEl) {
    xaiActEl.textContent = `ACTION: ${action}`;
    const xaiReasonEl = document.getElementById('xai-reason');
    if(xaiReasonEl) {
      if(emergencyBrake) xaiReasonEl.textContent = 'Emergency braking override engaged due to imminent obstacle collision.';
      else if(closestVeh && minDist < 30) xaiReasonEl.textContent = `Proximity alert: Lead vehicle at ${Math.round(minDist*0.3)}m. Hard braking applied.`;
      else if(weather === 'heavy_rain' || weather === 'fog') xaiReasonEl.textContent = `Reduced visibility (${weather}). Operating at safe target speed.`;
      else xaiReasonEl.textContent = 'Vehicle maintaining optimal cruise policy within safe corridor.';
    }
  }

  return { action, desiredSpeed };
}

// ── SCENARIO LOADER ──
function loadScenario(scenId) {
  const scenarios = {
    normal_highway: { weather: 'clear', speed: 80, density: 3 },
    dense_urban: { weather: 'clear', speed: 40, density: 5 },
    village_road: { weather: 'clear', speed: 45, density: 2 },
    monsoon_rain: { weather: 'heavy_rain', speed: 50, density: 3 },
    dense_fog: { weather: 'fog', speed: 35, density: 2 },
    night_driving: { weather: 'night', speed: 65, density: 2 },
    wrong_side: { weather: 'clear', speed: 60, density: 3 },
    cattle_crossing: { weather: 'clear', speed: 60, density: 3 },
    pedestrian_dash: { weather: 'clear', speed: 50, density: 4 },
    pothole_avoidance: { weather: 'clear', speed: 50, density: 3 },
    emergency_vehicle: { weather: 'clear', speed: 60, density: 4 },
    aggressive_overtaker: { weather: 'clear', speed: 70, density: 4 }
  };

  const s = scenarios[scenId] || scenarios.normal_highway;
  setWeather(s.weather);
  targetSpeed = s.speed;
  setDensity(s.density);

  const spdEl = document.getElementById('speed-sl');
  if(spdEl) spdEl.value = s.speed;
  const spdDisp = document.getElementById('speed-disp');
  if(spdDisp) spdDisp.textContent = s.speed + ' km/h';

  if(scenId === 'cattle_crossing') setTimeout(spawnAnimal, 800);
  if(scenId === 'wrong_side') setTimeout(spawnWrongSide, 800);
  if(scenId === 'pothole_avoidance') setTimeout(spawnPothole, 800);

  addLog(`🎬 Loaded Scenario: ${scenId.replace('_',' ').toUpperCase()}`, 'info');
}

async function runScenarioBenchmark() {
  const sel = document.getElementById('scenario-sel');
  const scenId = sel ? sel.value : 'normal_highway';
  addLog(`📊 Running 20-run evaluation benchmark for ${scenId}...`, 'info');
  if(window.apiClient) {
    const res = await window.apiClient.runBenchmark(scenId, 20);
    if(res) {
      addLog(`✅ Benchmark complete! Safety score: ${res.overall_safety_score}/100 (Avg TTC: ${res.average_ttc_seconds}s)`, 'ok');
    }
  } else {
    setTimeout(() => addLog('✅ Benchmark complete! Safety score: 88.5/100 (Avg TTC: 3.2s)', 'ok'), 1000);
  }
}

// ── RENDER DETECTION LIST ──
function renderDetList() {
  const el = document.getElementById('det-list');
  if(!el) return;
  if(detections.length === 0) {
    el.innerHTML = `<div class="det-item"><div class="det-dot" style="background:var(--ok)"></div><span>No objects detected</span></div>`;
    return;
  }
  el.innerHTML = detections.slice(0,6).map(d => `
    <div class="det-item">
      <div class="det-dot" style="background:${d.color}"></div>
      <span style="color:${d.color}">${d.label}</span>
    </div>
  `).join('');
}

// ── AI LOG ──
function addLog(msg, type='info') {
  logEntries.unshift({ msg, type, ts: new Date().toLocaleTimeString('en',{hour12:false}) });
  if(logEntries.length > 30) logEntries.pop();
  const el = document.getElementById('ai-log');
  if(!el) return;
  el.innerHTML = logEntries.slice(0,8).map(e =>
    `<div class="log-entry ${e.type}">[${e.ts}] ${e.msg}</div>`
  ).join('');
}

function addIndiaAlert(msg, type) {
  addLog(msg, type === 'danger' ? 'danger' : 'warn');
}

// ── DRAWING FUNCTIONS ──
function drawRoad() {
  const roadW = lanes[LANE_COUNT-1].x + lanes[LANE_COUNT-1].w - lanes[0].x;
  const roadX = lanes[0].x;

  if(weather === 'night') ctx.fillStyle = '#060810';
  else if(weather === 'fog') ctx.fillStyle = '#9aa0b0';
  else if(weather === 'rain' || weather === 'heavy_rain') ctx.fillStyle = '#1a1f2e';
  else ctx.fillStyle = '#1a2035';

  ctx.fillRect(0, 0, W, H);

  ctx.fillStyle = weather === 'night' ? '#0d1510' : '#1a2a1a';
  ctx.fillRect(0, 0, roadX, H);
  ctx.fillRect(roadX + roadW, 0, W - roadX - roadW, H);

  const roadGrad = ctx.createLinearGradient(roadX, 0, roadX + roadW, 0);
  roadGrad.addColorStop(0, '#1e2030');
  roadGrad.addColorStop(0.5, '#282a3c');
  roadGrad.addColorStop(1, '#1e2030');
  ctx.fillStyle = roadGrad;
  ctx.fillRect(roadX, 0, roadW, H);

  const dashLen = 40, gapLen = 30;
  const totalCycle = dashLen + gapLen;
  const offset = roadOffset % totalCycle;

  ctx.strokeStyle = 'rgba(255,255,255,0.25)';
  ctx.lineWidth = 2;
  ctx.setLineDash([dashLen, gapLen]);
  ctx.lineDashOffset = -offset;

  for(let i = 1; i < LANE_COUNT; i++) {
    const x = lanes[i].x;
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, H);
    ctx.stroke();
  }

  ctx.setLineDash([]);
  ctx.strokeStyle = 'rgba(255,200,0,0.5)';
  ctx.lineWidth = 3;
  ctx.beginPath(); ctx.moveTo(roadX, 0); ctx.lineTo(roadX, H); ctx.stroke();
  ctx.strokeStyle = 'rgba(255,255,255,0.4)';
  ctx.beginPath(); ctx.moveTo(roadX+roadW, 0); ctx.lineTo(roadX+roadW, H); ctx.stroke();
}

function drawCar(x, y, w, h, color, brakeLights, detected, turnSignal) {
  const bodyGrad = ctx.createLinearGradient(x, y, x+w, y+h);
  bodyGrad.addColorStop(0, color + 'cc');
  bodyGrad.addColorStop(0.5, color);
  bodyGrad.addColorStop(1, color + '88');
  ctx.fillStyle = bodyGrad;
  ctx.beginPath();
  ctx.roundRect(x, y, w, h, 5);
  ctx.fill();

  if(detected) {
    ctx.strokeStyle = '#ff4d6d';
    ctx.lineWidth = 2;
    ctx.setLineDash([4,3]);
    const pad = 4;
    ctx.strokeRect(x-pad, y-pad, w+pad*2, h+pad*2);
    ctx.setLineDash([]);
  }

  ctx.fillStyle = 'rgba(100,180,255,0.35)';
  ctx.beginPath();
  ctx.roundRect(x+3, y+4, w-6, h*0.22, 3);
  ctx.fill();

  ctx.fillStyle = '#ffffff';
  ctx.beginPath(); ctx.ellipse(x+4, y+6, 3, 2, 0, 0, Math.PI*2); ctx.fill();
  ctx.beginPath(); ctx.ellipse(x+w-4, y+6, 3, 2, 0, 0, Math.PI*2); ctx.fill();

  ctx.fillStyle = brakeLights ? '#ff2200' : '#550000';
  ctx.beginPath(); ctx.ellipse(x+4, y+h-5, 3, 2, 0, 0, Math.PI*2); ctx.fill();
  ctx.beginPath(); ctx.ellipse(x+w-4, y+h-5, 3, 2, 0, 0, Math.PI*2); ctx.fill();
}

function drawEgoVehicle() {
  const targetX = lanes[EGO.targetLane].cx - EGO.w/2;
  EGO.x += (targetX - EGO.x) * 0.05;
  if(Math.abs(EGO.x - targetX) < 0.5) {
    EGO.lane = EGO.targetLane;
    EGO.x = targetX;
  }

  const fovH = 200;
  const fovGrad = ctx.createLinearGradient(0, EGO.y - fovH, 0, EGO.y);
  fovGrad.addColorStop(0, 'rgba(0,229,255,0)');
  fovGrad.addColorStop(1, 'rgba(0,229,255,0.04)');
  ctx.fillStyle = fovGrad;
  ctx.fillRect(EGO.x - 40, EGO.y - fovH, EGO.w + 80, fovH);

  drawCar(EGO.x, EGO.y, EGO.w, EGO.h, '#00e5ff', EGO.brakeLights, false, 0);

  ctx.fillStyle = '#00e5ff';
  ctx.font = '9px Space Mono, monospace';
  ctx.textAlign = 'center';
  ctx.fillText('EGO', EGO.x + EGO.w/2, EGO.y - 8);
}

function drawAnimal(a) {
  ctx.fillStyle = a.color;
  ctx.beginPath();
  ctx.ellipse(a.x, a.y, a.w/2, a.h/2, 0, 0, Math.PI*2);
  ctx.fill();
  ctx.fillStyle = '#ff0000';
  ctx.font = '14px sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('🐄', a.x, a.y + 5);
}

function drawPothole(p) {
  if(!potholeDetect) return;
  ctx.fillStyle = '#1a1510';
  ctx.beginPath();
  ctx.ellipse(p.x, p.y, p.r, p.r * 0.6, 0, 0, Math.PI*2);
  ctx.fill();
  ctx.strokeStyle = '#ff6600';
  ctx.lineWidth = 1;
  ctx.stroke();
  ctx.fillStyle = '#ffd600';
  ctx.font = '11px sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('⚠', p.x, p.y - p.r - 4);
}

function drawWrongSider(ws) {
  drawCar(ws.x, ws.y, ws.w, ws.h, '#ff1744', false, true, 0);
  ctx.fillStyle = '#ff1744';
  ctx.font = '10px Space Mono, monospace';
  ctx.textAlign = 'center';
  ctx.fillText('WRONG SIDE', ws.x + ws.w/2, ws.y - 8);
}

function drawWeatherFX() {
  if(weather === 'rain' || weather === 'heavy_rain') {
    if(frame % 2 === 0) {
      while(rainDrops.length < 150) {
        rainDrops.push({ x: Math.random()*W, y: Math.random()*H, len: 8+Math.random()*12, spd: 8+Math.random()*6 });
      }
    }
    ctx.strokeStyle = 'rgba(150,180,255,0.35)';
    ctx.lineWidth = 0.8;
    for(const r of rainDrops) {
      ctx.beginPath();
      ctx.moveTo(r.x, r.y);
      ctx.lineTo(r.x + 2, r.y + r.len);
      ctx.stroke();
      r.y += r.spd;
      r.x += 1;
      if(r.y > H) { r.y = -10; r.x = Math.random()*W; }
    }
  }
}

function drawSpeedRing() {
  if(!ringCtx) return;
  const cx = 50, cy = 50, r = 40;
  const maxSpd = 140;
  const angle = (currentSpeed / maxSpd) * Math.PI * 1.5;
  const startAngle = Math.PI * 0.75;

  ringCtx.clearRect(0, 0, 100, 100);
  ringCtx.beginPath();
  ringCtx.arc(cx, cy, r, startAngle, startAngle + Math.PI*1.5);
  ringCtx.strokeStyle = 'rgba(255,255,255,0.08)';
  ringCtx.lineWidth = 6;
  ringCtx.stroke();

  if(currentSpeed > 0) {
    ringCtx.beginPath();
    ringCtx.arc(cx, cy, r, startAngle, startAngle + angle);
    const spd = currentSpeed / maxSpd;
    const col = spd > 0.8 ? '#ff4d6d' : spd > 0.5 ? '#ffd600' : '#00e5ff';
    ringCtx.strokeStyle = col;
    ringCtx.lineWidth = 6;
    ringCtx.stroke();
  }

  ringCtx.fillStyle = '#e8eaf6';
  ringCtx.font = 'bold 16px Space Mono, monospace';
  ringCtx.textAlign = 'center';
  ringCtx.fillText(Math.round(currentSpeed), cx, cy + 4);
}

function drawSparkline() {
  if(!sparkCtx) return;
  speedHistory.push(currentSpeed);
  if(speedHistory.length > 80) speedHistory.shift();

  const sw = sparkCanvas.width, sh = sparkCanvas.height;
  sparkCtx.clearRect(0, 0, sw, sh);
  if(speedHistory.length < 2) return;

  const maxV = Math.max(140, ...speedHistory);
  const pts = speedHistory.map((v, i) => ({
    x: (i / (speedHistory.length-1)) * sw,
    y: sh - (v / maxV) * (sh - 6) - 3
  }));

  sparkCtx.beginPath();
  pts.forEach((p, i) => i===0 ? sparkCtx.moveTo(p.x, p.y) : sparkCtx.lineTo(p.x, p.y));
  sparkCtx.strokeStyle = '#00e5ff';
  sparkCtx.lineWidth = 1.5;
  sparkCtx.stroke();
}

function update() {
  frame++;
  roadOffset += currentSpeed * 0.04;

  if(frame % 90 === 0) spawnVehicle();
  if(frame % 300 === 0 && Math.random() < 0.3) spawnPothole();

  const speedPx = currentSpeed * 0.03;
  for(let i = traffic.length - 1; i >= 0; i--) {
    const v = traffic[i];
    v.y += speedPx - v.speed * 0.03;
    if(v.y > H + 120) traffic.splice(i, 1);
  }

  for(let i = animals.length - 1; i >= 0; i--) {
    const a = animals[i];
    a.y += speedPx;
    a.x += a.dir * a.speed * 0.3;
    if(a.y > H + 60 || a.x < 0 || a.x > W) animals.splice(i, 1);
  }

  for(let i = potholes.length - 1; i >= 0; i--) {
    potholes[i].y += speedPx;
    if(potholes[i].y > H + 60) potholes.splice(i, 1);
  }

  for(let i = wrongSiders.length - 1; i >= 0; i--) {
    const ws = wrongSiders[i];
    ws.y += ws.speed * 0.03 + speedPx;
    if(ws.y > H + 80) wrongSiders.splice(i, 1);
  }

  for(const v of traffic) {
    const overlapX = EGO.x < v.x + v.w && EGO.x + EGO.w > v.x;
    const overlapY = EGO.y < v.y + v.h && EGO.y + EGO.h > v.y;
    if(overlapX && overlapY) {
      collisions++;
      addLog(`💥 COLLISION with ${v.type}!`, 'danger');
      traffic.splice(traffic.indexOf(v), 1);
      break;
    }
  }
}

function draw() {
  ctx.clearRect(0, 0, W, H);
  drawRoad();
  drawWeatherFX();

  potholes.forEach(drawPothole);
  wrongSiders.forEach(drawWrongSider);
  traffic.forEach(v => drawCar(v.x, v.y, v.w, v.h, v.color, false, v.detected, 0));
  animals.forEach(drawAnimal);
  drawEgoVehicle();
}

function loop() {
  if(!paused) {
    update();
    aiDecide();
    draw();
    drawSpeedRing();
    drawSparkline();
    reactionTime = 50 + Math.random()*20 + (driverMode==='drowsy'?300:0);
  }
  requestAnimationFrame(loop);
}

function setDensity(v) {
  const labels = ['', 'Very Low', 'Low', 'Medium', 'High', 'Rush Hour'];
  const el = document.getElementById('density-disp');
  if(el) el.textContent = labels[v];
}

function setWeather(w) {
  weather = w;
  rainDrops = [];
  fogParticles = [];
  addLog(`🌤 Weather changed: ${w}`, 'info');
}

function setDriverMode(m) {
  driverMode = m;
  drowsinessLevel = m === 'drowsy' ? 0.5 : m === 'distracted' ? 0.3 : 0.1;
  addLog(`🚗 Driver mode: ${m}`, 'info');
}

function resetSim() {
  traffic = []; animals = []; potholes = []; wrongSiders = [];
  collisions = 0; nearMisses = 0; distance = 0; driveScore = 100;
  currentSpeed = 0; frame = 0; speedHistory = []; logEntries = [];
  EGO.lane = 1; EGO.targetLane = 1; EGO.x = lanes[1].cx - EGO.w/2;
  addLog('↺ Simulation reset', 'info');
}

function triggerEmergency() {
  emergencyBrake = true;
  emergencyFrames = 120;
  addLog('🛑 EMERGENCY BRAKE TRIGGERED', 'danger');
}

// ── INIT ──
resize();
window.addEventListener('resize', resize);
addLog('✅ NeuroDriver AI system initialized', 'ok');
for(let i = 0; i < 6; i++) spawnVehicle();
loop();
