@echo off
title ProjectFlow Intelligence - Stop All Services
color 0C

echo ======================================================================
echo                STOPPING ALL PROJECTFLOW SERVICES
echo ======================================================================
echo.

echo [INFO] Stopping port 8082 (ProjectFlow Full-Stack Server)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8082 ^| findstr LISTENING') do (
    echo   Killing PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

echo [INFO] Stopping port 8080...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080 ^| findstr LISTENING') do (
    echo   Killing PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

echo [INFO] Stopping port 5173 (Vite dev server if running)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do (
    echo   Killing PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo [OK] All ProjectFlow background services stopped cleanly!
echo.
pause
