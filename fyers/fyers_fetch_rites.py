import os
import webbrowser
import pandas as pd
from fyers_apiv3 import fyersModel

# =========================
# 🔹 UNIVERSAL PATH SETUP
# =========================
# Go up one level from 'fyers/' to get the Project Root ('New folder')
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR) 

# Define central paths
DATA_RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
TOKEN_PATH = os.path.join(PROJECT_ROOT, "access_token.txt")

os.makedirs(DATA_RAW_DIR, exist_ok=True)

# =========================
# 🔹 AUTHENTICATION
# =========================
CLIENT_ID = "6N3D2EQCU5-100" 
SECRET_KEY = "JVU3RW4QQY"
REDIRECT_URI = "https://www.google.com/"

session = fyersModel.SessionModel(
    client_id=CLIENT_ID, secret_key=SECRET_KEY, redirect_uri=REDIRECT_URI, 
    response_type="code", grant_type="authorization_code"
)

# Only open browser if we don't have a valid token (Optional logic, keeping it simple)
auth_url = session.generate_authcode()
print(f"🌍 Opening Login: {auth_url}")
webbrowser.open(auth_url)

auth_code = input("Paste auth_code from URL: ").strip()
session.set_token(auth_code)
response = session.generate_token()

if "access_token" in response:
    with open(TOKEN_PATH, "w") as f:
        f.write(response["access_token"])
    print(f"✅ Token saved to: {TOKEN_PATH}")
    access_token = response["access_token"]
else:
    raise Exception(f"Auth Failed: {response}")

# =========================
# 🔹 FETCH & SAVE
# =========================
fyers = fyersModel.FyersModel(client_id=CLIENT_ID, token=access_token, log_path=PROJECT_ROOT)

data_params = {
    "symbol": "NSE:RITES-EQ", "resolution": "D", "date_format": "1", 
    "range_from": "2025-11-01", "range_to": "2026-01-08", "cont_flag": "1"
}

print("Fetching Data...")
response = fyers.history(data=data_params)

if "candles" in response:
    cols = ["timestamp", "open", "high", "low", "close", "volume"]
    df = pd.DataFrame(response["candles"], columns=cols)
    df["date"] = pd.to_datetime(df["timestamp"], unit="s")
    
    # Save to the central data folder
    save_path = os.path.join(DATA_RAW_DIR, "rites_daily.csv")
    df.to_csv(save_path, index=False)
    print(f"✅ Data saved to: {save_path}")
else:
    print("❌ Error fetching data:", response)
