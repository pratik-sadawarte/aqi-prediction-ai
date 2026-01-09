import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os

# Load API key
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Coordinates (Mumbai)
LAT = 19.0760
LON = 72.8777

# CSV path
csv_path = "../data/aqi_data.csv"
os.makedirs("../data", exist_ok=True)

def fetch_aqi():
    print("Starting AQI fetch...")

    url = (
        f"http://api.openweathermap.org/data/2.5/air_pollution"
        f"?lat={LAT}&lon={LON}&appid={API_KEY}"
    )

    response = requests.get(url, timeout=20)
    data = response.json()

    aqi = data["list"][0]["main"]["aqi"]
    comp = data["list"][0]["components"]

    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "aqi": aqi,
        "co": comp["co"],
        "no2": comp["no2"],
        "o3": comp["o3"],
        "so2": comp["so2"],
        "pm2_5": comp["pm2_5"],
        "pm10": comp["pm10"]
    }

    df = pd.DataFrame([row])

    if not os.path.exists(csv_path):
        df.to_csv(csv_path, index=False)
    else:
        df.to_csv(csv_path, mode="a", header=False, index=False)

    print(f"Data recorded at {row['timestamp']} | AQI: {aqi}")

if __name__ == "__main__":
    fetch_aqi()
