# features/build_features.py

import pandas as pd
import numpy as np


def compute_clv(df):
    """
    CLV = Close Location Value
    CLV = ((Close - Low) - (High - Close)) / (High - Low)
    Range: [-1, +1]
    """
    denom = (df["high"] - df["low"])
    clv = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / denom

    # Avoid division by zero
    clv = clv.replace([np.inf, -np.inf], np.nan)
    clv = clv.fillna(0)

    return clv


def compute_streaks(df):
    """
    Computes up_streak and down_streak based on consecutive close changes.
    """
    close_diff = df["close"].diff()

    up = (close_diff > 0).astype(int)
    down = (close_diff < 0).astype(int)

    up_streak = []
    down_streak = []

    u, d = 0, 0
    for i in range(len(df)):
        if up.iloc[i] == 1:
            u += 1
        else:
            u = 0

        if down.iloc[i] == 1:
            d += 1
        else:
            d = 0

        up_streak.append(u)
        down_streak.append(d)

    return pd.Series(up_streak, index=df.index), pd.Series(down_streak, index=df.index)


def build_features(input_csv="data/raw/rites_daily.csv",
                   output_csv="data/processed/rites_features.csv"):
    # 1) Load raw OHLCV data from Ojas
    df = pd.read_csv(input_csv)

    # Ensure correct column order / types
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    # 2) FEATURES (Pranav’s final feature list)

    # (1) Simple returns
    df["return_1d"] = df["close"].pct_change(1)
    df["return_3d"] = df["close"].pct_change(3)
    df["return_5d"] = df["close"].pct_change(5)

    # (2) CLV
    df["clv"] = compute_clv(df)

    # (3) Streak features
    df["up_streak"], df["down_streak"] = compute_streaks(df)

    # (4) Momentum acceleration
    # accel = return_1d(t) - return_1d(t-1)
    df["accel"] = df["return_1d"] - df["return_1d"].shift(1)

    # 3) TARGET (locked definition)
    # target = 1 if close[t+1] > close[t] else 0
    df["target"] = (df["close"].shift(-1) > df["close"]).astype(int)

    # 4) Drop rows where features not available (due to shift/pct_change)
    # Also drop last row (no target for last day)
    feature_cols = [
        "return_1d", "return_3d", "return_5d",
        "clv",
        "up_streak", "down_streak",
        "accel",
        "target"
    ]

    final_df = df[["date"] + feature_cols].dropna().reset_index(drop=True)

    # 5) Save final features dataset
    import os
    os.makedirs("data/processed", exist_ok=True)
    final_df.to_csv(output_csv, index=False)

    print("✅ Feature dataset created successfully!")
    print("Saved to:", output_csv)
    print("\nPreview:\n", final_df.head())


if __name__ == "__main__":
    build_features()

