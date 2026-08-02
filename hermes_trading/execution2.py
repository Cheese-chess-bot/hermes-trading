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
    # Load AI and Q-Table
    ai = QLearner()
    try:
        resp = supabase.table("ai_brain").select("q_table").eq("id", symbol).single().execute()
        if resp.data and resp.data["q_table"]:
            ai.q_table = resp.data["q_table"]
            print(f"Loaded existing Q-Table with {len(ai.q_table)} states.")
    except Exception as e:
        print(f"Error loading Q-Table: {e}")

    # Data
    hist = yf.download(symbol, start="2022-01-01", interval="1d", progress=False)
    if hist.empty:
        print("No historical data to train on.")
        return
        
    prices = hist['Close'].values.flatten().tolist()
    
    trades_count = 0
    print(f"Starting evolution training on {len(prices)} candles...")

    for i in range(200, len(prices)):
        prices_subset = prices[:i]
        rsi = calculate_rsi(prices_subset)
        log_ret = np.log(prices[i]/prices[i-1])
        bb_pos = 1 
        regime = get_regime(prices_subset)
        
        state = ai.get_state(rsi, log_ret, bb_pos, regime)
        action = ai.choose_action(state)
        
        # Reward
        reward = log_ret if action == 'buy' else (-log_ret if action == 'sell' else 0)
        
        # Learn
        next_state = ai.get_state(rsi, log_ret, bb_pos, regime)
        ai.learn(state, action, reward, next_state)
        
        # Log to past_evol_trade if specific trigger
        if rsi < 30: # Trigger condition
            try:
                supabase.table("past_evol_trade").insert({
                    "ts": time.time(),
                    "asset": f"{symbol}/USDT",
                    "outcome": f"evol_rsi_{rsi:.1f}_action_{action}"
                }).execute()
                trades_count += 1
            except Exception as e:
                print(f"DB Error: {e}")

    print(f"Training complete. Trades logged: {trades_count}, Q-Table states: {len(ai.q_table)}")
    
    # Save Brain
    try:
        supabase.table("ai_brain").upsert({"id": symbol, "q_table": ai.q_table}).execute()
        print("Saved Q-Table to Supabase.")
    except Exception as e:
        print(f"Save Error: {e}")

if __name__ == "__main__":
    run_rl_evolution()
