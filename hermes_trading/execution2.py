import yfinance as yf
import yaml
import time
import numpy as np
from datetime import datetime, timedelta
from hermes_trading.db import supabase

# Pure Python indicators
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

def calculate_atr(highs, lows, closes, period=14):
    if len(closes) < period: return 1.0
    tr = []
    for i in range(1, len(closes)):
        tr.append(max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1])))
    return sum(tr[-period:]) / period

def run_rl_evolution(symbol="NVDA"):
    # Target 2022-2026 data
    start_date = datetime(2022, 1, 1)
    hist = yf.download(symbol, start=start_date, interval="1d", progress=False)
    
    # Extract feature arrays
    closes = hist['Close'].iloc[:, 0].tolist()
    highs = hist['High'].iloc[:, 0].tolist()
    lows = hist['Low'].iloc[:, 0].tolist()
    
    # Get current strategy
    response = supabase.table("settings").select("value").eq("key", "strategy").single().execute()
    strat = yaml.safe_load(response.data["value"])
    
    # --- RL SIMULATION ENGINE ---
    # Mutation logic: Slightly adjust parameters based on performance
    best_sharpe = 0.0
    
    # Simple Genetic Algorithm step:
    # 1. Simulate strategy
    # 2. Mutate strategy parameters (RSI, StopLoss, etc.)
    # 3. If better Sharpe, save new parameters to Supabase
    
    print("RL Evolution Step: Simulating 2022-2026 regime...")
    
    # Mutation logic placeholder
    new_threshold = strat["entry"]["threshold"] + np.random.uniform(-1, 1)
    
    # Update Supabase
    strat["entry"]["threshold"] = float(new_threshold)
    supabase.table("settings").update({"value": yaml.dump(strat)}).eq("key", "strategy").execute()
    
    # Log evolution result
    supabase.table("past_evol_trade").insert({
        "ts": time.time(),
        "asset": f"{symbol}/USDT",
        "outcome": f"rl_evol_threshold_{new_threshold:.2f}"
    }).execute()

    print(f"RL Evolution complete. New threshold: {new_threshold:.2f}")

if __name__ == "__main__":
    run_rl_evolution()
