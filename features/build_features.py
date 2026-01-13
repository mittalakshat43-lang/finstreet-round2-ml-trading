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
    # PATH SETUP
    # Assuming this script is inside a folder (e.g., 'features/' or root)
    # We use relative paths to be safe.
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # If this script is in 'features/', go up one level. If in root, stay there.
    # Adjust this logic if your folder structure changes. 
    # Here we assume running from ROOT.
    input_path = "data/raw/rites_daily.csv"
    output_path = "data/processed/rites_features.csv"
    
    if not os.path.exists(input_path):
        print(f"❌ Error: {input_path} not found. Run fyers_fetch_rites.py first.")
        return

    print("📖 Loading Data...")
    df = pd.read_csv(input_path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    print("⚙️ Engineering Features...")
    df["return_1d"] = df["close"].pct_change(1)
    df["return_3d"] = df["close"].pct_change(3)
    df["return_5d"] = df["close"].pct_change(5)
    df["clv"] = compute_clv(df)
    df["up_streak"], df["down_streak"] = compute_streaks(df)
    df["accel"] = df["return_1d"] - df["return_1d"].shift(1)
    
    # Target: 1 if NEXT day is Up, 0 if Down
    df["target"] = (df["close"].shift(-1) > df["close"]).astype(int)

    # Clean NaNs (removes the last row because target is NaN)
    final_df = df.dropna().reset_index(drop=True)

    # SAVE
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_df.to_csv(output_path, index=False)
    print(f"✅ Features saved to {output_path} ({len(final_df)} rows for training)")

if __name__ == "__main__":
    build_features()
