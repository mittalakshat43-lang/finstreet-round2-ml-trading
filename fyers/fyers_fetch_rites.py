# fyers_fetch_rites.py
# Fetch daily OHLCV data for RITES using FYERS API

from fyers_apiv3 import fyersModel
import pandas as pd
import webbrowser
import datetime
import os

# =========================
# 🔹 ENTER YOUR DETAILS
# =========================
CLIENT_ID = "6N3D2EQCU5-100"        # format: ABCD1234-100
SECRET_KEY = "JVU3RW4QQY"
REDIRECT_URI = "https://www.google.com/"

# =========================
# 🔹 STEP 1: Generate Auth Code URL
# =========================
session = fyersModel.SessionModel(
    client_id= "6N3D2EQCU5-100",
    secret_key= "JVU3RW4QQY",
    redirect_uri="https://www.google.com/",
    response_type="code",
    grant_type="authorization_code"
)

auth_url = session.generate_authcode()
print("Opening browser for FYERS login...")
webbrowser.open(auth_url)

# =========================
# 🔹 STEP 2: Paste Auth Code
# =========================
auth_code = input("Paste auth_code from URL here: ").strip()

session.set_token(auth_code)
response = session.generate_token()

if "access_token" in response:
    access_token = response["access_token"]
    
    # This line is the "Bridge". It saves the pass for the next script.
    with open("access_token.txt", "w") as f:
        f.write(access_token)
print("Access token generated successfully!")

# =========================
# 🔹 STEP 3: Initialize FYERS
# =========================
fyers = fyersModel.FyersModel(
    client_id= "6N3D2EQCU5-100",
    token=access_token,
    log_path=os.getcwd()
)

# =========================
# 🔹 STEP 4: Fetch OHLCV Data (RITES)
# =========================
data = {
    "symbol": "NSE:RITES-EQ",
    "resolution": "D",
    "date_format": "1",
    "range_from": "2025-11-01",
    "range_to": "2025-12-31",
    "cont_flag": "1"
}

print("Fetching OHLCV data from FYERS...")
response = fyers.history(data=data)

if "candles" not in response:
    raise Exception(f"Error fetching data: {response}")

# =========================
# 🔹 STEP 5: Convert to DataFrame
# =========================
cols = ["timestamp", "open", "high", "low", "close", "volume"]
df = pd.DataFrame(response["candles"], columns=cols)

df["date"] = pd.to_datetime(df["timestamp"], unit="s")
df = df[["date", "open", "high", "low", "close", "volume"]]

# =========================
# 🔹 STEP 6: Save CSV
# =========================
output_file = "rites_daily.csv"
df.to_csv(output_file, index=False)

print(f"✅ Data saved successfully as {output_file}")
print(df.head())

