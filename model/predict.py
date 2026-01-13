import pandas as pd
import numpy as np
import joblib
import os

# =========================
# 🔹 CONFIGURATION
# =========================
BASE_DIR = os.getcwd()
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "rites_daily.csv")
MODEL_PATH = os.path.join(BASE_DIR, "artifacts", "trading_model.pkl")
OUTPUT_CSV = os.path.join(BASE_DIR, "data", "processed", "jan_predictions.csv")

# Must match train.py columns exactly
FEATURE_COLS = ["return_1d", "return_3d", "return_5d", "clv", "up_streak", "down_streak", "accel"]

def compute_features(df):
    """Calculates technical indicators for the entire dataset."""
    df = df.copy()
    df["return_1d"] = df["close"].pct_change(1)
    df["return_3d"] = df["close"].pct_change(3)
    df["return_5d"] = df["close"].pct_change(5)
    
    denom = (df["high"] - df["low"]).replace(0, np.nan)
    df["clv"] = (((df["close"] - df["low"]) - (df["high"] - df["close"])) / denom).fillna(0)
    
    df["up_streak"] = (df["close"].diff() > 0).astype(int).cumsum()
    df["down_streak"] = (df["close"].diff() < 0).astype(int).cumsum()
    df["accel"] = df["return_1d"] - df["return_1d"].shift(1)
    
    return df

def run_predictions():
    print("⏳ Loading Data & Model...")
    if not os.path.exists(RAW_DATA_PATH):
        print("❌ Error: Raw data not found.")
        return

    # Load Full Data (Nov 1 - Jan 8)
    full_df = pd.read_csv(RAW_DATA_PATH)
    full_df["date"] = pd.to_datetime(full_df["date"])
    full_df = full_df.sort_values("date").reset_index(drop=True)
    
    # Load Model (Trained on Nov-Dec only)
    model = joblib.load(MODEL_PATH)

    # Identify the specific days we want to PREDICT (Jan 1 - Jan 8)
    # Note: We filter for dates > Dec 31
    target_dates = full_df[full_df["date"] > "2025-12-31"]["date"].tolist()
    
    predictions_list = []

    print(f"🔮 Generating Sequential Predictions for {len(target_dates)} days...")
    print("="*60)
    print(f"{'TARGET DATE':<12} | {'INPUT DATE':<12} | {'PREDICTION':<10}")
    print("="*60)

    for target_date in target_dates:
        # To predict 'target_date', we use data UP TO the day before it.
        # This mimics standing at 9:00 AM on 'target_date' with yesterday's charts.
        historical_context = full_df[full_df["date"] < target_date].copy()
        
        # Calculate features on this history
        feats_df = compute_features(historical_context)
        
        # Get the very last row (Yesterday's closed candle)
        # This is our input vector
        input_vector = feats_df.tail(1)[FEATURE_COLS].fillna(0)
        input_date = historical_context.iloc[-1]["date"]

        # Predict
        pred = model.predict(input_vector)[0]
        prob = model.predict_proba(input_vector)[0].max()
        
        signal = "BUY" if pred == 1 else "WAIT"
        
        print(f"{target_date.date()} | {input_date.date()}   | {signal} ({prob:.2f})")

        predictions_list.append({
            "date": target_date,
            "prediction": pred,       # 1 or 0
            "confidence": prob
        })

    # Save to CSV
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    pd.DataFrame(predictions_list).to_csv(OUTPUT_CSV, index=False)
    print("="*60)
    print(f"✅ Predictions saved to: {OUTPUT_CSV}")

if __name__ == "__main__":
    run_predictions()
