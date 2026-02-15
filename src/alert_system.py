import pandas as pd
from datetime import datetime
import joblib


DATA_PATH = r"C:\Users\prati\Downloads\mumbai_aqi_weather (2).csv"


# -------------------------
# Load Data
# -------------------------
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["timestamp"] = pd.to_datetime(
        df["timestamp"], format="%d-%m-%Y %H:%M"
    )
    return df


# -------------------------
# Get Latest Record
# -------------------------
def get_latest_record(df):
    return df.sort_values("timestamp").iloc[-1]


# -------------------------
# Trend Calculation
# -------------------------
def calculate_trend(df, window=3):

    recent = df.sort_values("timestamp").tail(window + 1)

    if len(recent) < window + 1:
        return "Insufficient Data"

    current = recent.iloc[-1]["pm2_5"]
    previous_avg = recent.iloc[:-1]["pm2_5"].mean()

    if current > previous_avg + 5:
        return "Worsening"
    elif current < previous_avg - 5:
        return "Improving"
    else:
        return "Stable"


# -------------------------
# Best Travel Hour
# -------------------------
def get_best_travel_hour(df):

    df["hour"] = df["timestamp"].dt.hour

    hourly_avg = df.groupby("hour")["pm2_5"].mean()

    return hourly_avg.idxmin()


# -------------------------
# Severity Classification
# -------------------------
def classify_severity(pm25):

    if pm25 > 100:
        return "Severe"
    elif pm25 > 60:
        return "Moderate"
    else:
        return "Low"


# -------------------------
# ML Prediction
# -------------------------
def predict_next_pm25(df):

    model = joblib.load("models/pm25_rf.pkl")

    df = df.sort_values("timestamp")

    if len(df) < 3:
        return None

    last = df.iloc[-1]
    prev = df.iloc[-2]

    features = [[
        last["pm2_5"],
        prev["pm2_5"],
        last["timestamp"].hour
    ]]

    pred = model.predict(features)[0]

    return pred


# -------------------------
# Alert Generator
# -------------------------
def generate_alert():

    df = load_data()

    latest = get_latest_record(df)

    pm25 = latest["pm2_5"]
    pm10 = latest["pm10"]
    aqi = latest["aqi"]
    time = latest["timestamp"]

    trend = calculate_trend(df)
    best_hour = get_best_travel_hour(df)
    severity = classify_severity(pm25)

    pred_pm25 = predict_next_pm25(df)

    # Advice
    if severity == "Severe":
        advice = "Avoid outdoor travel and wear masks"
    elif severity == "Moderate":
        advice = "Limit prolonged outdoor activities"
    else:
        advice = "Safe for travel"

    # Output
    print("\n========== AIR QUALITY ALERT ==========")
    print(f"Time: {time}")
    print(f"AQI Level: {aqi}")
    print(f"PM2.5: {pm25:.2f} µg/m³")
    print(f"PM10: {pm10:.2f} µg/m³")
    print(f"Status: {severity}")
    print(f"Trend: {trend}")
    print(f"Best Travel Hour: {best_hour}:00 – {best_hour+1}:00")
    print(f"Advice: {advice}")

    # Prediction
    if pred_pm25 is not None:

        print(f"Predicted PM2.5 (next): {pred_pm25:.2f} µg/m³")

        if pred_pm25 > pm25 + 10:
            print("Forecast: Pollution likely to worsen")
        elif pred_pm25 < pm25 - 10:
            print("Forecast: Pollution likely to improve")
        else:
            print("Forecast: Stable conditions expected")

    else:
        print("Prediction: Not enough data")

    print("======================================\n")


# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    generate_alert()
