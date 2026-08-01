---
title: Hermes Trading
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Hermes Trading Agent

A self-improving, autonomous trading agent.

## Changes Log
- **Added:** Pattern recognition engine (`patterns.py`) with 20+ technical patterns (no emojis).
- **Added:** Evolutionary backtesting engine (`reflect2.py`) for sliding-window optimization.
- **Added:** `analyze.py` for performance metrics calculation.
- **Added:** `clock.py` for NYSE market hours.
- **Added:** `execution.py` (Live sentinel) and `execution2.py` (Evolutionary backtester).
- **Updated:** Loop now uses pure Python RSI and executes live BUY signals on Alpaca (Paper mode).
- **Fixed:** Dependency issues (replaced `pandas` with pure Python logic).
- **Fixed:** Corrected `Dockerfile` and Python version (3.11).
