@echo off
TITLE Personal Life Vault Server & Cloudflare Tunnel
COLOR 0A
CLS

echo =========================================================
echo       🔒 PERSONAL LIFE VAULT SERVER LAUNCHER
echo =========================================================
echo.
echo [1/2] Starting Personal Life Vault Node Server (Port 8088)...
echo [2/2] Auto-connecting Cloudflare Tunnel...
echo.
echo Local Web Dashboard: http://localhost:8088
echo.
echo Keep this window open to run the server.
echo Press Ctrl + C to stop the server anytime.
echo =========================================================
echo.

cd /d "%~dp0server"
node --experimental-sqlite server.js

pause
