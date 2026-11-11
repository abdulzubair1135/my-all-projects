@echo off
title FollowTrack - Instagram Analytics Platform
echo ===================================================
echo             FOLLOWTRACK APPLICATION
echo    "Know Who Follows You. Track Every Change."
echo ===================================================
echo.

echo [1/3] Checking Node.js environment...
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed or not in PATH!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

if not exist node_modules (
    echo [2/3] Installing dependencies...
    call npm install --legacy-peer-deps
) else (
    echo [2/3] Dependencies verified.
)

echo.
echo [3/3] Starting FollowTrack on http://localhost:5173/ ...
echo Opening your browser automatically...
start http://localhost:5173/

echo.
echo ===================================================
echo FollowTrack is running!
echo URL: http://localhost:5173/
echo (Keep this terminal window open while using the app)
echo ===================================================
echo.

call npm run dev
