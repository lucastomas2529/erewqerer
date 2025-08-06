@echo off
echo ========================================
echo    PYTHON INSTALLATION HELPER
echo ========================================
echo.

echo [1/3] Checking if Python is installed...
python --version >nul 2>&1
if not errorlevel 1 (
    echo ✅ Python is already installed!
    echo Version:
    python --version
    echo.
    echo You can now run START_BOT.bat
    pause
    exit /b 0
)

echo ❌ Python is not installed or not in PATH
echo.

echo [2/3] Opening Python download page...
echo Please download and install Python from:
echo https://www.python.org/downloads/
echo.
echo IMPORTANT: Check "Add Python to PATH" during installation
echo.

set /p choice="Open Python download page in browser? (y/n): "
if /i "%choice%"=="y" (
    start https://www.python.org/downloads/
)

echo.
echo [3/3] Installation Instructions:
echo.
echo 1. Download Python 3.8 or higher
echo 2. Run the installer
echo 3. CHECK "Add Python to PATH" ✅
echo 4. Click "Install Now"
echo 5. Restart your computer
echo 6. Run START_BOT.bat
echo.
echo After installation, run this script again to verify.
echo.
pause 