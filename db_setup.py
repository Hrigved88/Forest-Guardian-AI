import streamlit as st
import pandas as pd
import requests 
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

# --- 1. PAGE CONFIG & CUSTOM CSS ---
st.set_page_config(page_title="Forest Guardian AI", layout="wide", page_icon="🌲")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #c9d1d9; }
    [data-testid="stMetricValue"] { color: #00ffcc !important; font-size: 2rem !important; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #8b949e !important; font-size: 1rem !important; }
    .critical-alert { background-color: #3b0000; border-left: 5px solid #ff4b4b; padding: 15px; border-radius: 5px; margin-bottom: 10px; }
    .high-risk { background-color: #332100; border-left: 5px solid #ffa421; padding: 15px; border-radius: 5px; margin-bottom: 10px; }
    hr { border-color: #30363d !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. LIVE API EXTRACTION ---
@st.cache_data(ttl=900) 
def fetch_live_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m&temperature_unit=celsius&wind_speed_unit=mph"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return {
                "temp": data['current']['temperature_2m'],
                "humidity": data['current']['relative_humidity_2m'],
                "wind": data['current']['wind_speed_10m']
            }
    except Exception as e:
        st.sidebar.error(f"Weather API Error: {e}")
    return {"temp": 25.0, "humidity": 30.0, "wind": 10.0}

live_weather = fetch_live_weather(38.0124, -120.1234)

# --- 3. DATABASE CONNECTION (The Backend Upgrade) ---
@st.cache_resource
def init_connection():
    db_password = 'YOUR_DB_PASSWORD_HERE' 
    url_object = URL.create(
        "postgresql",
        username="postgres",
        password=db_password,
        host="localhost",
        port=5432,
        database="forest_guardian"
    )
    return create_engine(url_object)

engine = init_connection()

# Fetch data directly from PostgreSQL using SQL!
@st.cache_data(ttl=600)
def load_data():
    return pd.read_sql("SELECT * FROM sectors;", engine)

df_sectors = load_data()

# Combine API with DB metadata
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

# --- 4. AGENT INTELLECTUAL ENGINE ---
class ForestGuardianAgent:
    def __init__(self, static_terrain, live_api):
        self.df = static_terrain
        self.live = live_api["live_conditions"]
        
    def calculate_wildfire_risk(self):
        temp = self.live["ambient_temperature_c"]
        rh = self.live["relative_humidity_pct"]
        weather_multiplier = 1.0 + ((temp / 40.0) * 0.25) + ((1 - (rh / 100.0)) * 0.25)
        hotspot_sectors = [h["nearest_sector_id"] for h in self.live["active_thermal_hotspots"]]
        
        risks = []
        for _, row in self.df.iterrows():
            static_score = (row['Tree_Density_Pct'] * 20) + ((1.0 - row['Fuel_Moisture_Content_Pct']) * 20) + ((min(row['Slope_Steepness_Deg'], 45) / 45) * 10)
            base_risk = static_score * weather_multiplier
            boost = 20 if row['Sector_ID'] in hotspot_sectors else 0
            boost += 5 if row['Historical_Fires_10Yr'] >= 5 else 0
            
            risks.append({
                "Sector ID": row['Sector_ID'],
                "Zone Name": row['Zone_Name'],
                "Vegetation": row['Primary_Vegetation_Type'],
                "Risk Score": round(min(base_risk + boost, 100.0), 1),
                "latitude": row['Latitude'],
                "longitude": row['Longitude']
            })
            
        return pd.DataFrame(risks).sort_values(by="Risk Score", ascending=False)

# --- 5. TACTICAL INTERFACE RENDERING ---
st.title("🌲 Forest Guardian Tactical Dashboard")
st.markdown(f"**Target Area:** `{api_data['target_forest']}` | **Live Telemetry Feed:** `{api_data['source']}`")
st.divider()

guardian = ForestGuardianAgent(df_sectors, api_data)
risk_df = guardian.calculate_wildfire_risk()

# Live Weather Metrics 
st.subheader("📡 Live Environmental Telemetry")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Temperature", f"{api_data['live_conditions']['ambient_temperature_c']} °C")
col2.metric("Relative Humidity", f"{api_data['live_conditions']['relative_humidity_pct']} %")
col3.metric("Wind Speed", f"{api_data['live_conditions']['wind_speed_mph']} MPH")
col4.metric("Wind Direction", api_data['live_conditions']['wind_direction_cardinal'])
st.divider()

# Interactive Map Section
st.subheader("🗺️ Live Sector Risk Map")
st.map(risk_df, color="#ff4b4b", size=250, zoom=9)
st.caption("Red dots represent monitored sector coordinates. Zoom and pan to explore the terrain.")
st.divider()

# Active Alerts Section
st.subheader("🚨 Active Ranger Dispatch Alerts")
critical_sectors = risk_df[risk_df["Risk Score"] >= 85]
high_sectors = risk_df[(risk_df["Risk Score"] >= 70) & (risk_df["Risk Score"] < 85)]

if not critical_sectors.empty:
    for _, row in critical_sectors.iterrows():
        st.markdown(f"""
        <div class="critical-alert">
            <h4 style="margin:0; color:#ff4b4b;">CRITICAL ALERT - Score: {row['Risk Score']}/100</h4>
            <strong>Sector:</strong> {row['Sector ID']} ({row['Zone Name']})<br>
            <strong>Action:</strong> Immediate thermal threat detected. Dispatch patrol trucks & air support immediately.
        </div>
        """, unsafe_allow_html=True)

if not high_sectors.empty:
    for _, row in high_sectors.iterrows():
        st.markdown(f"""
        <div class="high-risk">
            <h4 style="margin:0; color:#ffa421;">HIGH RISK WARNING - Score: {row['Risk Score']}/100</h4>
            <strong>Sector:</strong> {row['Sector ID']} ({row['Zone Name']})<br>
            <strong>Action:</strong> High structural vulnerability under current weather. Pre-position assets.
        </div>
        """, unsafe_allow_html=True)

st.divider()

# Risk Data Visualization
st.subheader("📊 Sector Risk Breakdown")
with st.expander("View Complete Sector Analysis", expanded=True):
    for _, row in risk_df.iterrows():
        score = row['Risk Score']
        text_col, bar_col = st.columns([1, 2])
        with text_col:
            st.write(f"**{row['Sector ID']}** - {row['Zone Name']}")
            st.caption(f"Vegetation: {row['Vegetation']}")
        with bar_col:
            st.progress(int(score), text=f"Risk Score: {score}/100")