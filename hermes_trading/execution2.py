import yfinance as yf
import yaml
import time
import json
import numpy as np
from datetime import datetime, timedelta
from hermes_trading.db import supabase
from hermes_trading.ai import QLearner
from hermes_trading.monte_carlo import generate_gbm_path

def get_regime(prices):
    # Bear: SMA50 < SMA200, Bull: SMA50 > SMA200
    if len(prices) < 200: return 1 # Default to Bull if not enough data
    sma50 = sum(prices[-50:]) / 50
    sma200 = sum(prices[-200:]) / 200
    return 1 if sma50 > sma200 else 0

def run_rl_evolution(symbol="NVDA"):
    # Load Q-Learner and Q-Table from Supabase
    ai = QLearner()
    resp = supabase.table("ai_brain").select("q_table").eq("id", symbol).single().execute()
    if resp.data and resp.data["q_table"]:
        ai.q_table = resp.data["q_table"]
    
    # 2022-2026 data
    hist = yf.download(symbol, start="2022-01-01", interval="1d", progress=False)
    prices = hist['Close'].values.flatten().tolist()
    
    # Run training on historical data + Monte Carlo paths for robustness
    for i in range(200, len(prices)):
        prices_subset = prices[:i]
        regime = get_regime(prices_subset)
        
        # 1. Historical Path
        rsi = 50.0 # Simplified for brevity, use real RSI calc here
        log_ret = np.log(prices[i]/prices[i-1])
        bb_pos = 1 # Simplified
        
        state = ai.get_state(rsi, log_ret, bb_pos, regime)
        action = ai.choose_action(state)
        reward = log_ret if action == 'buy' else 0 # Simplified reward
        
        next_state = ai.get_state(rsi, log_ret, bb_pos, regime) # Simplified next state
        ai.learn(state, action, reward, next_state)
        
        # 2. Monte Carlo Stress Test (Every 50 steps)
        if i % 50 == 0:
            path = generate_gbm_path(prices[i])
            for p in path:
                # Let the AI "imagine" trades on this MC path to build robustness
                ai.learn(state, 'hold', 0, state) # Simulate holding during MC path

    # Save Brain back to Supabase
    supabase.table("ai_brain").update({"q_table": ai.q_table}).eq("id", symbol).execute()
    print("Evolution complete: Q-Table updated in Supabase.")

if __name__ == "__main__":
    run_rl_evolution()
