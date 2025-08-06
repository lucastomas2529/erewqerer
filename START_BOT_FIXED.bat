@echo off
echo ========================================
echo    TOMAS BOT - FIXED STARTUP
echo ========================================

echo 🐍 Python found

echo [2/4] Setting up virtual environment...
call ".venv\Scripts\activate.bat"
echo ✅ Virtual environment ready

echo [3/4] Installing dependencies...
pip install -r requirements.txt >nul 2>&1
echo ✅ Dependencies installed

echo [4/4] Starting Tomas Bot...
echo 🚀 BOT IS STARTING...
echo 📡 Monitoring Telegram groups...
echo 🛡️ Running in MOCK MODE (safe for testing)

echo.
echo Press Ctrl+C to stop the bot
echo.

REM Set PYTHONPATH and start the bot
set PYTHONPATH=.
python runner/main.py

pause 