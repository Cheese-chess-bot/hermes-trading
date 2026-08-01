import yfinance as yf
import yaml
import time
from datetime import datetime, timedelta
from hermes_trading.db import supabase
from hermes_trading.patterns import get_patterns

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
    windows = {"1d": timedelta(days=1), "1w": timedelta(weeks=1)}
    
    response = supabase.table("settings").select("value").eq("key", "strategy").single().execute()
    strat = yaml.safe_load(response.data["value"])
    
    for name, delta in windows.items():
        start_date = datetime.now() - delta
        # Ensure symbol format is yfinance-friendly
        hist = yf.download(symbol, start=start_date, interval="1m", progress=False)
        
        if hist.empty:
            print(f"No data for {symbol}")
            continue
            
        prices = hist['Close'].iloc[:, 0].tolist()
        
        for i in range(14, len(prices)):
            rsi = calculate_rsi(prices[:i])
            # Simplified trigger for evolution
            if rsi < strat["entry"]["threshold"]:
                # Log as past_evol_trade
                supabase.table("past_evol_trade").insert({
                    "ts": time.time(),
                    "asset": f"{symbol}/USDT",
                    "outcome": f"evol_rsi_{rsi:.1f}"
                }).execute()

    print("Evolutionary backtest complete. Logged to past_evol_trade.")

if __name__ == "__main__":
    run_evolutionary_backtest()
