import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import random

print("⚙️ Generating historical synthetic data for ML training...")

# 1. Connect to our Postgres database to get the real terrain constraints
db_password = 'YOUR_DB_PASSWORD_HERE' # <--- INSERT YOUR POSTGRES PASSWORD HERE
url_object = URL.create("postgresql", username="postgres", password=db_password, host="localhost", port=5432, database="forest_guardian")
engine = create_engine(url_object)

df_sectors = pd.read_sql("SELECT * FROM sectors;", engine)

# 2. Synthesize 5,000 days of historical weather data
historical_records = []
for _ in range(5000):
    # Pick a random sector
    sector = df_sectors.sample(1).iloc[0]
    
    # Generate random weather that makes sense for California
    temp = round(random.uniform(10.0, 45.0), 1)
    humidity = round(random.uniform(5.0, 80.0), 1)
    wind = round(random.uniform(0.0, 60.0), 1)
    
    # Simulate if a NASA Hotspot was detected (rare occurrence)
    hotspot = 1 if random.random() < 0.05 else 0 
    
    # THE SECRET LOGIC: This is what the ML model will try to learn.
    # Fire is likely if Temp > 35, Humidity < 15, Wind > 25, or if there is a Hotspot.
    fire_occurred = 0
    if (temp > 35 and humidity < 15) or wind > 40 or hotspot == 1:
        fire_occurred = 1 if random.random() < 0.85 else 0 # 85% chance it caught fire
    elif temp > 30 and humidity < 25 and sector['Tree_Density_Pct'] > 0.7:
        fire_occurred = 1 if random.random() < 0.40 else 0
        
    historical_records.append({
        "Sector_ID": sector['Sector_ID'],
        "Tree_Density_Pct": sector['Tree_Density_Pct'],
        "Fuel_Moisture_Content_Pct": sector['Fuel_Moisture_Content_Pct'],
        "Slope_Steepness_Deg": sector['Slope_Steepness_Deg'],
        "Temperature_C": temp,
        "Humidity_Pct": humidity,
        "Wind_Speed_MPH": wind,
        "Active_Hotspot": hotspot,
        "Fire_Occurred": fire_occurred
    })

df_historical = pd.DataFrame(historical_records)

# 3. Save the synthetic data to a CSV file for the ML model to read
csv_path = 'historical_fire_data.csv'
df_historical.to_csv(csv_path, index=False)
print(f"✅ Generated {len(df_historical)} historical records and saved to {csv_path}")
print(f"🔥 Total Simulated Fires: {df_historical['Fire_Occurred'].sum()}")