import asyncio
import time
import os
import httpx
from hermes_trading.adapters import price, onchain, news, macro
from hermes_trading.db import supabase
from hermes_trading.patterns import get_patterns

# RSI helper
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

async def run_loop(asset, goal):
    print(f"Starting loop for {asset}")
    alpaca_url = "https://paper-api.alpaca.markets/v2/orders"
    headers = {
        "APCA-API-KEY-ID": os.environ.get("ALPACA_API_KEY"),
        "APCA-API-SECRET-KEY": os.environ.get("ALPACA_SECRET_KEY"),
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        while True:
            try:
                # 1. Pull data
                price_data = await price.fetch(asset)
                bars = price_data['bars']
                current_price = price_data['current_price']
                
                # 2. Analyze
                closing_prices = [b['close'] for b in bars]
                rsi = calculate_rsi(closing_prices)
                patterns = get_patterns(bars)
                
                pat_str = " | ".join(patterns) if patterns else "Scanning"
                print(f"Symbol: {asset} | Price: {current_price} | RSI: {rsi:.2f} | Patterns: {pat_str}")

                # 3. Decision Logic (Only BUY if RSI < 30 and pattern exists)
                if rsi < 30 and patterns:
                    payload = {
                        "symbol": asset.split('/')[0],
                        "qty": 1,
                        "side": "buy",
                        "type": "market",
                        "time_in_force": "gtc"
                    }
                    await client.post(alpaca_url, headers=headers, json=payload)
                    
                    supabase.table("trades").insert({
                        "ts": time.time(),
                        "asset": asset,
                        "outcome": f"live_trade_{rsi:.1f}_{pat_str}"
                    }).execute()
                    print(f"Trade placed for {asset} based on RSI and Pattern")
                
                await asyncio.sleep(60)
            except Exception as e:
                print(f"Error in loop: {e}")
                await asyncio.sleep(60)
