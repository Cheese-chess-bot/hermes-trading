import asyncio
import json
import yaml
import time
from hermes_trading.adapters import price, onchain, news, macro
from hermes_trading.db import supabase

async def run_loop(asset, goal):
    print(f"Starting loop for {asset}")
    while True:
        try:
            # 1. Pull data
            data = await asyncio.gather(
                price.fetch(asset),
                onchain.fetch(asset),
                news.fetch(asset),
                macro.fetch(asset)
            )
            
            # 2. Log outcome to Supabase
            supabase.table("trades").insert({
                "ts": time.time(),
                "asset": asset,
                "outcome": "paper_trade"
            }).execute()
            
            # 3. Heartbeat
            # (Supabase can be used to store heartbeats)
            
            await asyncio.sleep(60)
        except Exception as e:
            print(f"Error in loop: {e}")
            await asyncio.sleep(60)
