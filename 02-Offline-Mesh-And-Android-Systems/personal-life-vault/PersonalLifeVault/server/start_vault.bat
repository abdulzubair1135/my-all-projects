@echo off
setlocal EnableDelayedExpansion
title Personal Life Vault - Server Launcher

echo.
echo  +===========================================+
echo  ^|     PERSONAL LIFE VAULT - SERVER          ^|
echo  +===========================================+
echo.

:: Kill any existing server on port 8088
for /f "tokens=5" %%i in ('netstat -ano ^| findstr ":8088 "') do (
    taskkill /F /PID %%i >nul 2>&1
)

:: Find the LAN IP (USB tethering or WiFi, not loopback or link-local)
set "LAPTOP_IP=127.0.0.1"
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4" ^| findstr /v "169.254" ^| findstr /v "127.0.0.1" ^| findstr /v "192.168.112"') do (
    set "RAW=%%a"
    set "LAPTOP_IP=!RAW: =!"
    goto :gotip
)
:gotip

echo  Server will listen on: http://0.0.0.0:8088
echo  Laptop LAN IP:         http://%LAPTOP_IP%:8088
echo.
echo  In the Android app, set Server URL to:
echo    http://%LAPTOP_IP%:8088
echo.

:: Setup ADB reverse if phone is connected via USB
set ADB=%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe
if exist "%ADB%" (
    "%ADB%" reverse tcp:8088 tcp:8088 >nul 2>&1
    if !errorlevel! equ 0 (
        echo  [ADB] Phone connected via USB - tunnel active on http://127.0.0.1:8088
    ) else (
        echo  [ADB] Phone not connected via USB. Use LAN IP above.
    )
) else (
    echo  [ADB] ADB not found. Only LAN/Tailscale connectivity available.
)
echo.
echo  Starting server...
echo  ----------------------------------------

:: Start the Node.js server
node --experimental-sqlite server.js

endlocal
