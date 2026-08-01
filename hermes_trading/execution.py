import asyncio
import subprocess
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
            print("Market Closed: Running evolutionary backtest.")
            # Run evolution script as a subprocess
            subprocess.run(["python", "-m", "hermes_trading.execution2"], check=True)
            await asyncio.sleep(3600) # Sleep for an hour

if __name__ == "__main__":
    asyncio.run(live_execution())
