@echo off
cd /d "C:\Users\Wribhi\hermes-trading"
:: API keys are in Windows Environment Variables (sysdm.cpl)
echo Launching Hermès...
"C:\Users\Wribhi\.local\bin\uv.exe" run python -m hermes_trading.run
pause
