@echo off
TITLE Storage Cleanup and Cloudflare Tunnel Launcher
color 0A

echo ================================================================
echo    STORAGE CLEANUP ANALYZER - CLOUDFLARE TUNNEL LAUNCHER
echo ================================================================
echo.

cd /d "%~dp0"

REM Step 1: Check Python / Node.js and start server
echo [1/2] Checking local server environment...
where python >nul 2>nul
if %errorlevel%==0 (
    echo [+] Python detected. Checking Flask dependency...
    python -c "import flask" >nul 2>nul
    if %errorlevel% neq 0 (
        echo [!] Installing Flask...
        python -m pip install flask
    )
    echo [+] Starting Python Localhost Server on port 5000...
    start "Localhost Server" python server.py
    timeout /t 2 /nobreak >nul
    start http://localhost:5000
    goto START_TUNNEL
)

where node >nul 2>nul
if %errorlevel%==0 (
    echo [+] Node.js detected. Starting Node.js Localhost Server on port 5000...
    if not exist node_modules (
        echo [!] Installing express...
        npm install express
    )
    start "Localhost Server" node server.js
    timeout /t 2 /nobreak >nul
    start http://localhost:5000
    goto START_TUNNEL
)

echo [X] Error: Neither Python nor Node.js was found on your system!
echo Please install Python (https://www.python.org/) or Node.js (https://nodejs.org/).
pause
exit /b

:START_TUNNEL
echo.
echo [2/2] Launching Cloudflare Tunnel...
where cloudflared >nul 2>nul
if %errorlevel%==0 (
    echo [+] Cloudflare Tunnel binary detected. Launching tunnel...
    start "Cloudflare Tunnel" cloudflared tunnel --url http://localhost:5000
) else if exist "C:\Program Files (x86)\cloudflared\cloudflared.exe" (
    echo [+] Cloudflare Tunnel found in Program Files. Launching tunnel...
    start "Cloudflare Tunnel" "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://localhost:5000
) else (
    echo [!] cloudflared not found. Please ensure Cloudflare Tunnel is installed.
)

:FINISH
echo.
echo ================================================================
echo    LAUNCH COMPLETE!
echo ================================================================
echo.
echo  1. Local Web Dashboard:        http://localhost:5000
echo  2. Cloudflare Tunnel Window:   Copy the generated https://xxxx.trycloudflare.com URL
echo                                 from the Cloudflare window into the app!
echo.
echo Press any key to exit launcher (Server and Tunnel remain running).
pause >nul
