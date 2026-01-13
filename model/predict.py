# model/predict.py

import os
import joblib
import pandas as pd
from fyers_apiv3 import fyersModel

# --- CONFIGURATION ---
CLIENT_ID = "6N3D2EQCU5-100"
TOKEN_FILE = "access_token.txt"
MODEL_PATH = "model/artifacts/trading_model.pkl"
DATA_PATH = "data/processed/rites_features.csv"

def get_latest_signal():
    """Loads the latest features and predicts tomorrow's move."""
    if not os.path.exists(MODEL_PATH) or not os.path.exists(DATA_PATH):
        print("❌ Model or Features missing!")
        return None

    # Load Model and Data
    model = joblib.load(MODEL_PATH)
    df = pd.read_csv(DATA_PATH)
    
    # Take the VERY LAST row (most recent data)
    # We drop 'date' and 'target' to match training features
    latest_data = df.tail(1).drop(columns=["date", "target"])
    
    prediction = model.predict(latest_data)[0]
    return prediction # 1 for Buy, 0 for No Action/Sell

def execute_trade(signal):
    """Uses FYERS API to place an order based on signal."""
    if not os.path.exists(TOKEN_FILE):
        print("❌ No access token found. Run fetch script first.")
        return

    with open(TOKEN_FILE, "r") as f:
        access_token = f.read().strip()

    fyers = fyersModel.FyersModel(client_id=CLIENT_ID, token=access_token)

    # 1. Check Profile (Risk Management: ensure we have funds)
    profile = fyers.get_profile()
    if profile.get('s') != 'ok':
        print("❌ API Error:", profile)
        return
    
    print(f"💰 Account: {profile['data']['display_name']} | Signal: {'BUY' if signal == 1 else 'WAIT'}")

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
        print("🚀 Order Response:", response)
    else:
        print("⏸️ No buy signal generated. Staying cash.")

if __name__ == "__main__":
    print("🤖 Running Trading Bot...")
    signal = get_latest_signal()
    if signal is not None:
        execute_trade(signal)
