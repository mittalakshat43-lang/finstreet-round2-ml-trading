# features/build_features.py

import pandas as pd
import numpy as np
import os

def compute_clv(df):
    denom = (df["high"] - df["low"]).replace(0, np.nan)
    clv = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / denom
    return clv.fillna(0)

def compute_streaks(df):
    close_diff = df["close"].diff()
    up = (close_diff > 0).astype(int)
    down = (close_diff < 0).astype(int)
    up_streak, down_streak = [], []
    u, d = 0, 0
    for i in range(len(df)):
        u = u + 1 if up.iloc[i] == 1 else 0
        d = d + 1 if down.iloc[i] == 1 else 0
        up_streak.append(u)
        down_streak.append(d)
    return pd.Series(up_streak, index=df.index), pd.Series(down_streak, index=df.index)

def build_features():
    # --- STEP 1: LOCATE THE FILE ---
    # We look in 'data/raw/' since your fetch script put it there
    input_path = "data/raw/rites_daily.csv"
    output_path = "data/processed/rites_features.csv"
    
    print(f"🔍 Searching for input file at: {os.path.abspath(input_path)}")
    
    if not os.path.exists(input_path):
        print(f"❌ FAILED: The file '{input_path}' does not exist.")
        return

    # --- STEP 2: LOAD DATA ---
    print("📖 Loading CSV...")
    df = pd.read_csv(input_path)
    print(f"✅ Loaded {len(df)} rows.")

    # --- STEP 3: CALCULATE FEATURES ---
    print("⚙️  Calculating technical indicators...")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    
    df["return_1d"] = df["close"].pct_change(1)
    df["return_3d"] = df["close"].pct_change(3)
    df["return_5d"] = df["close"].pct_change(5)
    df["clv"] = compute_clv(df)
    df["up_streak"], df["down_streak"] = compute_streaks(df)
    df["accel"] = df["return_1d"] - df["return_1d"].shift(1)
    
    # Target: 1 if tomorrow's price is higher than today
    df["target"] = (df["close"].shift(-1) > df["close"]).astype(int)

    # --- STEP 4: CLEANING ---
    feature_cols = ["return_1d", "return_3d", "return_5d", "clv", "up_streak", "down_streak", "accel", "target"]
    final_df = df[["date"] + feature_cols].dropna().reset_index(drop=True)
    print(f"🧹 Dropped NaNs. Remaining rows for training: {len(final_df)}")

    # --- STEP 5: SAVE ---
    os.makedirs("data/processed", exist_ok=True)
    final_df.to_csv(output_path, index=False)
    
    print(f"🚀 SUCCESS! Features saved to: {os.path.abspath(output_path)}")
    print("\nPreview of processed data:")
    print(final_df.head())

# THIS PART IS CRUCIAL: It tells Python to actually run the function
if __name__ == "__main__":
    build_features()
