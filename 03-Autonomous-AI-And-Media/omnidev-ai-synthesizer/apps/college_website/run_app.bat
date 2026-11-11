@echo off
chcp 65001 >nul
title College Website
cd /d "%~dp0"
echo ================================================================
echo    College Website - 1-Click Auto Launcher
echo ================================================================
echo.

if exist "requirements.txt" (
    echo [OmniDev] Verifying Python dependencies...
    pip install -r requirements.txt -q
)

if exist "package.json" (
    if not exist "node_modules" (
        echo [OmniDev] Installing Node packages...
        call npm install
    )
    echo [OmniDev] Launching application...
    npm start
) else (
    echo [OmniDev] Launching server on http://127.0.0.1:8000 ...
    python -m uvicorn main:app --host 127.0.0.1 --port 8000
)
pause
