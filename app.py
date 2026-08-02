import os
import gradio as gr
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yaml
import datetime
import pytz
import yfinance as yf
import subprocess
from hermes_trading.db import supabase
from hermes_trading.clock import is_market_open

def get_market_metrics():
    # Fetch live trades
    live_trades = supabase.table("trades").select("*").execute().data
    
    # Calculate metrics (Simple placeholders for now)
    trade_count = len(live_trades)
    profit, drawdown, win_rate, sharpe = 0.0, 0.0, 0.0, 0.0
        
    nyse_tz = pytz.timezone('America/New_York')
    nyse_time = datetime.datetime.now(nyse_tz).strftime('%Y-%m-%d %H:%M:%S %Z')
    market_status = "Open" if is_market_open() else "Closed"
    
    return {
        "trades": trade_count,
        "mode": "Real" if is_market_open() else "Past",
        "market": "NVDA",
        "status": market_status,
        "nyse_time": nyse_time,
        "strat": "01",
        "profit": profit,
        "drawdown": drawdown,
        "win_rate": win_rate,
        "sharpe": sharpe
    }

def force_evolve():
    subprocess.Popen(["python", "-m", "hermes_trading.execution2"])
    return "Evolution triggered!"

def update_dashboard():
    m = get_market_metrics()
    
    # Fetch chart data
    ticker = yf.Ticker("NVDA")
    hist = ticker.history(period="1mo", interval="1d")
    
    # Create Dual-Axis Plotly Chart
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add Price Line
    fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name="Price"), secondary_y=False)
    # Add Volume Bar
    fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name="Volume", opacity=0.3), secondary_y=True)
    
    fig.update_layout(title="NVDA Price & Volume", template="plotly_dark")
    
    return (
        gr.update(value=m["trades"]), m["mode"], m["market"], m["status"], 
        m["nyse_time"], m["strat"], gr.update(value=m["profit"]), 
        gr.update(value=m["drawdown"]), gr.update(value=m["win_rate"]), 
        gr.update(value=m["sharpe"]), fig
    )

with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue")) as demo:
    gr.Markdown("# Hermes Trading Dashboard")
    
    with gr.Row():
        force_btn = gr.Button("Force Evolve Now")
        force_status = gr.Textbox(label="Status", interactive=False)
    
    force_btn.click(force_evolve, outputs=[force_status])
    
    with gr.Row():
        trades_display = gr.Number(label="Trades executed", interactive=False)
        mode_display = gr.Textbox(label="Mode", interactive=False)
        market_display = gr.Textbox(label="Market", interactive=False)
        status_display = gr.Textbox(label="Market status", interactive=False)
        time_display = gr.Textbox(label="Time (NYSE)", interactive=False)
        strat_display = gr.Textbox(label="Model strats version", interactive=False)
        
    with gr.Row():
        profit_display = gr.Number(label="Max Profit (Live)", interactive=False)
        profit_paper_display = gr.Number(label="Max Profit (Paper)", interactive=False)
        dd_display = gr.Number(label="Max Drawdown", interactive=False)
        win_display = gr.Number(label="Win%", interactive=False)
        loss_display = gr.Number(label="Loss%", interactive=False)
        sharpe_display = gr.Number(label="Sharpe", interactive=False)
        
    chart_display = gr.Plot(label="NVDA IRL CHART")
    
    demo.load(update_dashboard, outputs=[
        trades_display, mode_display, market_display, status_display, 
        time_display, strat_display, profit_display, dd_display, 
        win_display, sharpe_display, chart_display
    ])

port = int(os.environ.get("PORT", 7860))
demo.launch(server_name="0.0.0.0", server_port=port)
