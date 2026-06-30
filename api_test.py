import requests

# We are testing Sector 43 (Smokey Ridge) coordinates
latitude = 38.0124
longitude = -120.1234

print(f"📡 Pinging Open-Meteo Satellite for Sector (Lat: {latitude}, Lon: {longitude})...")

# The exact URL to ask Open-Meteo for current temp, humidity, and wind
url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,wind_speed_10m&temperature_unit=celsius&wind_speed_unit=mph"

try:
    # Send the request to the internet
    response = requests.get(url)
    
    # Check if the server answered successfully (Status Code 200)
    if response.status_code == 200:
        data = response.json() # Convert the response into a Python dictionary
        
        # Dig into the JSON to pull out our specific metrics
        current = data['current']
        temp = current['temperature_2m']
        humidity = current['relative_humidity_2m']
        wind = current['wind_speed_10m']
        
        print("\n✅ CONNECTION SUCCESSFUL. LIVE DATA EXTRACTED:")
        print("-" * 40)
        print(f"Temperature:       {temp} °C")
        print(f"Relative Humidity: {humidity} %")
        print(f"Wind Speed:        {wind} MPH")
        print("-" * 40)
    else:
        print(f"❌ Connection Failed. Server returned status code: {response.status_code}")

except Exception as e:
    print(f"❌ A network error occurred: {e}")