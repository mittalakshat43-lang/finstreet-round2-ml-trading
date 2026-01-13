# model/predict.py

import os
import joblib
import pandas as pd
from fyers_apiv3 import fyersModel

# --- CONFIGURATION ---
CLIENT_ID = "6N3D2EQCU5-100"
MODEL_PATH = "model/artifacts/trading_model.pkl"
DATA_PATH = "data/processed/rites_features.csv"

def get_token_path():
    """Finds access_token.txt in current or parent directory."""
    # This list ensures the script looks everywhere for your 'pass'
    possible_paths = [
        "access_token.txt",             # Root folder
        "../access_token.txt",          # One level up
        "fyers/access_token.txt"        # Inside fyers folder
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def get_latest_signal():
    """Loads the latest features and predicts tomorrow's move."""
    if not os.path.exists(MODEL_PATH) or not os.path.exists(DATA_PATH):
        print(f"❌ Error: Model ({MODEL_PATH}) or Features ({DATA_PATH}) missing!")
        return None

    # Load Model and Data
    model = joblib.load(MODEL_PATH)
    df = pd.read_csv(DATA_PATH)
    
    # Take the VERY LAST row (most recent data)
    latest_data = df.tail(1).drop(columns=["date", "target"], errors='ignore')
    
    prediction = model.predict(latest_data)[0]
    # Optional: Get probability to track confidence for Jan 1-8
    try:
        prob = model.predict_proba(latest_data)[0][1]
        print(f"🎲 Model Confidence: {prob:.2%}")
    except:
        pass

    return prediction 

def execute_trade(signal):
    """Uses FYERS API to place an order based on signal."""
    token_path = get_token_path()
    
    if token_path is None:
        print("❌ ERROR: access_token.txt not found. Please run fyers_fetch_rites.py first!")
        return

    with open(token_path, "r") as f:
        access_token = f.read().strip()

    # Initialize Fyers Model
    fyers = fyersModel.FyersModel(client_id=CLIENT_ID, token=access_token)

    # 1. Verify Login (Fixes the 'Account: None' error)
    profile = fyers.get_profile()
    if profile.get('s') != 'ok':
        print("❌ API Error: Token may be expired. Refresh it by running your fetch script.")
        print("Response:", profile)
        return
    
    # Extract name for verification
    user_name = profile.get('data', {}).get('display_name', 'Verified User')
    print(f"💰 Account: {user_name} | Signal: {'BUY' if signal == 1 else 'WAIT'}")

    # 2. Place Order if Signal is 1 (Buy)
    if signal == 1:
        data = {
            "symbol": "NSE:RITES-EQ",
            "qty": 1,
            "type": 2,          # 2 = Market Order
            "side": 1,          # 1 = Buy
            "productType": "INTRADAY",
            "limitPrice": 0,
            "stopPrice": 0,
            "validity": "DAY",
            "disclosedQty": 0,
            "offlineOrder": "False"
        }
        response = fyers.place_order(data=data)
        print("🚀 FYERS Response:", response.get('message', response))
    else:
        print("⏸️ No buy signal generated for today. Staying cash.")

if __name__ == "__main__":
    print("\n" + "="*30)
    print("🤖 FINSTREET TRADING BOT")
    print("="*30)
    
    signal = get_latest_signal()
    if signal is not None:
        execute_trade(signal)
    print("="*30 + "\n")
