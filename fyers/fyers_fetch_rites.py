
from fyers_apiv3 import fyersModel
from fyers_apiv3 import accessToken
import pandas as pd
import webbrowser
import time

# =====================================================
# 1️⃣ ENTER YOUR DETAILS HERE ONLY
# =====================================================
APP_ID = 6N3D2EQCU5-100
SECRET_KEY = JVU3RW4QQY
REDIRECT_URI = "https://www.google.com"

# =====================================================
# 2️⃣ GENERATE AUTH URL (one-time login)
# =====================================================
session = accessToken.SessionModel(
    client_id=APP_ID,
    secret_key=SECRET_KEY,
    redirect_uri=REDIRECT_URI,
    response_type="code",
    grant_type="authorization_code"
)

auth_url = session.generate_authcode()

print("\n🔗 Opening browser for FYERS login...")
webbrowser.open(auth_url)

# =====================================================
# 3️⃣ USER PASTES AUTH CODE
# =====================================================
auth_code = input("\nPaste the auth_code from browser URL here: ").strip()

session.set_token(auth_code)
response = session.generate_token()

access_token = response["access_token"]
print("✅ Access token generated")

# =====================================================
# 4️⃣ INITIALIZE FYERS
# =====================================================
fyers = fyersModel.FyersModel(
    client_id=APP_ID,
    token=access_token,
    log_path="."
)

# =====================================================
# 5️⃣ FETCH DAILY OHLCV DATA (RITES)
# =====================================================
data = {
    "symbol": "NSE:RITES-EQ",
    "resolution": "D",
    "date_format": "1",
    "range_from": "2025-11-01",
    "range_to": "2025-12-31",
    "cont_flag": "1"
}

print("📥 Fetching RITES daily data...")
response = fyers.history(data=data)

candles = response["candles"]

df = pd.DataFrame(
    candles,
    columns=["timestamp", "open", "high", "low", "close", "volume"]
)

df["date"] = pd.to_datetime(df["timestamp"], unit="s").dt.date
df = df.drop(columns=["timestamp"])
df = df[["date", "open", "high", "low", "close", "volume"]]

# =====================================================
# 6️⃣ SAVE CSV
# =====================================================
df.to_csv("rites_daily.csv", index=False)
print("✅ Data saved as rites_daily.csv")

print("\n🎉 DONE! Upload this CSV to GitHub.")
