@echo off
title CycleCare — Admin Control Panel
color 0D

echo ========================================================
echo        CycleCare Master Admin Control Panel
echo ========================================================
echo.
echo [1/3] Checking environment...
node -v >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js is not found in your PATH. Please install Node.js!
    pause
    exit /b 1
)

echo [2/3] Starting CycleCare Backend Engine on port 5000...
cd /d "%~dp0backend"

:: Start backend in a separate background window if not already started
start "CycleCare Backend Service" cmd /c "npm start"

echo [3/3] Opening Admin Control Panel in browser...
timeout /t 2 /nobreak >nul
start http://localhost:5000/admin-panel/admin.html

echo.
echo ========================================================
echo  ✓ CycleCare Control Panel is now running!
echo  URL: http://localhost:5000/admin-panel/admin.html
echo  To shut down, close the Backend Service console window.
echo ========================================================
echo.
pause
