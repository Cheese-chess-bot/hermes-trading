import asyncio
import time
import os
import argparse
import yfinance as yf
import pandas as pd
from datetime import datetime
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

async def run_backtest(symbol="NVDA", period="2y", interval="1m"):
    print(f"Fetching historical {interval} data for {symbol} (period: {period})...")
    # yfinance handles period strings like '1mo', '1y', 'max'
    df = yf.download(symbol, period=period, interval=interval, progress=False)
    
    if df.empty:
        print("No historical data found.")
        return

    print(f"Loaded {len(df)} candles. Running simulation loop...")

    trades_executed = 0
    prices = df['Close'].tolist()

    for i in range(14, len(prices)):
        close_price = float(prices[i])
        rsi_val = calculate_rsi(prices[:i])

        # Strategy check: Buy when RSI < 30
        if rsi_val < 30:
            trades_executed += 1
            ts_seconds = datetime.now().timestamp()
            
            # Log to Supabase as past_trade (Simulation)
            try:
                supabase.table("trades").insert({
                    "ts": ts_seconds,
                    "asset": f"{symbol}/USDT",
                    "outcome": f"backtest_buy_price_{close_price:.2f}_rsi_{rsi_val:.1f}"
                }).execute()
                print(f"[{i}] BUY signal | Price: ${close_price:.2f} | RSI: {rsi_val:.1f}")
            except Exception as e:
                print(f"Supabase logging error: {e}")

    print(f"\nBacktest complete. Total trades simulated: {trades_executed}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--period", default="2y", help="Historical data period (e.g., 7d, 1mo, 1y, max)")
    args = parser.parse_args()
    asyncio.run(run_backtest(period=args.period))
