@echo off
setlocal enabledelayedexpansion
title ProjectFlow Intelligence - Server & Web Launcher
color 0A

:: Safety path detection
if exist "C:\Program Files\nodejs\node.exe" (
    set "PATH=%PATH%;C:\Program Files\nodejs;%APPDATA%\npm"
)

echo ======================================================================
echo             PROJECTFLOW INTELLIGENCE - FULL-STACK LAUNCHER
echo ======================================================================
echo.

:: Check Node.js
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [!] Node.js not detected in PATH.
    echo [INFO] Running automatic setup wizard...
    call "1_SETUP_NEW_LAPTOP.bat"
)

:: Check if server is already running on port 8082
netstat -aon | findstr :8082 | findstr LISTENING >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [INFO] ProjectFlow Server is already running on port 8082!
) else (
    echo [INFO] Starting ProjectFlow Node.js Cloud & Local Server on port 8082...
    start "ProjectFlow Backend & Web Server [Port 8082]" cmd /k "node server.js"
    echo [INFO] Waiting 3 seconds for server to initialize...
    timeout /t 3 >nul
)

echo.
echo [INFO] Opening Web Dashboard in your default browser...
start http://localhost:8082

echo.
echo ======================================================================
echo                     WEBSITE IS NOW RUNNING!
echo ======================================================================
echo.
echo   * Local URL:       http://localhost:8082
echo   * Production Live: https://projectflow-intelligence.onrender.com
echo.
echo   [DEFAULT LOGIN ACCOUNTS]:
echo   1. Administrator:   admin@projectflow.io      / ProjectFlow@2026
echo   2. Project Manager:  manager@projectflow.io    / ProjectFlow@2026
echo   3. Engineer:         abdulzubair221@gmail.com  / kalyani
echo   4. UI/UX Designer:   puneet@projectflow.io     / ProjectFlow@2026
echo.
echo Server window ko band mat karna jab tak kaam karna ho.
echo Server band karne ke liye "STOP_ALL_SERVICES.bat" run karein.
echo.
pause
