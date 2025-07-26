@echo off
REM Check if Python launcher is available
py --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [Error] Python not found. Please install Python and add it to the PATH environment variable.
    pause
    exit /b 1
)

REM Install dependencies if requirements.txt exists
IF EXIST requirements.txt (
    echo [Info] Installing dependencies from requirements.txt...
    py -m pip install --quiet -r requirements.txt
)

REM Run the main script
echo [Run] Starting the project...
py openerGUI.py

pause
