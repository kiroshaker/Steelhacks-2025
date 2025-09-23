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

load_dotenv()

try:
    base_dir = os.path.dirname(__file__)
    model_path = os.path.join(base_dir, "model.pkl")
    bundle = joblib.load(model_path)
    model = bundle["model"]
    model_features = bundle["features"]
    print(f"INFO:     Model and feature list loaded successfully from {model_path}.")
except FileNotFoundError:
    print(f"ERROR:    'model.pkl' not found at expected path: {model_path}. Please ensure the model file is in the backend/ folder.")
    model = None
except KeyError:
    print("ERROR:    'model.pkl' is not in the expected format (dict with 'model' and 'features').")
    model = None
except Exception as e:
    print(f"ERROR:    Unexpected error while loading model.pkl: {e!r}")
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
    suggested_po_qty: int
    at_risk: bool

# --- 2. Connector Functions --

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
        for forecast in data.get("list", []):
            forecast_date = date.fromtimestamp(forecast.get("dt")).strftime("%Y-%m-%d")
            if forecast_date not in daily_forecasts:
                daily_forecasts[forecast_date] = {
                    "avg_temp": forecast.get("main", {}).get("temp"),
                    "precipitation": forecast.get("rain", {}).get("3h", 0) 
                }

        forecast_data = list(daily_forecasts.values())[:5]
        
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
            "confidence": 0.0,
            "suggested_po_qty": 0,
            "at_risk": False,
        }
        
    weather_data = get_weather_forecast()
    
    if not weather_data:
        return {
            "forecast_dates": [], "predicted_demand": [],
            "status": "Error: Weather data not available",
            "confidence": 0.0,
            "suggested_po_qty": 0,
            "at_risk": False,
        }

    future_dates = [date.today() + timedelta(days=i) for i in range(7)]
    
    df_predict = pd.DataFrame({
        'avg_temp': [day['avg_temp'] for day in weather_data],
        'month': [d.month for d in future_dates],
        'dayofweek': [d.weekday() for d in future_dates],
        'precipitation': [day['precipitation'] for day in weather_data]
    })

    seasons = []
    for d in future_dates:
        if d.month in [3, 4, 5]: seasons.append("Spring")
        elif d.month in [6, 7, 8]: seasons.append("Summer")
        elif d.month in [9, 10, 11]: seasons.append("Fall")
        else: seasons.append("Winter")
    
    df_predict['season'] = seasons
    df_predict = pd.get_dummies(df_predict, columns=['season'], drop_first=True)

    for col in model_features:
        if col not in df_predict.columns:
            df_predict[col] = 0
    
    df_predict = df_predict[model_features]
    
    predictions = model.predict(df_predict)
    predicted_demand = predictions.astype(int).tolist()

    CURRENT_INVENTORY = 1500
    total_expected_demand = int(sum(predicted_demand))
    remaining_stock = CURRENT_INVENTORY - total_expected_demand

    at_risk = remaining_stock <= 20
    suggested_po_qty = 0
    if at_risk:
        suggested_po_qty = max(0, total_expected_demand + 20 - CURRENT_INVENTORY)

    if at_risk:
        final_overall_status = "At Risk: Low Inventory"
    elif remaining_stock < 500:
        final_overall_status = "Warning: Potential Local Shortage"
    else:
        final_overall_status = "Stock Level OK"

    return {
        "forecast_dates": [d.strftime("%Y-%m-%d") for d in future_dates],
        "predicted_demand": predicted_demand,
        "status": final_overall_status,
        "confidence": 0.92,
        "suggested_po_qty": suggested_po_qty,
        "at_risk": at_risk,
    }

# --- 4. API Endpoint ---

@app.get("/predict", response_model=PredictionResponse)
def get_prediction():
    """Returns a 7-day demand forecast for Tamiflu (Oseltamivir)."""
    return get_real_forecast()
