import asyncio
from hermes_trading.clock import is_market_open
from hermes_trading.loop import run_loop
import yaml

async def live_execution():
    print("Sentinel Active: Monitoring market status...")
    with open("state/goal.yaml", "r") as f:
        goal = yaml.safe_load(f)
        
    while True:
        if is_market_open():
            print("Market Open: Running live loop.")
            await run_loop(goal["asset"], goal)
        else:
            print("Market Closed: Sleeping.")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(live_execution())
