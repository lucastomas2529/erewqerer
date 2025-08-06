@echo off
echo ========================================
echo    TOMAS BOT - AUTOMATIC STARTUP
echo ========================================
echo.

echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)
echo ✅ Python found

echo.
echo [2/4] Setting up virtual environment...
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)
echo ✅ Virtual environment ready

echo.
echo [3/4] Installing dependencies...
call .venv\Scripts\activate.bat
pip install --upgrade pip
pip install telethon aiohttp cryptg ccxt python-dotenv websockets pandas numpy
echo ✅ Dependencies installed

echo.
echo [4/4] Starting Tomas Bot...
echo.
echo 🚀 BOT IS STARTING...
echo 📡 Monitoring Telegram groups...
echo 💰 Running in MOCK MODE (safe for testing)
echo.
echo Press Ctrl+C to stop the bot
echo.

set PYTHONPATH=.
python runner/main.py

echo.
echo Bot stopped. Press any key to exit...
pause >nul 