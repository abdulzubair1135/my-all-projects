@echo off
chcp 65001 >nul
title Autonomous Web-Agent IDE
cls

echo ====================================================================
echo             AUTONOMOUS WEB-AGENT IDE - ONE CLICK LAUNCH
echo ====================================================================
echo.

cd /d "%~dp0"

:: Start the master Node launcher
node launch.js

pause
