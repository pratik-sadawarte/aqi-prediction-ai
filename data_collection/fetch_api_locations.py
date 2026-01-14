import requests
import csv
import os
from datetime import datetime, timezone
from time import sleep

# =========================
# API CONFIG
# =========================
API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not API_KEY:
    raise ValueError("OPENWEATHER_API_KEY not found in environment variables")

AQI_URL = "https://api.openweathermap.org/data/2.5/air_pollution"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

CSV_FILE = "data/mumbai_aqi_weather.csv"

# =========================
# LOCATIONS (LOCKED)
# =========================
LOCATIONS = [
    {"id": "CHEMBUR", "lat": 19.0510, "lon": 72.8940},
    {"id": "ANDHERI_E", "lat": 19.1136, "lon": 72.8697},
    {"id": "POWAI", "lat": 19.1197, "lon": 72.9051},
    {"id": "DADAR", "lat": 19.0176, "lon": 72.8562},
    {"id": "COLABA", "lat": 18.9067, "lon": 72.8147},
    {"id": "BORIVALI_W", "lat": 19.2307, "lon": 72.8567},
    {"id": "MULUND_E", "lat": 19.1726, "lon": 72.9570},
    {"id": "ULHASNAGAR", "lat": 19.2160, "lon": 73.1510},
]

# =========================
# CSV SCHEMA
# =========================
FIELDNAMES = [
    "timestamp",
    "location_id",
    "latitude",
    "longitude",
    "aqi",
    "pm2_5",
    "pm10",
    "no2",
    "so2",
    "o3",
    "co",
    "temperature",
    "humidity",
    "wind_speed",
    "wind_deg",
    "pressure",
    "cloud_coverage",
    "rainfall"
]

os.makedirs("data", exist_ok=True)

# Create CSV if not exists
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()

# =========================
# FETCH DATA
# =========================
timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
rows = []

for loc in LOCATIONS:
    params = {
        "lat": loc["lat"],
        "lon": loc["lon"],
        "appid": API_KEY
    }

    # AQI REQUEST
    aqi_resp = requests.get(AQI_URL, params=params, timeout=10).json()
    if "list" not in aqi_resp or not aqi_resp["list"]:
        print(f"[WARN] AQI missing for {loc['id']}")
        continue

    aqi = aqi_resp["list"][0]

    # WEATHER REQUEST
    weather_resp = requests.get(WEATHER_URL, params=params, timeout=10).json()
    if "main" not in weather_resp:
        print(f"[WARN] Weather missing for {loc['id']}")
        continue

    row = {
        "timestamp": timestamp,
        "location_id": loc["id"],
        "latitude": loc["lat"],
        "longitude": loc["lon"],
        "aqi": aqi["main"]["aqi"],
        "pm2_5": aqi["components"].get("pm2_5"),
        "pm10": aqi["components"].get("pm10"),
        "no2": aqi["components"].get("no2"),
        "so2": aqi["components"].get("so2"),
        "o3": aqi["components"].get("o3"),
        "co": aqi["components"].get("co"),
        "temperature": weather_resp["main"].get("temp"),
        "humidity": weather_resp["main"].get("humidity"),
        "wind_speed": weather_resp.get("wind", {}).get("speed"),
        "wind_deg": weather_resp.get("wind", {}).get("deg"),
        "pressure": weather_resp["main"].get("pressure"),
        "cloud_coverage": weather_resp.get("clouds", {}).get("all"),
        "rainfall": weather_resp.get("rain", {}).get("1h", 0.0)
    }

    rows.append(row)
    sleep(1)

# WRITE DATA
if rows:
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerows(rows)

print(f"SUCCESS: Inserted {len(rows)} rows at {timestamp}")
