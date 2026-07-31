import asyncio
import time
import os
import httpx
from hermes_trading.adapters import price, onchain, news, macro
from hermes_trading.db import supabase

async def run_loop(asset, goal):
    print(f"Starting loop for {asset}")
    # Raw Alpaca REST API URL
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
                await asyncio.gather(
                    price.fetch(asset),
                    onchain.fetch(asset),
                    news.fetch(asset),
                    macro.fetch(asset)
                )
                
                # 2. Place paper trade via raw HTTP
                payload = {
                    "symbol": asset.split('/')[0],
                    "qty": 1,
                    "side": "buy",
                    "type": "market",
                    "time_in_force": "gtc"
                }
                await client.post(alpaca_url, headers=headers, json=payload)
                
                # 3. Log outcome to Supabase
                supabase.table("trades").insert({
                    "ts": time.time(),
                    "asset": asset,
                    "outcome": "paper_trade_executed"
                }).execute()
                
                print(f"Trade placed for {asset}")
                await asyncio.sleep(60)
            except Exception as e:
                print(f"Error in loop: {e}")
                await asyncio.sleep(60)
