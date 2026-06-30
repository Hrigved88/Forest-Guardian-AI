import streamlit as st
import pandas as pd
import requests
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import pickle
import streamlit.components.v1 as components

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Forest Guardian AI", layout="wide", page_icon="🌲")

# --- 2. PARALLAX BG + PARTICLES (height=0, invisible) ---
components.html("""
<!DOCTYPE html>
<html>
<head>
<style>
  html, body { margin: 0; padding: 0; overflow: hidden; background: transparent; }

  #parallax-bg {
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background: radial-gradient(ellipse at 20% 50%, #0d2b1a 0%, #050e07 40%, #020605 100%);
    z-index: -10;
  }
  #forest-layer-far {
    position: fixed; bottom: -20px; left: 0; width: 130%; height: 55%; z-index: -9; opacity: 0.35;
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 400'%3E%3Cpolygon points='0,400 50,200 100,280 150,160 200,240 250,120 300,210 350,140 400,230 450,100 500,200 550,130 600,210 650,90 700,180 750,120 800,200 850,150 900,210 950,80 1000,190 1050,140 1100,220 1150,110 1200,200 1200,400' fill='%230d2b1a'/%3E%3C/svg%3E") repeat-x bottom;
    background-size: 1200px 400px;
  }
  #forest-layer-mid {
    position: fixed; bottom: -10px; left: 0; width: 140%; height: 45%; z-index: -8; opacity: 0.55;
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 350'%3E%3Cpolygon points='0,350 30,180 70,240 110,150 160,220 210,100 260,190 310,130 370,200 420,80 480,170 530,110 590,190 640,70 700,160 760,110 820,170 870,120 930,180 980,60 1040,160 1090,120 1150,180 1200,100 1200,350' fill='%230a2218'/%3E%3C/svg%3E") repeat-x bottom;
    background-size: 1200px 350px;
  }
  #forest-layer-near {
    position: fixed; bottom: 0; left: 0; width: 150%; height: 35%; z-index: -7; opacity: 0.85;
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 300'%3E%3Cpolygon points='0,300 20,150 60,200 100,120 150,180 200,80 250,160 300,100 360,170 410,60 470,150 520,90 580,160 630,50 690,140 750,90 810,150 860,100 920,160 970,40 1030,140 1080,100 1140,160 1200,80 1200,300' fill='%23071a10'/%3E%3C/svg%3E") repeat-x bottom;
    background-size: 1200px 300px;
  }
  #fog-layer {
    position: fixed; bottom: 0; left: 0; width: 100%; height: 30%; z-index: -6;
    background: linear-gradient(to top, rgba(10,25,15,0.6) 0%, transparent 100%);
    animation: fogDrift 12s ease-in-out infinite alternate;
  }
  @keyframes fogDrift {
    0%   { transform: translateX(0) scaleX(1); opacity: 0.4; }
    100% { transform: translateX(-3%) scaleX(1.06); opacity: 0.7; }
  }
  canvas#particles {
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    z-index: -5; pointer-events: none;
  }
</style>
</head>
<body>
  <div id="parallax-bg"></div>
  <div id="forest-layer-far"></div>
  <div id="forest-layer-mid"></div>
  <div id="forest-layer-near"></div>
  <div id="fog-layer"></div>
  <canvas id="particles"></canvas>
<script>
  const canvas = document.getElementById('particles');
  const ctx = canvas.getContext('2d');
  let W, H, particles = [];
  function resize() { W = canvas.width = window.innerWidth; H = canvas.height = window.innerHeight; }
  resize();
  window.addEventListener('resize', resize);
  class Particle {
    constructor() { this.reset(); }
    reset() {
      this.x = Math.random() * W; this.y = H + 10;
      this.size = Math.random() * 2.5 + 0.5;
      this.speedY = -(Math.random() * 0.8 + 0.3);
      this.speedX = (Math.random() - 0.5) * 0.5;
      this.opacity = Math.random() * 0.6 + 0.2;
      this.life = 0; this.maxLife = Math.random() * 300 + 200;
      const r = Math.random();
      if (r < 0.5) this.color = `rgba(255,${140+Math.floor(Math.random()*80)},0,`;
      else if (r < 0.8) this.color = `rgba(0,${200+Math.floor(Math.random()*55)},${100+Math.floor(Math.random()*70)},`;
      else this.color = `rgba(255,255,${200+Math.floor(Math.random()*55)},`;
    }
    update() {
      this.x += this.speedX + Math.sin(this.life * 0.04) * 0.3;
      this.y += this.speedY; this.life++;
      const fade = Math.min(this.life/40,1) * Math.min((this.maxLife-this.life)/60,1);
      this.currentOpacity = this.opacity * Math.max(0, fade);
      if (this.life > this.maxLife) this.reset();
    }
    draw() {
      ctx.beginPath(); ctx.arc(this.x, this.y, this.size, 0, Math.PI*2);
      ctx.fillStyle = this.color + this.currentOpacity + ')'; ctx.fill();
    }
  }
  for (let i = 0; i < 80; i++) {
    const p = new Particle(); p.y = Math.random() * H; p.life = Math.random() * p.maxLife; particles.push(p);
  }
  function animate() { ctx.clearRect(0,0,W,H); particles.forEach(p=>{p.update();p.draw();}); requestAnimationFrame(animate); }
  animate();
  const parentWindow = window.parent || window;
  let lastScroll = 0;
  function applyParallax(scrollY) {
    document.getElementById('forest-layer-far').style.transform = `translateX(${-scrollY*0.08}px)`;
    document.getElementById('forest-layer-mid').style.transform = `translateX(${-scrollY*0.15}px)`;
    document.getElementById('forest-layer-near').style.transform = `translateX(${-scrollY*0.25}px)`;
    document.getElementById('parallax-bg').style.transform = `translateY(${scrollY*0.05}px)`;
    document.getElementById('fog-layer').style.opacity = Math.min(0.4 + scrollY*0.001, 0.9);
  }
  setInterval(() => {
    try {
      const scrollY = parentWindow.scrollY || parentWindow.pageYOffset || 0;
      if (scrollY !== lastScroll) { lastScroll = scrollY; applyParallax(scrollY); }
    } catch(e) {}
  }, 16);
</script>
</body>
</html>
""", height=0)

# --- 3. SPINNING EARTH + FOREST SCENE (Three.js) ---
components.html("""
<!DOCTYPE html>
<html>
<head>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: transparent; overflow: hidden; }
  #three-canvas {
    width: 100%;
    height: 520px;
    display: block;
    background: transparent;
  }
</style>
</head>
<body>
<canvas id="three-canvas"></canvas>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const canvas = document.getElementById('three-canvas');
const W = canvas.offsetWidth || window.innerWidth;
const H = 520;

const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
renderer.setSize(W, H);
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setClearColor(0x000000, 0);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, W / H, 0.1, 1000);
camera.position.set(0, 0, 5);

// --- LIGHTING ---
const ambientLight = new THREE.AmbientLight(0x223322, 1.2);
scene.add(ambientLight);
const sunLight = new THREE.DirectionalLight(0xffeedd, 2.5);
sunLight.position.set(5, 3, 5);
scene.add(sunLight);
const rimLight = new THREE.DirectionalLight(0x004422, 0.8);
rimLight.position.set(-5, -2, -3);
scene.add(rimLight);

// --- EARTH (procedural texture) ---
function makeEarthTexture() {
  const size = 1024;
  const offscreen = document.createElement('canvas');
  offscreen.width = size; offscreen.height = size;
  const c = offscreen.getContext('2d');

  // Ocean base
  c.fillStyle = '#0a2a4a';
  c.fillRect(0, 0, size, size);

  // Atmosphere gradient overlay
  const atmo = c.createLinearGradient(0, 0, 0, size);
  atmo.addColorStop(0, 'rgba(10,60,120,0.4)');
  atmo.addColorStop(0.5, 'rgba(5,30,70,0.1)');
  atmo.addColorStop(1, 'rgba(0,10,40,0.5)');
  c.fillStyle = atmo;
  c.fillRect(0, 0, size, size);

  // Continents (rough procedural shapes)
  const continents = [
    // North America
    { x: 180, y: 200, w: 160, h: 200, rx: 60 },
    // South America
    { x: 240, y: 380, w: 100, h: 180, rx: 40 },
    // Europe
    { x: 490, y: 160, w: 90, h: 100, rx: 30 },
    // Africa
    { x: 490, y: 260, w: 110, h: 200, rx: 45 },
    // Asia
    { x: 570, y: 130, w: 270, h: 220, rx: 70 },
    // Australia
    { x: 730, y: 420, w: 110, h: 80, rx: 35 },
    // Greenland
    { x: 320, y: 80, w: 70, h: 80, rx: 25 },
    // Antarctica
    { x: 0, y: 920, w: 1024, h: 104, rx: 0 },
  ];

  continents.forEach(({ x, y, w, h, rx }) => {
    c.beginPath();
    c.roundRect(x, y, w, h, rx);
    const g = c.createRadialGradient(x+w/2, y+h/2, 0, x+w/2, y+h/2, Math.max(w,h)*0.7);
    g.addColorStop(0, '#2d6a2d');
    g.addColorStop(0.5, '#1a4a1a');
    g.addColorStop(1, '#0f3010');
    c.fillStyle = g;
    c.fill();
  });

  // Ice caps
  c.fillStyle = 'rgba(220,240,255,0.85)';
  c.beginPath(); c.ellipse(512, 30, 300, 60, 0, 0, Math.PI*2); c.fill();
  c.beginPath(); c.ellipse(512, 990, 400, 80, 0, 0, Math.PI*2); c.fill();

  // Ocean shimmer lines
  c.strokeStyle = 'rgba(50,120,200,0.12)';
  c.lineWidth = 1;
  for (let i = 0; i < 20; i++) {
    c.beginPath();
    c.moveTo(0, i * 52);
    c.lineTo(size, i * 52 + 30);
    c.stroke();
  }

  return new THREE.CanvasTexture(offscreen);
}

function makeAtmosphereTexture() {
  const size = 512;
  const off = document.createElement('canvas');
  off.width = size; off.height = size;
  const c = off.getContext('2d');
  const g = c.createRadialGradient(size/2, size/2, size*0.35, size/2, size/2, size/2);
  g.addColorStop(0, 'rgba(0,80,180,0)');
  g.addColorStop(0.7, 'rgba(0,100,200,0.05)');
  g.addColorStop(1, 'rgba(0,150,255,0.35)');
  c.fillStyle = g;
  c.fillRect(0,0,size,size);
  return new THREE.CanvasTexture(off);
}

function makeCloudTexture() {
  const size = 1024;
  const off = document.createElement('canvas');
  off.width = size; off.height = size;
  const c = off.getContext('2d');
  c.fillStyle = 'rgba(0,0,0,0)';
  c.fillRect(0,0,size,size);
  for (let i = 0; i < 80; i++) {
    const x = Math.random() * size;
    const y = Math.random() * size;
    const r = Math.random() * 60 + 20;
    const g = c.createRadialGradient(x,y,0,x,y,r);
    g.addColorStop(0, 'rgba(255,255,255,0.25)');
    g.addColorStop(1, 'rgba(255,255,255,0)');
    c.fillStyle = g;
    c.beginPath(); c.ellipse(x, y, r, r*0.4, Math.random()*Math.PI, 0, Math.PI*2); c.fill();
  }
  return new THREE.CanvasTexture(off);
}

const earthGeo = new THREE.SphereGeometry(1.4, 64, 64);
const earthMat = new THREE.MeshPhongMaterial({
  map: makeEarthTexture(),
  specular: new THREE.Color(0x1a3a6a),
  shininess: 18,
});
const earth = new THREE.Mesh(earthGeo, earthMat);
earth.position.set(-2.2, 0.3, 0);
earth.rotation.x = 0.2;
scene.add(earth);

// Atmosphere glow shell
const atmoGeo = new THREE.SphereGeometry(1.48, 64, 64);
const atmoMat = new THREE.MeshPhongMaterial({
  map: makeAtmosphereTexture(),
  transparent: true, opacity: 0.5,
  side: THREE.FrontSide, depthWrite: false,
});
const atmosphere = new THREE.Mesh(atmoGeo, atmoMat);
atmosphere.position.copy(earth.position);
scene.add(atmosphere);

// Cloud layer
const cloudGeo = new THREE.SphereGeometry(1.43, 64, 64);
const cloudMat = new THREE.MeshPhongMaterial({
  map: makeCloudTexture(),
  transparent: true, opacity: 0.55,
  depthWrite: false,
});
const clouds = new THREE.Mesh(cloudGeo, cloudMat);
clouds.position.copy(earth.position);
scene.add(clouds);

// --- FOREST SCENE (right side) ---
const forestGroup = new THREE.Group();
forestGroup.position.set(2.2, -0.8, 0);
scene.add(forestGroup);

// Ground plane
const groundGeo = new THREE.PlaneGeometry(4, 2);
const groundMat = new THREE.MeshPhongMaterial({ color: 0x0a1f0d });
const ground = new THREE.Mesh(groundGeo, groundMat);
ground.rotation.x = -Math.PI / 2;
ground.position.y = -0.5;
forestGroup.add(ground);

// Tree generator
function makeTree(x, z, scale, darkFactor) {
  const treeGroup = new THREE.Group();
  treeGroup.position.set(x, -0.5, z);

  const trunkH = 0.18 * scale;
  const trunkGeo = new THREE.CylinderGeometry(0.025*scale, 0.04*scale, trunkH, 6);
  const trunkMat = new THREE.MeshPhongMaterial({ color: new THREE.Color(0.2*darkFactor, 0.12*darkFactor, 0.06*darkFactor) });
  const trunk = new THREE.Mesh(trunkGeo, trunkMat);
  trunk.position.y = trunkH / 2;
  treeGroup.add(trunk);

  const layers = 3;
  for (let i = 0; i < layers; i++) {
    const r = (0.22 - i * 0.055) * scale;
    const h = (0.28 - i * 0.04) * scale;
    const coneGeo = new THREE.ConeGeometry(r, h, 7);
    const brightness = darkFactor * (0.5 + i * 0.12);
    const coneMat = new THREE.MeshPhongMaterial({
      color: new THREE.Color(0.04*brightness, 0.22*brightness, 0.07*brightness),
      shininess: 5,
    });
    const cone = new THREE.Mesh(coneGeo, coneMat);
    cone.position.y = trunkH + h/2 + i * (h * 0.45);
    treeGroup.add(cone);
  }
  return treeGroup;
}

// Place trees in multiple depth rows
const treeData = [
  [-0.9,-0.3,1.0,1.0], [-0.5,-0.5,0.85,0.9], [0.0,-0.4,1.1,1.0],
  [0.4,-0.5,0.9,0.85], [0.8,-0.3,1.0,1.0],   [1.1,-0.5,0.8,0.8],
  [-1.2,-0.1,0.7,0.7], [-0.7,-0.1,0.75,0.75], [0.2,-0.1,0.7,0.7],
  [0.7,-0.1,0.8,0.75], [1.3,-0.2,0.65,0.65],
  [-1.0, 0.2,0.55,0.6], [-0.3, 0.15,0.6,0.6], [0.5, 0.2,0.55,0.55],
  [1.1, 0.1,0.5,0.55],
];
treeData.forEach(([x, z, scale, dark]) => {
  forestGroup.add(makeTree(x, z, scale, dark));
});

// Fireflies in the forest
const fireflyCount = 30;
const fireflyGeo = new THREE.BufferGeometry();
const fireflyPositions = new Float32Array(fireflyCount * 3);
const fireflyBaseY = [];
for (let i = 0; i < fireflyCount; i++) {
  fireflyPositions[i*3]   = (Math.random() - 0.5) * 3;
  fireflyPositions[i*3+1] = Math.random() * 0.8;
  fireflyPositions[i*3+2] = (Math.random() - 0.5) * 1.5;
  fireflyBaseY.push(fireflyPositions[i*3+1]);
}
fireflyGeo.setAttribute('position', new THREE.BufferAttribute(fireflyPositions, 3));
const fireflyMat = new THREE.PointsMaterial({ color: 0x00ffaa, size: 0.025, transparent: true, opacity: 0.8 });
const fireflies = new THREE.Points(fireflyGeo, fireflyMat);
forestGroup.add(fireflies);

// --- STARS ---
const starGeo = new THREE.BufferGeometry();
const starPositions = new Float32Array(600 * 3);
for (let i = 0; i < 600; i++) {
  starPositions[i*3]   = (Math.random() - 0.5) * 80;
  starPositions[i*3+1] = (Math.random() - 0.5) * 40;
  starPositions[i*3+2] = -20 + Math.random() * -10;
}
starGeo.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));
const starMat = new THREE.PointsMaterial({ color: 0xaaffcc, size: 0.06, transparent: true, opacity: 0.5 });
scene.add(new THREE.Points(starGeo, starMat));

// --- ANIMATION LOOP ---
let t = 0;
function animate() {
  requestAnimationFrame(animate);
  t += 0.005;

  earth.rotation.y += 0.003;
  clouds.rotation.y += 0.0035;
  atmosphere.rotation.y += 0.001;

  // Firefly bob
  const pos = fireflies.geometry.attributes.position;
  for (let i = 0; i < fireflyCount; i++) {
    pos.array[i*3+1] = fireflyBaseY[i] + Math.sin(t * 2 + i) * 0.06;
    pos.array[i*3]  += Math.sin(t + i * 0.5) * 0.002;
  }
  pos.needsUpdate = true;
  fireflyMat.opacity = 0.5 + Math.sin(t * 3) * 0.3;

  // Gentle forest sway
  forestGroup.rotation.y = Math.sin(t * 0.3) * 0.015;

  renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
  const nW = canvas.offsetWidth || window.innerWidth;
  camera.aspect = nW / H;
  camera.updateProjectionMatrix();
  renderer.setSize(nW, H);
});
</script>
</body>
</html>
""", height=540)

# --- 4. STREAMLIT CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Inter:wght@400;600&display=swap');

.stApp { background: transparent !important; color: #e0e6ed; font-family: 'Inter', sans-serif; }
[data-testid="stAppViewContainer"] { background: transparent !important; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { background: transparent !important; }
section[data-testid="stSidebar"] { background: rgba(5,14,7,0.85) !important; }
.block-container { background: transparent !important; }

h1, h2, h3, h4 {
    font-family: 'Cinzel', serif !important;
    color: #ffffff !important;
    text-shadow: 0 2px 10px rgba(0,0,0,0.5);
}
[data-testid="stMetricValue"] {
    color: #00ffaa !important; font-size: 2.2rem !important;
    font-weight: 800 !important; text-shadow: 0 0 10px rgba(0,255,170,0.3);
}
[data-testid="stMetricLabel"] { color: #8fa499 !important; font-size: 1.1rem !important; font-weight: 500 !important; }
div[data-testid="stMetric"] {
    background: rgba(16,26,21,0.6) !important;
    border: 1px solid rgba(76,110,94,0.3) !important;
    border-radius: 8px !important; padding: 15px !important;
    backdrop-filter: blur(10px) !important;
}
.critical-alert {
    background: rgba(102,17,17,0.45) !important; border-left: 6px solid #ff3333 !important;
    border-top: 1px solid rgba(255,51,51,0.3); border-right: 1px solid rgba(255,51,51,0.3);
    border-bottom: 1px solid rgba(255,51,51,0.3); padding: 20px !important;
    border-radius: 0 8px 8px 0 !important; margin-bottom: 15px !important;
    box-shadow: 0 0 15px rgba(255,51,51,0.15) !important;
}
.high-risk {
    background: rgba(102,68,17,0.45) !important; border-left: 6px solid #ff9900 !important;
    border-top: 1px solid rgba(255,153,0,0.3); border-right: 1px solid rgba(255,153,0,0.3);
    border-bottom: 1px solid rgba(255,153,0,0.3); padding: 20px !important;
    border-radius: 0 8px 8px 0 !important; margin-bottom: 15px !important;
    box-shadow: 0 0 15px rgba(255,153,0,0.15) !important;
}
hr { border-color: rgba(76,110,94,0.3) !important; }
.stTabs [data-testid="baseButton-secondary"] {
    background-color: rgba(16,26,21,0.5) !important;
    color: #00ffaa !important; border: 1px solid rgba(76,110,94,0.4) !important;
}
</style>
""", unsafe_allow_html=True)

# --- 5. LIVE WEATHER API ---
@st.cache_data(ttl=900)
def fetch_live_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m&temperature_unit=celsius&wind_speed_unit=mph"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "temp": data['current']['temperature_2m'],
                "humidity": data['current']['relative_humidity_2m'],
                "wind": data['current']['wind_speed_10m']
            }
    except Exception as e:
        st.sidebar.error(f"Weather API Error: {e}")
    return {"temp": 17.1, "humidity": 32.0, "wind": 5.1}

live_weather = fetch_live_weather(38.0124, -120.1234)

# --- 6. DATABASE CONNECTION ---
@st.cache_resource
def init_connection():
    try:
        db_password = 'YOUR_DB_PASSWORD_HERE'  # swap to st.secrets["db_password"] before GitHub push
        url_object = URL.create(
            "postgresql", username="postgres", password=db_password,
            host="localhost", port=5432, database="forest_guardian"
        )
        return create_engine(url_object)
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        st.stop()

engine = init_connection()

@st.cache_data(ttl=600)
def load_data():
    return pd.read_sql("SELECT * FROM sectors;", engine)

df_sectors = load_data()

# --- 7. LOAD ML MODEL ---
@st.cache_resource
def load_ml_model():
    try:
        with open('xgboost_fire_model.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        st.error("ML model file not found.")
        st.stop()

xgb_model = load_ml_model()

# --- 8. API DATA BUNDLE ---
api_data = {
    "source": "Open-Meteo API & PostgreSQL Backend",
    "target_forest": "Stanislaus National Forest",
    "live_conditions": {
        "ambient_temperature_c": live_weather["temp"],
        "relative_humidity_pct": live_weather["humidity"],
        "wind_speed_mph": live_weather["wind"],
        "wind_direction_cardinal": "Variable",
        "active_thermal_hotspots": [{"nearest_sector_id": "SEC-043", "intensity_frp_mw": 45.2}]
    }
}

# --- 9. AGENT ---
class ForestGuardianAgent:
    def __init__(self, static_terrain, live_api, ai_model):
        self.df = static_terrain
        self.live = live_api["live_conditions"]
        self.model = ai_model

    def calculate_wildfire_risk(self):
        temp = self.live["ambient_temperature_c"]
        rh = self.live["relative_humidity_pct"]
        wind = self.live["wind_speed_mph"]
        hotspot_sectors = [h["nearest_sector_id"] for h in self.live["active_thermal_hotspots"]]
        risks = []
        for _, row in self.df.iterrows():
            is_hotspot = 1 if row['Sector_ID'] in hotspot_sectors else 0
            live_features = pd.DataFrame([{
                "Tree_Density_Pct": row['Tree_Density_Pct'],
                "Fuel_Moisture_Content_Pct": row['Fuel_Moisture_Content_Pct'],
                "Slope_Steepness_Deg": row['Slope_Steepness_Deg'],
                "Temperature_C": temp, "Humidity_Pct": rh, "Wind_Speed_MPH": wind,
                "Active_Hotspot": is_hotspot
            }])
            fire_probability = self.model.predict_proba(live_features)[0][1]
            risks.append({
                "Sector ID": row['Sector_ID'], "Zone Name": row['Zone_Name'],
                "Vegetation": row['Primary_Vegetation_Type'],
                "Risk Score": round(fire_probability * 100, 1),
                "latitude": row['Latitude'], "longitude": row['Longitude']
            })
        return pd.DataFrame(risks).sort_values(by="Risk Score", ascending=False)

# --- 10. RENDER DASHBOARD ---
st.title("Forest Guardian Tactical Dashboard")
st.markdown(f"**Target Area:** `{api_data['target_forest']}` | **Live Feed:** `{api_data['source']}`")
st.divider()

guardian = ForestGuardianAgent(df_sectors, api_data, xgb_model)
risk_df = guardian.calculate_wildfire_risk()

st.subheader("Live Environmental Telemetry")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Temperature", f"{api_data['live_conditions']['ambient_temperature_c']} °C")
with col2:
    st.metric("Relative Humidity", f"{api_data['live_conditions']['relative_humidity_pct']} %")
with col3:
    st.metric("Wind Speed", f"{api_data['live_conditions']['wind_speed_mph']} MPH")
with col4:
    st.metric("Wind Direction", api_data['live_conditions']['wind_direction_cardinal'])

st.divider()

tab1, tab2 = st.tabs(["🗺️ Tactical Map & Alerts", "📊 ML Analytics Breakdown"])

with tab1:
    st.subheader("Live Sector Risk Map (AI Predicted)")
    st.map(risk_df, color="#00ffaa", size=250, zoom=9)
    st.caption("🟢 Green markers represent monitored sector coordinates.")
    st.divider()

    st.subheader("Active Ranger Dispatch Alerts")
    critical_sectors = risk_df[risk_df["Risk Score"] >= 85]
    high_sectors = risk_df[(risk_df["Risk Score"] >= 70) & (risk_df["Risk Score"] < 85)]

    if critical_sectors.empty and high_sectors.empty:
        st.info("No immediate threats detected. Status: GREEN.")

    for _, row in critical_sectors.iterrows():
        st.markdown(f"""
        <div class="critical-alert">
            <h4 style="margin:0;color:#ff3333;font-family:'Inter',sans-serif;">🔴 CRITICAL — Confidence: {row['Risk Score']:.1f}%</h4>
            <hr style="margin:10px 0;">
            <strong>Sector:</strong> {row['Sector ID']} &nbsp;|&nbsp; <strong>Zone:</strong> {row['Zone Name']}<br>
            <strong>Vegetation:</strong> {row['Vegetation']}<br><br>
            <strong>Action:</strong> Dispatch patrol trucks immediately.
        </div>
        """, unsafe_allow_html=True)

    for _, row in high_sectors.iterrows():
        st.markdown(f"""
        <div class="high-risk">
            <h4 style="margin:0;color:#ff9900;font-family:'Inter',sans-serif;">🟠 HIGH RISK — Confidence: {row['Risk Score']:.1f}%</h4>
            <hr style="margin:10px 0;">
            <strong>Sector:</strong> {row['Sector ID']} &nbsp;|&nbsp; <strong>Zone:</strong> {row['Zone Name']}<br>
            <strong>Vegetation:</strong> {row['Vegetation']}<br><br>
            <strong>Action:</strong> Pre-position suppression assets.
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.subheader("Sector Probability Distribution")
    st.caption("XGBoost inference over live telemetry.")
    for _, row in risk_df.iterrows():
        score = row['Risk Score']
        text_col, bar_col = st.columns([1, 2])
        with text_col:
            st.write(f"**{row['Sector ID']}** - {row['Zone Name']}")
            st.caption(f"Vegetation: {row['Vegetation']}")
        with bar_col:
            st.progress(int(score), text=f"AI Fire Probability: {score:.1f}%")
        st.divider()