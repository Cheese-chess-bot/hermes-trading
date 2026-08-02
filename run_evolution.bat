@echo off
cd /d "C:\Users\Wribhi\hermes-trading"
:: Ensure SUPABASE_URL and SUPABASE_KEY are set in Windows System Environment Variables
echo Launching Evolutionary Training...
"C:\Users\Wribhi\hermes-trading\.venv\Scripts\python.exe" -m hermes_trading.execution2
echo.
echo Training complete. Press any key to close.
pause
