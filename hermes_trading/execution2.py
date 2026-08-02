import yfinance as yf
import yaml
import time
import numpy as np
from datetime import datetime, timedelta
from hermes_trading.db import supabase
from hermes_trading.ai import QLearner

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

def get_bb_pos(prices, period=20, k=2):
    if len(prices) < period: return 1
    sma = sum(prices[-period:]) / period
    std = np.std(prices[-period:])
    upper = sma + (k * std)
    lower = sma - (k * std)
    current = prices[-1]
    if current > upper: return 2
    if current < lower: return 0
    return 1

def run_rl_evolution(symbol="NVDA"):
    # Goal
    with open("state/goal.yaml", "r") as f:
        goal = yaml.safe_load(f)
    
    # RL Brain
    ai = QLearner()
    
    # Target 2022-2026 data
    start_date = datetime(2022, 1, 1)
    hist = yf.download(symbol, start=start_date, interval="1d", progress=False)
    prices = hist['Close'].values.flatten().tolist()
    
    # Simulation
    total_profit = 0.0
    for i in range(20, len(prices)):
        rsi = calculate_rsi(prices[:i])
        log_ret = np.log(prices[i]/prices[i-1])
        bb_pos = get_bb_pos(prices[:i])
        
        state = ai.get_state(rsi, log_ret, bb_pos)
        action = ai.choose_action(state)
        
        # Reward logic: log return if action is buy, negative if sell wrongly
        reward = log_ret if action == 'buy' else (-log_ret if action == 'sell' else 0)
        total_profit += reward
        
        next_state = ai.get_state(calculate_rsi(prices[:i+1]), np.log(prices[i+1]/prices[i]), get_bb_pos(prices[:i+1]))
        ai.learn(state, action, reward, next_state)
        
    # Check against goal
    if total_profit < goal["target_return_30d"]:
        print(f"Goal NOT met: {total_profit:.4f}. RL Brain adapting...")
    
    # Log evolution result
    supabase.table("past_evol_trade").insert({
        "ts": time.time(),
        "asset": f"{symbol}/USDT",
        "outcome": f"rl_evol_profit_{total_profit:.4f}"
    }).execute()

if __name__ == "__main__":
    run_rl_evolution()
