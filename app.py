import os
import gradio as gr
import pandas as pd
import plotly.graph_objects as go
import yaml
import datetime
import pytz
import threading
import asyncio
import time
import subprocess
from hermes_trading.db import supabase
from hermes_trading.clock import is_market_open
from hermes_trading.loop import run_loop
import yfinance as yf

# --- 1. AUTONOMOUS LIVE TRADER ---
def start_live_trader():
    with open("state/goal.yaml", "r") as f:
        goal = yaml.safe_load(f)
    asyncio.run(run_loop(goal["asset"], goal))

# --- 2. AUTONOMOUS EVOLUTION SCHEDULER ---
def start_evolution_scheduler():
    print("Evolution Scheduler Active...")
    last_evol_date = None
    while True:
        nyse_tz = pytz.timezone('America/New_York')
        now = datetime.datetime.now(nyse_tz)
        
        # Trigger evolution once per day after market close
        if not is_market_open() and now.date() != last_evol_date:
            print("Market Closed: Running automated daily evolution...")
            try:
                subprocess.run(["python", "-m", "hermes_trading.execution2"], check=True)
                last_evol_date = now.date()
                print("Daily evolution complete.")
            except Exception as e:
                print(f"Evolution failed: {e}")
        
        time.sleep(3600) # Check every hour

# Launch background processes
threading.Thread(target=start_live_trader, daemon=True).start()
threading.Thread(target=start_evolution_scheduler, daemon=True).start()

# --- 3. DASHBOARD UI ---
def get_market_metrics():
    # Fetch live trades
    live_trades = supabase.table("trades").select("*").execute().data
    trade_count = len(live_trades)
    
    nyse_tz = pytz.timezone('America/New_York')
    nyse_time = datetime.datetime.now(nyse_tz).strftime('%Y-%m-%d %H:%M:%S %Z')
    market_status = "Open" if is_market_open() else "Closed"
    
    return {
        "trades": trade_count,
        "mode": "Real" if is_market_open() else "Past",
        "market": "NVDA",
        "status": market_status,
        "nyse_time": nyse_time,
        "strat": "01"
    }

def update_dashboard():
    m = get_market_metrics()
    ticker = yf.Ticker("NVDA")
    hist = ticker.history(period="1mo", interval="1d")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name="Price"))
    fig.update_layout(title="NVDA Price", template="plotly_dark")
    
    return (m["trades"], m["mode"], m["market"], m["status"], m["nyse_time"], m["strat"], fig)

with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue")) as demo:
    gr.Markdown("# Hermes Trading Dashboard - Fully Autonomous")
    with gr.Row():
        trades_display = gr.Number(label="Trades executed")
        mode_display = gr.Textbox(label="Mode")
        market_display = gr.Textbox(label="Market")
        status_display = gr.Textbox(label="Market status")
        time_display = gr.Textbox(label="Time (NYSE)")
        strat_display = gr.Textbox(label="Model strats version")
    chart_display = gr.Plot(label="NVDA IRL CHART")
    
    demo.load(update_dashboard, outputs=[
        trades_display, mode_display, market_display, status_display, 
        time_display, strat_display, chart_display
    ])

demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
