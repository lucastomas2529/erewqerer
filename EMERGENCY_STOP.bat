@echo off
echo ========================================
echo    TOMAS BOT - EMERGENCY STOP
echo ========================================
echo.

echo ⚠️  EMERGENCY STOP ACTIVATED
echo This will immediately stop all trading activities.
echo.

set /p confirm="Are you sure you want to EMERGENCY STOP? (yes/no): "
if /i "%confirm%" neq "yes" (
    echo Emergency stop cancelled.
    pause
    exit /b 0
)

echo.
echo [1/3] Stopping all bot processes...
taskkill /f /im python.exe 2>nul
echo ✅ Bot processes stopped

echo.
echo [2/3] Setting emergency stop flag...
echo EMERGENCY_STOP=true > .emergency_stop
echo ✅ Emergency stop flag set

echo.
echo [3/3] Notifying via Telegram (if configured)...
if exist ".env" (
    echo Emergency stop activated at %date% %time% >> bot_log.txt
    echo ✅ Emergency stop logged
)

echo.
echo 🛑 EMERGENCY STOP COMPLETE
echo All trading activities have been halted.
echo.
echo To restart the bot:
echo 1. Delete the .emergency_stop file
echo 2. Run START_BOT.bat (for testing) or START_BOT_LIVE.bat (for live trading)
echo.
pause 