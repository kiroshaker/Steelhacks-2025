# rxcast_demand_forecast_xgb.py
# Train & evaluate an XGBoost model on fabricated dataset

import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error
import xgboost as xgb

# -------------------------------
# 1. Load dataset
# -------------------------------
df = pd.read_csv("fabricated_pharmacy_dataset_year.csv")

# Combine date + time into a single timestamp
df["timestamp"] = pd.to_datetime(df["date"] + " " + df["time"])
df = df.sort_values("timestamp")

# -------------------------------
# 2. Feature Engineering
# -------------------------------
df["dayofweek"] = df["timestamp"].dt.dayofweek
df["hour"] = df["timestamp"].dt.hour
df["month"] = df["timestamp"].dt.month

# One-hot encode categorical variables
df = pd.get_dummies(df, columns=["weather", "season"], drop_first=True)

# Split features and target
X = df.drop(columns=["qty.dispensed", "date", "time", "timestamp"])
y = df["qty.dispensed"]

# -------------------------------
# 3. Train/Test Split
# -------------------------------
split_index = int(len(df) * 0.8)
X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]
time_test = df["timestamp"].iloc[split_index:]

# -------------------------------
# 4. Train XGBoost Model
# -------------------------------
xgb_model = xgb.XGBRegressor(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    random_state=42,
    n_jobs=-1
)

xgb_model.fit(X_train, y_train)

# -------------------------------
# 5. Evaluate
# -------------------------------
preds = xgb_model.predict(X_test)
mae = mean_absolute_error(y_test, preds)
rmse = np.sqrt(mean_squared_error(y_test, preds))

print(f"XGBoost MAE: {mae:.2f}")
print(f"XGBoost RMSE: {rmse:.2f}")

# -------------------------------
# 6. Plot Results
# -------------------------------
plt.figure(figsize=(12, 6))
plt.plot(time_test, y_test.values, label="Actual", color="blue")
plt.plot(time_test, preds, label="Predicted", color="orange", alpha=0.7)
plt.xlabel("Date")
plt.ylabel("Qty Dispensed")
plt.title("XGBoost Forecast: Actual vs Predicted Medication Demand")
plt.legend()
plt.tight_layout()
plt.show()

# -------------------------------
# 7. Save Model + Feature List
# -------------------------------
model_bundle = {
    "model": xgb_model,
    "features": X_train.columns.tolist()
}
joblib.dump(model_bundle, "model.pkl")
print("✅ Model and feature list saved to model.pkl")
