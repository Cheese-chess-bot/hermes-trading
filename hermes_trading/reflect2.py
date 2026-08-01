import yfinance as yf
import yaml
import json
import time
from datetime import datetime, timedelta
from hermes_trading.db import supabase

# Pure Python RSI implementation to avoid Pandas dependency
def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return None
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def run_reflection_cycle(strat, trades_data):
    # Analyze performance, mutate ONE variable
    total_pnl = sum([t['pnl'] for t in trades_data])
    if total_pnl < 0:
        strat["entry"]["threshold"] += 2  # Loosen threshold
    
    strat["version"] = str(int(strat["version"]) + 1).zfill(2)
    return strat

def run_evolutionary_backtest(symbol="NVDA"):
    windows = {
        "1d": timedelta(days=1),
        "1w": timedelta(weeks=1),
        "1m": timedelta(days=30),
    }
    
    response = supabase.table("settings").select("value").eq("key", "strategy").single().execute()
    strat = yaml.safe_load(response.data["value"])
    
    for name, delta in windows.items():
        start_date = datetime.now() - delta
        ticker = yf.Ticker(symbol)
        hist = ticker.history(start=start_date, interval="1m")
        prices = hist['Close'].tolist()
        
        trades = []
        trades_count = 0
        
        # Simple backtest
        for i in range(14, len(prices)):
            rsi = calculate_rsi(prices[:i])
            if rsi and rsi < strat["entry"]["threshold"]:
                # Execute simulated buy
                trades.append({"pnl": 0.01}) # placeholder PnL logic
                trades_count += 1
                
                # Log as past_trade
                supabase.table("trades").insert({
                    "ts": time.time(),
                    "asset": f"{symbol}/USDT",
                    "outcome": "past_trade"
                }).execute()
                
                if trades_count >= 5:
                    strat = run_reflection_cycle(strat, trades)
                    trades = []
                    trades_count = 0
                    supabase.table("settings").update({"value": yaml.dump(strat)}).eq("key", "strategy").execute()

    print("Evolutionary backtest complete.")

if __name__ == "__main__":
    run_evolutionary_backtest()
