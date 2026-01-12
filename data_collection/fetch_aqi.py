import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os
import sys

# Load API key
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not API_KEY:
    print("ERROR: OPENWEATHER_API_KEY not found")
    sys.exit(1)

LAT = 19.0760
LON = 72.8777

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)


csv_path = os.path.join(DATA_DIR, "aqi_data.csv")

print("Writing data to:", csv_path)



def fetch_aqi():
    print("Starting AQI fetch...")

    url = (
        f"http://api.openweathermap.org/data/2.5/air_pollution"
        f"?lat={LAT}&lon={LON}&appid={API_KEY}"
    )

    response = requests.get(url, timeout=20)

    if response.status_code != 200:
        print(f"API ERROR: {response.status_code}")
        print(response.text)
        return

    data = response.json()

    # Validate response structure
    if "list" not in data or len(data["list"]) == 0:
        print("ERROR: AQI data not found in API response")
        print(data)
        return

    comp = data["list"][0]["components"]
    aqi = data["list"][0]["main"]["aqi"]

    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "aqi": aqi,
        "co": comp.get("co"),
        "no2": comp.get("no2"),
        "o3": comp.get("o3"),
        "so2": comp.get("so2"),
        "pm2_5": comp.get("pm2_5"),
        "pm10": comp.get("pm10")
    }

    df = pd.DataFrame([row])

    if not os.path.exists(csv_path):
        df.to_csv(csv_path, index=False)
    else:
        df.to_csv(csv_path, mode="a", header=False, index=False)

    print(f"AQI data recorded at {row['timestamp']} | AQI: {aqi}")

if __name__ == "__main__":
    fetch_aqi()
