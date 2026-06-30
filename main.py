from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pandas as pd
import requests
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import pickle
import os

app = FastAPI()

# 1. Mount the frontend folder so the browser can see it
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Database & ML Initialization (Runs once when server starts)
db_password = 'YOUR_DB_PASSWORD_HERE' # <--- INSERT POSTGRES PASSWORD HERE
url_object = URL.create("postgresql", username="postgres", password=db_password, host="localhost", port=5432, database="forest_guardian")
engine = create_engine(url_object)

with open('xgboost_fire_model.pkl', 'rb') as f:
    xgb_model = pickle.load(f)

# 3. The Core API Endpoint
@app.get("/api/telemetry")
def get_telemetry():
    # Fetch Live Weather
    weather = {"temp": 17.1, "humidity": 32.0, "wind": 5.1}
    try:
        req = requests.get("https://api.open-meteo.com/v1/forecast?latitude=38.01&longitude=-120.12&current=temperature_2m,relative_humidity_2m,wind_speed_10m", timeout=3)
        if req.status_code == 200:
            data = req.json()
            weather = {"temp": data['current']['temperature_2m'], "humidity": data['current']['relative_humidity_2m'], "wind": data['current']['wind_speed_10m']}
    except: pass

    # Fetch Sectors & Predict
    df_sectors = pd.read_sql("SELECT * FROM sectors;", engine)
    hotspot_sectors = ["SEC-043"] # Simulated active hotspot
    
    risks = []
    for _, row in df_sectors.iterrows():
        is_hotspot = 1 if row['Sector_ID'] in hotspot_sectors else 0
        features = pd.DataFrame([{
            "Tree_Density_Pct": row['Tree_Density_Pct'], "Fuel_Moisture_Content_Pct": row['Fuel_Moisture_Content_Pct'],
            "Slope_Steepness_Deg": row['Slope_Steepness_Deg'], "Temperature_C": weather["temp"],
            "Humidity_Pct": weather["humidity"], "Wind_Speed_MPH": weather["wind"], "Active_Hotspot": is_hotspot
        }])
        prob = float(xgb_model.predict_proba(features)[0][1])
        risks.append({
            "id": str(row['Sector_ID']), 
            "zone": str(row['Zone_Name']), 
            "veg": str(row['Primary_Vegetation_Type']),
            "score": float(round(prob * 100, 1)), 
            "lat": float(row['Latitude']), 
            "lon": float(row['Longitude'])
        })
    
    # Sort and return the highest risk sectors
    risks.sort(key=lambda x: x["score"], reverse=True)
    return {"weather": weather, "risks": risks}

# Serve the HTML UI
@app.get("/")
def serve_ui():
    return FileResponse('static/index.html')