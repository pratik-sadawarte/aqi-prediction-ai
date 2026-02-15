import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

DATA_PATH = (r"data/mumbai_aqi_weather.csv")
MODEL_PATH = "models/pm25_rf.pkl"

def prepare_data(df):
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%d-%m-%Y %H:%M")

    df = df.sort_values("timestamp")

    # Lag features (use past values)
    df["pm2_5_lag1"] = df["pm2_5"].shift(1)
    df["pm2_5_lag2"] = df["pm2_5"].shift(2)

    # Time features
    df["hour"] = df["timestamp"].dt.hour

    df = df.dropna()
    return df

def train():
    df = pd.read_csv(DATA_PATH)
    df = prepare_data(df)

    FEATURES = ["pm2_5_lag1", "pm2_5_lag2", "hour"]
    TARGET = "pm2_5"

    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print(f"PM2.5 model trained. MAE: {mae:.2f}")
    print(f"Model saved at {MODEL_PATH}")

if __name__ == "__main__":
    train()
