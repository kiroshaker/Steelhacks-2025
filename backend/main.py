import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware

# --- 1. App & Pydantic Model ---

app = FastAPI()

# This enables your frontend to call your API from a different domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictionResponse(BaseModel):
    forecast_dates: List[str]
    predicted_demand: List[int]
    status: str
    confidence: float
    fda_status: str

# --- 2. Connector Functions ---

def get_fda_shortage_status() -> str:
    """Checks the openFDA API for Oseltamivir's shortage status."""
    TAMIFLU_GENERIC_NAME = "Oseltamivir Phosphate"
    API_ENDPOINT = "https://api.fda.gov/drug/shortages.json"
    search_query = f'generic_name:"{TAMIFLU_GENERIC_NAME}"'
    url = f'{API_ENDPOINT}?search={search_query}&limit=1'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "results" in data and len(data["results"]) > 0:
            return "Currently in Shortage"
        else:
            return "Normal"
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Could not connect to FDA API: {e}")
        return "API Error"

def get_weather_forecast() -> list:
    """Gets the 7-day weather forecast for Pittsburgh from OpenWeatherMap."""
    # IMPORTANT: Replace with your actual key.
    # For deployment, this should come from a secret manager.
    API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY", "YOUR_API_KEY_HERE")
    API_ENDPOINT = "https://api.openweathermap.org/data/3.0/onecall"
    
    PITTSBURGH_LAT = 40.4406
    PITTSBURGH_LON = -79.9959
    
    params = {
        "lat": PITTSBURGH_LAT,
        "lon": PITTSBURGH_LON,
        "appid": API_KEY,
        "units": "imperial",
        "exclude": "current,minutely,hourly,alerts"
    }
    
    try:
        response = requests.get(API_ENDPOINT, params=params)
        response.raise_for_status()
        data = response.json()
        
        forecast_data = []
        for day_data in data.get("daily", [])[:7]:
            forecast_data.append({
                "avg_temp": day_data.get("temp", {}).get("day"),
                "precipitation": day_data.get("rain", 0)
            })
        return forecast_data
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Could not connect to Weather API: {e}")
        return []

# --- 3. Main Prediction Logic (Placeholder) ---

def get_real_forecast() -> dict:
    """
    Orchestrates the data gathering, prediction, and logic.
    This is the function you will complete in Phase B-2.
    """
    # Step 1: Call your connector functions (they are ready to use!)
    weather_data = get_weather_forecast()
    fda_status = get_fda_shortage_status()

    # Step 2: (TODO) Integrate the ML model
    # TODO: Load model.pkl using joblib
    # TODO: Prepare weather_data and time features into a pandas DataFrame
    # TODO: predicted_demand = model.predict(df)
    
    # Step 3: (TODO) Perform shortage calculation
    # TODO: internal_status = "Stock Level OK" # or "Potential Shortage"
    # TODO: Determine final_overall_status based on fda_status and internal_status

    # Step 4: Return the final, structured data (using placeholders for now)
    return {
        "forecast_dates": ["2025-09-21", "2025-09-22", "2025-09-23", "2025-09-24", "2025-09-25", "2025-09-26", "2025-09-27"],
        "predicted_demand": [150, 165, 180, 170, 160, 140, 120],
        "status": "Warning: Potential Local Shortage",
        "confidence": 0.92,
        "fda_status": fda_status
    }

# --- 4. API Endpoint ---

@app.get("/predict", response_model=PredictionResponse)
def get_prediction():
    """Returns a 7-day demand forecast for Tamiflu (Oseltamivir)."""
    return get_real_forecast()