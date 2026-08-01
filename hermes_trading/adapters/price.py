import yfinance as yf
import asyncio

async def fetch(asset):
    # Convert ccxt style ticker like NVDA/USDT to yfinance symbol (NVDA)
    symbol = asset.split('/')[0]
    
    def _get_bars():
        ticker = yf.Ticker(symbol)
        # Fetch OHLCV data
        hist = ticker.history(period="1d", interval="1m")
        if hist.empty:
            return []
        
        # Convert to list of dicts for our pure-python pattern engine
        bars = []
        for index, row in hist.iterrows():
            bars.append({
                'open': float(row['Open']),
                'close': float(row['Close']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'volume': float(row['Volume'])
            })
        return bars

    loop = asyncio.get_running_loop()
    bars = await loop.run_in_executor(None, _get_bars)
    
    return {"schema_version": "1.0", "bars": bars, "current_price": bars[-1]['close'] if bars else 100.0}
