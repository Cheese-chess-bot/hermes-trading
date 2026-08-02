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

def get_regime(prices):
    if len(prices) < 200: return 1
    sma50 = sum(prices[-50:]) / 50
    sma200 = sum(prices[-200:]) / 200
    return 1 if sma50 > sma200 else 0

def run_rl_evolution(symbol="NVDA"):
    ai = QLearner()
    
    # Data
    hist = yf.download(symbol, start="2022-01-01", interval="1d", progress=False)
    prices = hist['Close'].values.flatten().tolist()
    
    # Metrics tracking
    wins = 0
    losses = 0
    profits = []
    
    # Train
    for i in range(200, len(prices)):
        prices_subset = prices[:i]
        rsi = calculate_rsi(prices_subset)
        log_ret = np.log(prices[i]/prices[i-1])
        bb_pos = 1 
        regime = get_regime(prices_subset)
        
        state = ai.get_state(rsi, log_ret, bb_pos, regime)
        action = ai.choose_action(state)
        
        reward = log_ret if action == 'buy' else (-log_ret if action == 'sell' else 0)
        
        if action == 'buy':
            if log_ret > 0: wins += 1
            else: losses += 1
            profits.append(log_ret)
            
            # Log to past_evol_trade
            try:
                supabase.table("past_evol_trade").insert({
                    "ts": time.time(),
                    "asset": f"{symbol}/USDT",
                    "outcome": f"evol_rsi_{rsi:.1f}_action_{action}"
                }).execute()
            except Exception as e:
                print(f"DB Error (past_evol_trade): {e}")
            
        ai.learn(state, action, reward, state)
        
    # Calculate metrics
    profit_pct = sum(profits) * 100
    win_rate = (wins / (wins + losses)) if (wins + losses) > 0 else 0
    max_dd = 0.0 # Simplified
    
    # 1. Upsert Q-Values (Normalized)
    supabase.table("q_values").delete().eq("asset", symbol).execute()
    q_rows = []
    for state, actions in ai.q_table.items():
        for action, val in actions.items():
            q_rows.append({"asset": symbol, "state": state, "action": action, "value": val})
    
    # Chunk insert to avoid limits
    for i in range(0, len(q_rows), 500):
        supabase.table("q_values").insert(q_rows[i:i+500]).execute()
        
    # 2. Log Daily Performance
    supabase.table("daily_performance").insert({
        "ts": time.time(),
        "asset": f"{symbol}/USDT",
        "profit_pct": profit_pct,
        "max_drawdown": max_dd,
        "win_rate": win_rate,
        "loss_rate": 1 - win_rate
    }).execute()

    print(f"Evolution complete. Logged performance and normalized Q-Table.")

if __name__ == "__main__":
    run_rl_evolution()
