import yfinance as yf
import yaml
import time
import pandas as pd
from datetime import datetime, timedelta
from hermes_trading.db import supabase

# Pure Python RSI implementation
def calculate_rsi(prices, period=14):
    if len(prices) < period + 1: return 50.0
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0: return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def run_evolutionary_backtest(symbol="NVDA"):
    # Evolutionary settings
    windows = {"1w": timedelta(weeks=1)}
    
    # Get strategy
    response = supabase.table("settings").select("value").eq("key", "strategy").single().execute()
    strat = yaml.safe_load(response.data["value"])
    threshold = strat["entry"]["threshold"]
    print(f"Running backtest with threshold: {threshold}")
    
    for name, delta in windows.items():
        start_date = datetime.now() - delta
        hist = yf.download(symbol, start=start_date, interval="1m", progress=False)
        
        if hist.empty:
            print(f"No data for {symbol}")
            continue
            
        # Robust price extraction
        prices = hist['Close'].values.flatten().tolist()
        print(f"Loaded {len(prices)} prices.")
        
        trades_count = 0
        for i in range(14, len(prices)):
            rsi = calculate_rsi(prices[:i])
            if rsi < threshold:
                # Log as past_evol_trade
                try:
                    supabase.table("past_evol_trade").insert({
                        "ts": time.time(),
                        "asset": f"{symbol}/USDT",
                        "outcome": f"evol_rsi_{rsi:.1f}"
                    }).execute()
                    trades_count += 1
                except Exception as e:
                    print(f"DB Error: {e}")

    print(f"Evolutionary backtest complete. Logged {trades_count} trades.")

if __name__ == "__main__":
    run_evolutionary_backtest()
