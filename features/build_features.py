# features/build_features.py
import pandas as pd
import numpy as np

def compute_clv(df):
    denom = (df["high"] - df["low"])
    # Avoid zero division
    denom = denom.replace(0, np.nan) 
    clv = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / denom
    return clv.fillna(0)

def build_features(df, mode="train"):
    """
    mode: 'train' (drops NaN targets for training) 
          or 'predict' (keeps the last row for inference)
    """
    # 1. Technical Indicators (Adding RSI & SMA for better score)
    df["return_1d"] = df["close"].pct_change(1)
    df["sma_5"] = df["close"].rolling(5).mean()
    df["clv"] = compute_clv(df)
    
    # Simple Volatility (Risk Management Feature)
    df["volatility"] = df["return_1d"].rolling(5).std()

    # 2. Prepare Features
    feature_cols = ["return_1d", "sma_5", "clv", "volatility"]
    
    if mode == "train":
        # Create Target: 1 if Next Day Close > Today Close
        df["target"] = (df["close"].shift(-1) > df["close"]).astype(int)
        
        # Drop NaNs (first 5 days have no SMA, last day has no Target)
        final_df = df[feature_cols + ["target"]].dropna().reset_index(drop=True)
        return final_df
        
    elif mode == "predict":
        # meaningful features only
        final_df = df[feature_cols].iloc[[-1]].reset_index(drop=True)
        return final_df
