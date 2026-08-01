import json
import numpy as np
import pandas as pd
from hermes_trading.db import supabase

def calculate_metrics():
    # Fetch trades from Supabase
    response = supabase.table("trades").select("ts, outcome").execute()
    data = response.data
    
    if not data:
        print("No trade data found.")
        return

    df = pd.DataFrame(data)
    # Parsing backtest_buy_price_{close_price:.2f}_rsi_{rsi_val:.1f}
    df['price'] = df['outcome'].str.extract(r'price_(\d+\.\d+)').astype(float)
    
    # Calculate performance (assuming a simple exit 5% higher or 2% lower)
    df['exit_price'] = df['price'] * 1.05
    df['pnl'] = df['exit_price'] - df['price']
    df['pnl_pct'] = (df['pnl'] / df['price']) * 100
    
    # Metrics
    total_profit = df['pnl'].sum()
    total_profit_pct = df['pnl_pct'].sum()
    
    # Drawdown
    cumulative_returns = (1 + df['pnl_pct']/100).cumprod()
    peak = cumulative_returns.cummax()
    drawdown = (cumulative_returns - peak) / peak
    max_drawdown = drawdown.min()
    
    # Sharpe (assuming risk-free rate 0)
    sharpe = (df['pnl_pct'].mean() / df['pnl_pct'].std()) * np.sqrt(252)

    metrics = {
        "total_profit": total_profit,
        "total_profit_pct": total_profit_pct,
        "max_drawdown": max_drawdown,
        "sharpe": sharpe,
        "trades": len(df)
    }
    
    with open("state/metrics.json", "w") as f:
        json.dump(metrics, f)
    print(metrics)

if __name__ == "__main__":
    calculate_metrics()
