# main.py (Updated to Save CSV)

import pandas as pd
import numpy as np
import os

# =========================
# 🔹 CONFIGURATION
# =========================
CAPITAL = 100000            
RISK_PER_TRADE = 0.02       
ATR_MULTIPLIER = 1.5        

BASE_DIR = os.getcwd()
PREDICTIONS_PATH = os.path.join(BASE_DIR, "data", "processed", "jan_predictions.csv")
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "rites_daily.csv")
ORDER_BOOK_PATH = os.path.join(BASE_DIR, "data", "processed", "final_order_book.csv")

def calculate_atr(df, period=14):
    df['tr0'] = abs(df["high"] - df["low"])
    df['tr1'] = abs(df["high"] - df["close"].shift())
    df['tr2'] = abs(df["low"] - df["close"].shift())
    df['tr'] = df[['tr0', 'tr1', 'tr2']].max(axis=1)
    df['atr'] = df['tr'].rolling(window=period).mean().fillna(0)
    return df

def execute_strategy():
    print("⚙️  Calculating Strategy Rules...")
    
    if not os.path.exists(PREDICTIONS_PATH):
        print("❌ Error: Run predict.py first.")
        return

    preds_df = pd.read_csv(PREDICTIONS_PATH)
    preds_df["date"] = pd.to_datetime(preds_df["date"])

    raw_df = pd.read_csv(RAW_DATA_PATH)
    raw_df["date"] = pd.to_datetime(raw_df["date"])
    raw_df = calculate_atr(raw_df)

    order_book = []

    for i, row in preds_df.iterrows():
        trade_date = row["date"]
        signal = row["prediction"]
        
        # Get data strictly BEFORE trade date to calculate ATR
        past_data = raw_df[raw_df["date"] < trade_date]
        if past_data.empty: continue
            
        current_atr = past_data.iloc[-1]["atr"]
        entry_price = past_data.iloc[-1]["close"] # Assumption for planning: Last Close ~ Next Open
        
        if signal == 1: # BUY
            stop_loss = entry_price - (current_atr * ATR_MULTIPLIER)
            risk_per_share = entry_price - stop_loss
            
            quantity = 0
            if risk_per_share > 0:
                total_risk_amount = CAPITAL * RISK_PER_TRADE
                quantity = int(total_risk_amount / risk_per_share)
                
                # Cap quantity at Max Cash
                quantity = min(quantity, int(CAPITAL / entry_price))

            order_book.append({
                "date": trade_date.date(),
                "signal": "BUY",
                "qty": quantity,
                "stop_loss": round(stop_loss, 2),
                "approx_entry": entry_price
            })
        else:
            order_book.append({
                "date": trade_date.date(),
                "signal": "WAIT",
                "qty": 0,
                "stop_loss": 0,
                "approx_entry": 0
            })

    # SAVE TO CSV
    order_df = pd.DataFrame(order_book)
    order_df.to_csv(ORDER_BOOK_PATH, index=False)
    print(f"✅ Final Order Book saved to: {ORDER_BOOK_PATH}")
    print(order_df.head(8))

if __name__ == "__main__":
    execute_strategy()
