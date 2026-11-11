@echo off
title Couple Canvas Cloudflare Signaling Server Launcher
cd /d "%~dp0signaling-server"
echo ================================================================
echo     💕 Couple Canvas WebRTC Signaling Server + Cloudflare WSS
echo ================================================================
echo.

IF NOT EXIST node_modules (
    echo Installing dependencies...
    call npm install
    echo.
)

echo [1/2] Starting Node.js signaling server on port 8080...
start "Couple Canvas Node Server" /min cmd /c "node server.js"

timeout /t 2 /nobreak >nul

echo [2/2] Starting Cloudflare HTTPS / WSS Tunnel...
echo.
echo ================================================================
echo   Public WSS Cloudflare Tunnel active at:
echo   wss://psychological-streams-centres-fell.trycloudflare.com
echo ================================================================
echo.

cloudflared tunnel --url http://localhost:8080

pause
