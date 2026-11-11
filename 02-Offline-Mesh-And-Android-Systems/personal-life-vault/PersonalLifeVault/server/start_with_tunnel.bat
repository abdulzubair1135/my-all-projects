@echo off
setlocal EnableDelayedExpansion
title Personal Life Vault - Cloudflare Tunnel Launcher

echo.
echo  +===================================================+
echo  ^|   PERSONAL LIFE VAULT - CLOUDFLARE TUNNEL       ^|
echo  +===================================================+
echo.

:: 1. Ensure server is running or start it in separate window
echo  [1/2] Launching Vault Server on http://127.0.0.1:8088...
start "Vault Server" /min cmd /c "node --experimental-sqlite server.js"

:: 2. Check cloudflared.exe
if not exist "C:\Vault\cloudflared.exe" (
    echo  [ERROR] cloudflared.exe not found at C:\Vault\cloudflared.exe!
    echo  Downloading cloudflared.exe...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'C:\Vault\cloudflared.exe'"
)

echo  [2/2] Starting Cloudflare Tunnel...
echo.
echo  ---------------------------------------------------
echo  Your Vault HTTPS Tunnel URL will appear below:
echo  ---------------------------------------------------
echo.

"C:\Vault\cloudflared.exe" tunnel --url http://127.0.0.1:8088

endlocal
