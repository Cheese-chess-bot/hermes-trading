import asyncio
import json
import yaml
import time
from hermes_trading.adapters import price, onchain, news, macro

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
            
            # 2. Evaluate strategy (simplified)
            # ... trade logic ...
            
            # 3. Log
            with open("state/trades.jsonl", "a") as f:
                f.write(json.dumps({"ts": time.time(), "asset": asset, "outcome": "paper_trade"}) + "\n")
            
            # 4. Heartbeat
            with open("state/heartbeat.json", "w") as f:
                json.dump({"ts": time.time(), "status": "ok"}, f)
                
            await asyncio.sleep(60)
        except Exception as e:
            print(f"Error in loop: {e}")
            await asyncio.sleep(60)
