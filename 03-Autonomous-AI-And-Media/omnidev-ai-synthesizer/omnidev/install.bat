@echo off
title OmniDev AI - Installer
cd /d "%~dp0"

echo ================================================================
echo           OmniDev AI - Environment Setup & Installation
echo ================================================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from python.org and check "Add to PATH".
    pause
    exit /b 1
)

echo [1/4] Checking Virtual Environment...
if not exist ".venv" (
    echo Creating virtual environment (.venv)...
    python -m venv .venv
) else (
    echo Virtual environment already exists.
)

echo.
echo [2/4] Activating Virtual Environment...
call .venv\Scripts\activate.bat

echo.
echo [3/4] Installing Python Dependencies from requirements.txt...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo [4/4] Installing Playwright Chromium browser...
playwright install chromium

echo.
echo ================================================================
echo           OmniDev AI Setup Completed Successfully!
echo ================================================================
echo You can now:
echo 1. Run 'setup_login.bat' to log into DeepSeek in Chrome.
echo 2. Run 'run_ai.bat' to launch the OmniDev AI terminal.
echo.
pause
