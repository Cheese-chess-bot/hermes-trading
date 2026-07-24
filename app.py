import os
import gradio as gr
import threading
import asyncio
from hermes_trading.loop import run_loop
import yaml

# Load goal for the loop
with open("state/goal.yaml", "r") as f:
    goal = yaml.safe_load(f)

# Background worker
def start_worker():
    asyncio.run(run_loop(goal["asset"], goal))

threading.Thread(target=start_worker, daemon=True).start()

# Gradio UI
def get_status():
    return "Worker running..."

demo = gr.Interface(fn=get_status, inputs=[], outputs="text")

# Cloud Run expects the app to listen on the port provided by the $PORT env var
port = int(os.environ.get("PORT", 7860))
demo.launch(server_name="0.0.0.0", server_port=port)
