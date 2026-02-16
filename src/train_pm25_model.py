import pandas as pd
import joblib
import os
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score


DATA_PATH = (r"data/mumbai_aqi_weather.csv")
MODEL_PATH = "models/pm25_rf.pkl"


# -------------------------
# Data Preparation
# -------------------------
def prepare_data(df):

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        format="mixed",
        errors="coerce"
    )

    df = df.dropna(subset=["timestamp"])
    df = df.sort_values("timestamp")

    # Time feature
    df["hour"] = df["timestamp"].dt.hour

    # Lag features
    df["pm2_5_lag1"] = df["pm2_5"].shift(1)
    df["pm2_5_lag2"] = df["pm2_5"].shift(2)

    df = df.dropna()

    return df


# -------------------------
# Training + Evaluation
# -------------------------
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

    # Train model
    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42
    )

    model.fit(X_train, y_train)

    # Prediction
    preds = model.predict(X_test)

    # Evaluation
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    rmse = np.sqrt(((preds - y_test) ** 2).mean())

    # Save model
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    # Print metrics
    print("\nModel Evaluation:")
    print(f"MAE  : {mae:.2f}")
    print(f"RMSE : {rmse:.2f}")
    print(f"R2   : {r2:.3f}")

    print(f"\nModel saved at {MODEL_PATH}")

    # Log performance
    with open("model_performance.txt", "a") as f:
        f.write(
            f"{pd.Timestamp.now()}, "
            f"MAE={mae:.2f}, RMSE={rmse:.2f}, R2={r2:.3f}\n"
        )


# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    train()
