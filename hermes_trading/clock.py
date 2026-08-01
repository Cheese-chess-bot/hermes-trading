import pandas_market_calendars as mcal
import pytz
import datetime

def is_market_open():
    nyse = mcal.get_calendar('NYSE')
    nyse_tz = pytz.timezone('America/New_York')
    now = datetime.datetime.now(nyse_tz)
    
    # Get schedule for today and tomorrow to handle end-of-day cases
    today_str = now.strftime('%Y-%m-%d')
    schedule = nyse.schedule(start_date=today_str, end_date=today_str)
    
    if schedule.empty:
        return False
        
    market_open = schedule.iloc[0]['market_open']
    market_close = schedule.iloc[0]['market_close']
    
    # Ensure times are timezone aware
    if market_open.tzinfo is None: market_open = nyse_tz.localize(market_open)
    if market_close.tzinfo is None: market_close = nyse_tz.localize(market_close)
    
    return market_open <= now <= market_close
