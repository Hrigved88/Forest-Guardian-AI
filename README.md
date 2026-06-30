# 🌲 Forest Guardian AI

**Forest Guardian AI** is a cinematic, highly-optimized proof-of-concept dashboard designed for regional wildfire dispatch and predictive risk modeling. It features a breathtaking 3D WebGL interface backed by live telemetry and machine learning.

## ✨ Features

- **🌍 Interactive 3D WebGL Globe:** Built with Three.js, featuring ultra-high-resolution 16K day and night textures for maximum visual fidelity and crisp zooming.
- **🔥 Predictive Risk Modeling:** Utilizes an XGBoost machine learning model trained on historical fire data and terrain constraints to predict wildfire risk scores.
- **🛰️ Live API Telemetry:** Integrates with the Open-Meteo API to fetch real-time weather conditions (temperature, humidity, wind speed) for active sectors.
- **🗄️ Spatial PostgreSQL Backend:** Leverages PostgreSQL for managing geographical clusters and terrain constraints.
- **🎬 Cinematic Animations:** Smooth, progressive camera sweeps and rotational algorithms that naturally track active fire zones without jarring movements.

## 🛠️ Technology Stack

- **Frontend:** HTML5, Vanilla CSS, JavaScript, Three.js
- **Backend:** Python, Streamlit (`app.py`)
- **Database:** PostgreSQL
- **Machine Learning:** XGBoost, Pandas, Scikit-Learn

## 🚀 Setup & Installation

### Prerequisites
- Python 3.8+
- PostgreSQL Server (running locally)

### 1. Database Configuration
Before running the application, ensure you have a local PostgreSQL server running. You will need to set up your database password:
1. Open `db_setup.py`, `generate_ml_data.py`, `main.py`, and `app.py`.
2. Locate the database connection strings and replace `"YOUR_DB_PASSWORD_HERE"` with your actual PostgreSQL password.

### 2. Install Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 3. Initialize the System
Run the following scripts in order to generate the database tables, create the synthetic terrain data, and train the predictive ML model:

```bash
# Set up the Postgres database
python db_setup.py

# Generate ML training data
python generate_ml_data.py

# Train the XGBoost predictive model
python train_model.py
```

### 4. Launch the Dashboard
Start the Streamlit application:
```bash
streamlit run app.py
```
*(Note: If you want to view the standalone 3D globe, you can launch a local web server in the `static` folder using `python -m http.server 8000` and navigate to `http://localhost:8000/index.html`)*

## 🎨 UI & Design Notes
The dashboard is designed to look like a premium dispatch center. It prioritizes dark-mode aesthetics, smooth glassmorphism, and high-performance WebGL rendering. The textures included in this repository have been specifically upscaled to 12K and 16K resolutions to prevent blurriness during extreme camera zooms.

---
*Disclaimer: This is a proof-of-concept application built for demonstration purposes.*
