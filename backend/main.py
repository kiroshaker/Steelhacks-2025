import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import pandas as pd
import joblib
from datetime import date, timedelta
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# --- 0. Load Environment & Global Objects ---

load_dotenv() # Loads variables from your .env file

# Load the model BUNDLE and unpack it
try:
    bundle = joblib.load("model.pkl")
    model = bundle["model"]
    model_features = bundle["features"]
    print("INFO:     Model and feature list loaded successfully.")
except FileNotFoundError:
    print("ERROR:    'model.pkl' not found. Please ensure the model file is in the same directory as main.py.")
    model = None
except KeyError:
    print("ERROR:    'model.pkl' is not in the expected format (dict with 'model' and 'features').")
    model = None

# --- 1. App & Pydantic Model ---

app = FastAPI()

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
    url = f'{API_ENDPOINT}?search={search_query}&limit=50'
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(response)
        data = response.json()
        print(data)
        if "results" in data and len(data["results"]) > 0:
            return "Currently in Shortage"
        else:
            return "Normal"
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Could not connect to FDA API: {e}")
        return "API Error"

def get_weather_forecast() -> list:
    """
    Gets the live 5-day weather forecast for Pittsburgh from OpenWeatherMap's
    free-tier endpoint and adapts it for the 7-day model.
    """
    API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
    
    # Use the free-tier 5-day forecast endpoint
    API_ENDPOINT = "https://api.openweathermap.org/data/2.5/forecast"
    
    PITTSBURGH_LAT, PITTSBURGH_LON = 40.4406, -79.9959

    params = {
        "lat": PITTSBURGH_LAT,
        "lon": PITTSBURGH_LON,
        "appid": API_KEY,
        "units": "imperial",
    }
    
    try:
        response = requests.get(API_ENDPOINT, params=params)
        response.raise_for_status()
        data = response.json()
        
        daily_forecasts = {}
        # The API returns data in 3-hour intervals. We'll pick one per day.
        for forecast in data.get("list", []):
            forecast_date = date.fromtimestamp(forecast.get("dt")).strftime("%Y-%m-%d")
            if forecast_date not in daily_forecasts:
                daily_forecasts[forecast_date] = {
                    "avg_temp": forecast.get("main", {}).get("temp"),
                    "precipitation": forecast.get("rain", {}).get("3h", 0) # Precipitation in the last 3h
                }

        # Convert the dictionary to a list of the next 5 days
        forecast_data = list(daily_forecasts.values())[:5]
        
        # Hackathon workaround: If we have fewer than 7 days, repeat the last day's forecast
        while len(forecast_data) < 7:
            forecast_data.append(forecast_data[-1])

        print("INFO:     Successfully fetched and adapted live 5-day weather forecast.")
        return forecast_data

    except requests.exceptions.RequestException as e:
        print(f"ERROR:    Could not connect to Weather API: {e}")
        return []

# --- 3. Main Prediction Logic ---

def get_real_forecast() -> dict:
    """Orchestrates the data gathering, prediction, and logic for Tamiflu."""
    if model is None:
        return {
            "forecast_dates": [], "predicted_demand": [],
            "status": "Error: Model 'model.pkl' not loaded on server",
            "confidence": 0.0, "fda_status": "Unknown"
        }
        
    weather_data = get_weather_forecast()
    fda_status = get_fda_shortage_status()
    
    if not weather_data:
        return {
            "forecast_dates": [], "predicted_demand": [],
            "status": "Error: Weather data not available",
            "confidence": 0.0, "fda_status": fda_status
        }

    future_dates = [date.today() + timedelta(days=i) for i in range(7)]
    
    # Create the base features
    df_predict = pd.DataFrame({
        'avg_temp': [day['avg_temp'] for day in weather_data],
        'month': [d.month for d in future_dates],
        'dayofweek': [d.weekday() for d in future_dates],
        'precipitation': [day['precipitation'] for day in weather_data]
    })

    # Replicate the one-hot encoding for 'season'
    seasons = []
    for d in future_dates:
        if d.month in [3, 4, 5]: seasons.append("Spring")
        elif d.month in [6, 7, 8]: seasons.append("Summer")
        elif d.month in [9, 10, 11]: seasons.append("Fall")
        else: seasons.append("Winter")
    
    df_predict['season'] = seasons
    df_predict = pd.get_dummies(df_predict, columns=['season'], drop_first=True)

    # Ensure all expected feature columns exist, filling missing ones with 0
    for col in model_features:
        if col not in df_predict.columns:
            df_predict[col] = 0
    
    # Ensure the column order perfectly matches the training script
    df_predict = df_predict[model_features]
    
    predictions = model.predict(df_predict)
    predicted_demand = predictions.astype(int).tolist()

    CURRENT_INVENTORY, SAFETY_STOCK = 1500, 500
    remaining_stock = CURRENT_INVENTORY - sum(predicted_demand)

    if fda_status == "Currently in Shortage":
        final_overall_status = "CRITICAL: National Shortage"
    elif remaining_stock < SAFETY_STOCK:
        final_overall_status = "Warning: Potential Local Shortage"
    else:
        final_overall_status = "Stock Level OK"
        
    return {
        "forecast_dates": [d.strftime("%Y-%m-%d") for d in future_dates],
        "predicted_demand": predicted_demand,
        "status": final_overall_status,
        "confidence": 0.92,
        "fda_status": fda_status
    }

# --- 4. API Endpoint ---

@app.get("/predict", response_model=PredictionResponse)
def get_prediction():
    """Returns a 7-day demand forecast for Tamiflu (Oseltamivir)."""
    return get_real_forecast()