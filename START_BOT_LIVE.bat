@echo off
echo ========================================
echo    TOMAS BOT - LIVE TRADING MODE
echo ========================================
echo.

echo ⚠️  WARNING: LIVE TRADING MODE
echo This bot will execute real trades with real money!
echo Make sure you have:
echo - Tested the bot thoroughly in mock mode
echo - Configured your API credentials correctly
echo - Set appropriate risk limits
echo.

set /p confirm="Are you sure you want to start LIVE TRADING? (yes/no): "
if /i "%confirm%" neq "yes" (
    echo Live trading cancelled.
    echo Run START_BOT.bat for safe testing mode.
    pause
    exit /b 0
)

echo.
echo [1/4] Checking configuration...
if not exist ".env" (
    echo ERROR: No .env file found!
    echo Please run SETUP_LIVE_TRADING.bat first.
    pause
    exit /b 1
)
echo ✅ Configuration found

echo.
echo [2/4] Setting up environment...
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)
echo ✅ Environment ready

echo.
echo [3/4] Installing dependencies...
call .venv\Scripts\activate.bat
pip install --upgrade pip
pip install telethon aiohttp cryptg ccxt python-dotenv websockets pandas numpy
echo ✅ Dependencies installed

echo.
echo [4/4] Starting Tomas Bot in LIVE TRADING MODE...
echo.
echo 🚀 LIVE TRADING BOT IS STARTING...
echo 💰 REAL MONEY TRADING ENABLED
echo 📡 Monitoring Telegram groups...
echo ⚠️  Monitor closely and use emergency stop if needed
echo.
echo Press Ctrl+C to stop the bot
echo.

set PYTHONPATH=.
python runner/main.py

echo.
echo Bot stopped. Press any key to exit...
pause >nul 