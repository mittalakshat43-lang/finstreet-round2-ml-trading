# orders.py

import pandas as pd
import os
import datetime
from fyers_apiv3 import fyersModel

# =========================
# 🔹 CONFIGURATION
# =========================
CLIENT_ID = "6N3D2EQCU5-100"  # Your App ID
BASE_DIR = os.getcwd()
ORDER_BOOK_PATH = os.path.join(BASE_DIR, "data", "processed", "final_order_book.csv")
TOKEN_PATH = os.path.join(BASE_DIR, "access_token.txt")

# 🛑 FOR TESTING: You can hardcode a date here to force a test trade
# Example: FORCE_DATE = "2026-01-02"
FORCE_DATE = None 

def get_access_token():
    if not os.path.exists(TOKEN_PATH):
        print("❌ Error: access_token.txt not found.")
        return None
    with open(TOKEN_PATH, "r") as f:
        return f.read().strip()

def place_order():
    print("\n🚀 FINSTREET ORDER EXECUTION SYSTEM")
    print("="*40)

    # 1. DETERMINE "TODAY"
    if FORCE_DATE:
        today_str = FORCE_DATE
        print(f"⚠️ TEST MODE: Forcing execution for date: {today_str}")
    else:
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        print(f"📅 System Date: {today_str}")

    # 2. LOAD ORDER BOOK
    if not os.path.exists(ORDER_BOOK_PATH):
        print("❌ Error: Order book not found. Run main.py first.")
        return

    df = pd.read_csv(ORDER_BOOK_PATH)
    
    # 3. FIND TODAY'S SIGNAL
    # Filter where 'date' column matches today
    todays_plan = df[df["date"] == today_str]

    if todays_plan.empty:
        print("⏸️ No plan found for today in the Order Book.")
        return

    signal = todays_plan.iloc[0]["signal"]
    qty = int(todays_plan.iloc[0]["qty"])
    stop_loss = float(todays_plan.iloc[0]["stop_loss"])

    print(f"📋 Plan for Today: {signal} | Qty: {qty} | SL: {stop_loss}")

    # 4. EXECUTE IF BUY
    if signal == "BUY" and qty > 0:
        token = get_access_token()
        if not token: return

        fyers = fyersModel.FyersModel(client_id=CLIENT_ID, token=token, log_path=BASE_DIR)
        
        # Validate Token
        if fyers.get_profile().get('s') != 'ok':
            print("❌ API Error: Token Expired. Run fetch script.")
            return

        print(f"⚡ Placing BUY Order for {qty} shares of RITES...")

        data = {
            "symbol": "NSE:RITES-EQ",
            "qty": qty,
            "type": 2,           # 2 = Market Order
            "side": 1,           # 1 = Buy
            "productType": "INTRADAY",
            "limitPrice": 0,
            "stopPrice": 0,
            "validity": "DAY",
            "disclosedQty": 0,
            "offlineOrder": "False"
        }

        try:
            response = fyers.place_order(data=data)
            
            if response.get("s") == "ok":
                order_id = response.get("id")
                print(f"✅ SUCCESS! Order Placed. ID: {order_id}")
                
                # Optional: Place Stop Loss Order (Cover Order logic or separate SL-M)
                # Note: Fyers API requires separate calls for SL usually, or use BO/CO productType
                print(f"🛡️ REMINDER: Manually verify Stop Loss is set at ₹{stop_loss}")
                
            else:
                print(f"❌ Order Failed: {response.get('message')}")
        
        except Exception as e:
            print(f"❌ API Exception: {e}")

    else:
        print("😴 No Action Required. Staying Cash.")

    print("="*40)

if __name__ == "__main__":
    place_order()
