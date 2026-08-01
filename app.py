import os
import gradio as gr
import pandas as pd
import plotly.express as px
import yaml
import datetime
import pytz
from hermes_trading.db import supabase
from hermes_trading.clock import is_market_open

def get_market_metrics():
    # Fetch live trades
    live_trades = supabase.table("trades").select("*").execute().data
    # Fetch past evolution trades
    past_trades = supabase.table("past_evol_trade").select("*").execute().data
    
    # Strategy
    strat_resp = supabase.table("settings").select("value").eq("key", "strategy").single().execute()
    strat = yaml.safe_load(strat_resp.data["value"]) if strat_resp.data else {}

    # Metrics Calc (Placeholder logic for Sharpe/Drawdown if data is sparse)
    trade_count = len(live_trades)
    
    # Basic Time
    nyse_tz = pytz.timezone('America/New_York')
    nyse_time = datetime.datetime.now(nyse_tz).strftime('%Y-%m-%d %H:%M:%S %Z')
    market_status = "Open" if is_market_open() else "Closed"
    
    return {
        "trades": trade_count,
        "mode": "Real" if is_market_open() else "Past",
        "market": "NVDA",
        "status": market_status,
        "nyse_time": nyse_time,
        "strat": strat.get("version", "01"),
        "profit": 0.0,
        "drawdown": 0.0,
        "win_rate": 0.0,
        "sharpe": 0.0
    }

def update_dashboard():
    m = get_market_metrics()
    
    # Generate Plotly Chart
    df = pd.DataFrame(supabase.table("trades").select("ts, outcome").execute().data)
    fig = px.line(df, x='ts', y='outcome', title="NVDA Price Simulation")
    
    return (
        m["trades"], m["mode"], m["market"], m["status"], 
        m["nyse_time"], m["strat"], m["profit"], 
        m["drawdown"], m["win_rate"], m["sharpe"], fig
    )

with gr.Blocks() as demo:
    gr.Markdown("# Hermes Trading Dashboard")
    
    with gr.Row():
        trades_display = gr.Number(label="Trades executed")
        mode_display = gr.Textbox(label="Mode")
        market_display = gr.Textbox(label="Market")
        status_display = gr.Textbox(label="Market status")
        time_display = gr.Textbox(label="Time (NYSE)")
        strat_display = gr.Textbox(label="Model strats version")
        
    with gr.Row():
        profit_display = gr.Number(label="Max Profit")
        dd_display = gr.Number(label="Max Drawdown")
        win_display = gr.Number(label="Win%")
        loss_display = gr.Number(label="Loss%")
        sharpe_display = gr.Number(label="Sharpe")
        
    chart_display = gr.Plot(label="NVDA IRL CHART")
    
    demo.load(update_dashboard, outputs=[
        trades_display, mode_display, market_display, status_display, 
        time_display, strat_display, profit_display, dd_display, 
        win_display, sharpe_display, chart_display
    ])

port = int(os.environ.get("PORT", 7860))
demo.launch(server_name="0.0.0.0", server_port=port)
