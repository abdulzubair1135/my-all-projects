@echo off
title Sahay Real-Time Disaster Response Network
color 0C

echo ================================================================
echo           SAHAY DISASTER MANAGEMENT COMMAND PLATFORM
echo            "When the Network Fails, Sahay Doesn't."
echo ================================================================
echo.

echo [1/5] Configuring USB Debugging Zero-Latency Network Bridge...
if exist "C:\Users\abdul\AppData\Local\Android\Sdk\platform-tools\adb.exe" (
    "C:\Users\abdul\AppData\Local\Android\Sdk\platform-tools\adb.exe" reverse tcp:5000 tcp:5000 >nul 2>&1
    "C:\Users\abdul\AppData\Local\Android\Sdk\platform-tools\adb.exe" reverse tcp:3000 tcp:3000 >nul 2>&1
    echo       [OK] ADB reverse proxy active (Phone connected to 127.0.0.1:5000)
) else (
    echo       [NOTE] ADB not found in standard path, proceeding with direct network...
)

echo [2/5] Starting Resilient Backend Server (Port 5000)...
start "Sahay Backend Engine" cmd /k "cd /d c:\Users\abdul\OneDrive\ドキュメント\disaster\backend && npm run dev"

echo [3/5] Starting Command Center & Citizen Web UI (Port 3000)...
start "Sahay Web Frontend" cmd /k "cd /d c:\Users\abdul\OneDrive\ドキュメント\disaster\web && npm run dev"

echo [4/5] Starting Cloudflare Public HTTPS Tunnels...
if exist "C:\Program Files (x86)\cloudflared\cloudflared.exe" (
    start "Cloudflare Web Tunnel" cmd /k ""C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://localhost:3000"
    start "Cloudflare Backend Tunnel" cmd /k ""C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://localhost:5000"
    echo       [OK] Cloudflare tunnels launched
)

echo [5/5] Initializing platform services...
timeout /t 4 /nobreak >nul

echo Opening Sahay Government Command Center in default browser...
start http://localhost:3000

echo.
echo ================================================================
echo   All Sahay Services are LIVE!
echo   - Web Command Center: http://localhost:3000
echo   - Backend Server:     http://localhost:5000
echo   - Android Phone Node: Reverse bridged to 127.0.0.1:5000
echo ================================================================
echo Keep this window open or press any key to minimize.
pause >nul
