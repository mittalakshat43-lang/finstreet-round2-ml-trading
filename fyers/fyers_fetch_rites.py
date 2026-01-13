# fyers_fetch_rites.py

from fyers_apiv3 import fyersModel
import pandas as pd
import webbrowser
import os

# =========================
# 🔹 CONFIGURATION
# =========================
CLIENT_ID = "6N3D2EQCU5-100" 
SECRET_KEY = "JVU3RW4QQY"
REDIRECT_URI = "https://www.google.com/"

# 📂 STRICT PATH SETUP
# This gets the folder where THIS script is currently living.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# We force the data folder to be created inside this same folder
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
TOKEN_PATH = os.path.join(BASE_DIR, "access_token.txt")

# Create the folder if it doesn't exist
os.makedirs(DATA_RAW_DIR, exist_ok=True)

print(f"📂 Working Directory: {BASE_DIR}")
print(f"📂 Saving Data to:    {DATA_RAW_DIR}")

# =========================
# 🔹 AUTHENTICATION
# =========================
session = fyersModel.SessionModel(
    client_id=CLIENT_ID,
    secret_key=SECRET_KEY,
    redirect_uri=REDIRECT_URI,
    response_type="code",
    grant_type="authorization_code"
)

# Check if we already have a token
if os.path.exists(TOKEN_PATH):
    with open(TOKEN_PATH, "r") as f:
        access_token = f.read().strip()
    print("✅ Found existing access token.")
else:
    auth_url = session.generate_authcode()
    print(f"🌍 Opening Login: {auth_url}")
    webbrowser.open(auth_url)

    auth_code = input("Paste auth_code from URL here: ").strip()
    session.set_token(auth_code)
    response = session.generate_token()

    if "access_token" in response:
        access_token = response["access_token"]
        with open(TOKEN_PATH, "w") as f:
            f.write(access_token)
        print("✅ New token generated and saved!")
    else:
        raise Exception(f"Auth Failed: {response}")

# =========================
# 🔹 FETCH DATA (Correct Range: Nov 1 - Jan 8)
# =========================
fyers = fyersModel.FyersModel(client_id=CLIENT_ID, token=access_token, log_path=BASE_DIR)

data_params = {
    "symbol": "NSE:RITES-EQ",
    "resolution": "D",
    "date_format": "1",
    "range_from": "2025-11-01", 
    "range_to": "2026-01-08",    # <--- Includes the prediction week
    "cont_flag": "1"
}

print("⏳ Fetching OHLCV data...")
response = fyers.history(data=data_params)

if "candles" in response:
    cols = ["timestamp", "open", "high", "low", "close", "volume"]
    df = pd.DataFrame(response["candles"], columns=cols)
    
    df["date"] = pd.to_datetime(df["timestamp"], unit="s")
    df = df[["date", "open", "high", "low", "close", "volume"]]

    # Save exactly inside the project folder
    output_file = os.path.join(DATA_RAW_DIR, "rites_daily.csv")
    df.to_csv(output_file, index=False)

    print(f"✅ Data successfully saved to:\n{output_file}")
    print(f"📅 Data Range: {df['date'].min().date()} to {df['date'].max().date()}")
else:
    print("❌ Error fetching data:", response)
