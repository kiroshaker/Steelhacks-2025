# RxCast: AI-Powered Pharmacy Demand Forecasting
**RxCast** is an award-winning full-stack prototype developed in 24 hours for the Steelhacks 2025 hackathon. It addresses the critical issue of hospital drug shortages by using machine learning to forecast pharmaceutical demand, helping healthcare providers proactively manage their inventory and ensure patient safety.

This project won **1st Place in the Healthcare Optimization Track**.

## The Problem
Every year, U.S. hospitals lose billions of dollars to medication waste while simultaneously struggling with critical drug shortages that can impact patient care. This is a complex supply chain problem rooted in the difficulty of accurately predicting future demand.

## Our Solution
RxCast provides a clean, actionable dashboard for hospital pharmacists. Our system:

Forecasts Future Demand: Uses an XGBoost model trained on historical and environmental data to predict the 7-day demand for critical medications like Tamiflu.

Provides Real-Time Context: Integrates live data from the FDA's Drug Shortage Database and a live weather API to enrich its predictions.

Issues Proactive Alerts: Compares the predicted demand against simulated inventory levels to generate clear status updates, such as "Warning: Potential Local Shortage" or "CRITICAL: National Shortage," allowing staff to act before a problem occurs.

Tech Stack
Component

Technologies

Frontend

Next.js, React, TypeScript

Backend

Python, FastAPI

ML/Data

scikit-learn, XGBoost, pandas, joblib

Getting Started
Follow these instructions to set up and run the RxCast prototype on your local machine.

Prerequisites
Node.js (v18 or later recommended)

Python (v3.9 or later recommended)

1. Clone the Repository
git clone [https://github.com/your-username/rxcast.git](https://github.com/your-username/rxcast.git)
cd rxcast

2. Set Up the Backend
The backend server runs on Python with FastAPI and serves the ML model's predictions.

## Navigate to the backend directory
cd backend

## Create and activate a Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

## Install the required Python libraries
pip install -r requirements.txt

## Create the environment file for API keys
touch .env

Inside the newly created .env file, add your OpenWeatherMap API key:

OPENWEATHERMAP_API_KEY="your_api_key_goes_here"

You are now ready to run the backend:

## Run the FastAPI server
uvicorn main:app --reload

The backend API will now be running at http://127.0.0.1:8000.

3. Set Up the Frontend
The frontend is a Next.js application that visualizes the data from the backend.

## Navigate to the frontend directory from the root folder
cd frontend

## Install the required Node.js packages
npm install

## Run the frontend development server
npm run dev

The frontend application will now be running at http://localhost:3000. Open this URL in your web browser to see the RxCast dashboard in action!

Team
Kiro Shaker - Backend Engineer

Sohaib Hydari - Machine Learning Engineer

Senay Yemane - Data Engineer

Bryan Li - Frontend Developer

License
This project is licensed under the MIT License.
