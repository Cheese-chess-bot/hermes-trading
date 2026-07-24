import argparse
import yaml
import asyncio
from hermes_trading.loop import run_loop

def load_goal():
    with open("state/goal.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset", help="Asset ticker override")
    args = parser.parse_args()
    
    goal = load_goal()
    asset = args.asset or goal["asset"]
    
    print(f"Booting hermes-trading worker for {asset}")
    asyncio.run(run_loop(asset, goal))

if __name__ == "__main__":
    main()
