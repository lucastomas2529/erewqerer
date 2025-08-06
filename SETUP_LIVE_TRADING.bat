@echo off
echo ========================================
echo    TOMAS BOT - LIVE TRADING SETUP
echo ========================================
echo.
echo This will help you configure the bot for live trading.
echo WARNING: Only use with real money after thorough testing!
echo.

set /p choice="Do you want to configure live trading? (y/n): "
if /i "%choice%" neq "y" (
    echo Setup cancelled.
    pause
    exit /b 0
)

echo.
echo ========================================
echo    CONFIGURING API CREDENTIALS
echo ========================================
echo.

echo [1/3] Bitget API Configuration
echo Get your API credentials from: https://www.bitget.com/api-doc
echo.
set /p BITGET_API_KEY="Enter your Bitget API Key: "
set /p BITGET_API_SECRET="Enter your Bitget API Secret: "
set /p BITGET_API_PASSPHRASE="Enter your Bitget API Passphrase: "

echo.
echo [2/3] Telegram Bot Configuration
echo Get your bot token from: https://t.me/BotFather
echo.
set /p TELEGRAM_BOT_TOKEN="Enter your Telegram Bot Token: "
set /p TELEGRAM_API_ID="Enter your Telegram API ID: "
set /p TELEGRAM_API_HASH="Enter your Telegram API Hash: "

echo.
echo [3/3] Creating .env file...
echo # Tomas Bot Live Trading Configuration > .env
echo BITGET_API_KEY=%BITGET_API_KEY% >> .env
echo BITGET_API_SECRET=%BITGET_API_SECRET% >> .env
echo BITGET_API_PASSPHRASE=%BITGET_API_PASSPHRASE% >> .env
echo BITGET_SANDBOX=false >> .env
echo TELEGRAM_BOT_TOKEN=%TELEGRAM_BOT_TOKEN% >> .env
echo TELEGRAM_API_ID=%TELEGRAM_API_ID% >> .env
echo TELEGRAM_API_HASH=%TELEGRAM_API_HASH% >> .env
echo ENABLE_LIVE_TRADING=true >> .env
echo DEFAULT_LEVERAGE=10 >> .env
echo DEFAULT_RISK_PERCENT=2.0 >> .env
echo DEFAULT_IM_AMOUNT=20.0 >> .env
echo MAX_POSITION_SIZE=1000 >> .env
echo MAX_DAILY_LOSS=500 >> .env
echo EMERGENCY_STOP=false >> .env
echo LOG_LEVEL=INFO >> .env
echo API_DEBUG_LOGGING=false >> .env
echo ENABLE_TELEGRAM_NOTIFICATIONS=true >> .env

echo ✅ .env file created successfully!
echo.
echo IMPORTANT NOTES:
echo 1. The bot will now run in LIVE TRADING mode
echo 2. Start with small amounts to test
echo 3. Monitor the bot closely during initial trades
echo 4. Use the emergency stop if needed
echo.
echo To start the bot with live trading, run: START_BOT_LIVE.bat
echo.
pause 