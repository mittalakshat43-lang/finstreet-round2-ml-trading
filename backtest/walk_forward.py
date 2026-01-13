import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# =========================
# 🔹 CONFIGURATION
# =========================
INITIAL_CAPITAL = 100000    # ₹1 Lakh
BROKERAGE_PCT = 0.0005      # 0.05% per trade (roughly Brokerage + STT)

BASE_DIR = os.getcwd()
ORDER_BOOK_PATH = os.path.join(BASE_DIR, "data", "processed", "final_order_book.csv")
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "rites_daily.csv")
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")

def run_backtest():
    print("⏳ Starting Chronological Walk-Forward Backtest...")
    
    # 1. LOAD DATA
    if not os.path.exists(ORDER_BOOK_PATH) or not os.path.exists(RAW_DATA_PATH):
        print("❌ Error: Missing input files. Run main.py first.")
        return

    # Load planned trades
    orders_df = pd.read_csv(ORDER_BOOK_PATH)
    orders_df["date"] = pd.to_datetime(orders_df["date"])

    # Load actual market history (The "Answer Key")
    market_df = pd.read_csv(RAW_DATA_PATH)
    market_df["date"] = pd.to_datetime(market_df["date"])

    # Merge to align Plan with Reality
    backtest_df = pd.merge(orders_df, market_df, on="date", how="inner")
    
    if backtest_df.empty:
        print("⚠️ No overlapping dates found between Orders and Market Data.")
        print("   (Check if your rites_daily.csv actually contains Jan 2026 data)")
        return

    print(f"📊 Simulating {len(backtest_df)} trading days...")
    print("="*100)
    print(f"{'DATE':<12} | {'SIGNAL':<6} | {'ENTRY':<8} | {'STOP LOSS':<9} | {'EXIT':<8} | {'REASON':<10} | {'PnL (₹)':<10} | {'BALANCE'}")
    print("="*100)

    # 2. SIMULATION LOOP
    current_capital = INITIAL_CAPITAL
    capital_history = [INITIAL_CAPITAL]
    dates = [backtest_df.iloc[0]["date"] - pd.Timedelta(days=1)] # Start point for chart

    results = []

    for i, row in backtest_df.iterrows():
        signal = row["signal"]
        qty = row["qty"]
        planned_sl = row["stop_loss"]
        
        # Market Data for the day
        open_price = row["open"]
        high_price = row["high"]
        low_price = row["low"]
        close_price = row["close"]

        pnl = 0
        exit_price = 0
        reason = "-"
        
        if signal == "BUY" and qty > 0:
            # Entry assumption: We enter at the OPEN price
            entry_price = open_price 
            
            # --- CHECK STOP LOSS ---
            # Did the stock dip below our SL during the day?
            if low_price <= planned_sl:
                exit_price = planned_sl
                reason = "SL HIT 🛑"
            else:
                # If SL not hit, we exit at Market Close (Day Trade)
                exit_price = close_price
                reason = "CLOSE 🟢"

            # Gross PnL
            gross_pnl = (exit_price - entry_price) * qty
            
            # Transaction Costs (Entry + Exit)
            turnover = (entry_price * qty) + (exit_price * qty)
            costs = turnover * BROKERAGE_PCT
            
            pnl = gross_pnl - costs
        
        else:
            reason = "NO TRADE"

        # Update Balance
        current_capital += pnl
        capital_history.append(current_capital)
        dates.append(row["date"])

        print(f"{row['date'].date()} | {signal:<6} | {open_price:<8.2f} | {planned_sl:<9.2f} | {exit_price:<8.2f} | {reason:<10} | {pnl:<10.2f} | {current_capital:,.2f}")

        results.append({
            "date": row["date"],
            "daily_return": pnl
        })

    # 3. CALCULATE METRICS
    results_df = pd.DataFrame(results)
    
    # Net PnL
    net_pnl = current_capital - INITIAL_CAPITAL
    roi = (net_pnl / INITIAL_CAPITAL) * 100
    
    # Sharpe Ratio (Daily)
    # Note: For short periods (8 days), Sharpe is volatile. We annualize it.
    daily_returns = results_df["daily_return"] / INITIAL_CAPITAL
    mean_return = daily_returns.mean()
    std_return = daily_returns.std()
    
    if std_return == 0:
        sharpe = 0
    else:
        sharpe = (mean_return / std_return) * np.sqrt(252)

    # Max Drawdown
    equity_curve = np.array(capital_history)
    peak = np.maximum.accumulate(equity_curve)
    drawdown = (equity_curve - peak) / peak
    max_drawdown = drawdown.min()

    print("="*100)
    print("\n🏆 FINAL PERFORMANCE REPORT")
    print("-" * 30)
    print(f"💰 Final Capital:    ₹{current_capital:,.2f}")
    print(f"💵 Net Profit:       ₹{net_pnl:,.2f} ({roi:.2f}%)")
    print(f"📉 Max Drawdown:     {max_drawdown:.2%}")
    print(f"⚡ Sharpe Ratio:     {sharpe:.2f} (Target > 1.5)")
    print("-" * 30)

    # 4. PLOT & SAVE CHART
    plt.figure(figsize=(10, 5))
    plt.plot(dates, capital_history, marker='o', linestyle='-', color='green', linewidth=2)
    plt.title(f"Equity Curve: {roi:.2f}% Return")
    plt.xlabel("Date")
    plt.ylabel("Account Value (₹)")
    plt.grid(True)
    plt.axhline(y=INITIAL_CAPITAL, color='r', linestyle='--', label="Initial Capital")
    plt.legend()
    
    chart_path = os.path.join(ARTIFACTS_DIR, "performance_chart.png")
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    plt.savefig(chart_path)
    print(f"📈 Performance Chart saved to: {chart_path}")
    # plt.show() # Uncomment if you want to see the popup

if __name__ == "__main__":
    run_backtest()
