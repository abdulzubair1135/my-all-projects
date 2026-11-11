@echo off
title Personal AI Agent - Master Brain
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================================
echo   Starting Personal AI Agent (Qwen3.5 4B + Local Brain)
echo ========================================================
echo.

python main.py

if errorlevel 1 (
    echo.
    echo Agent exited with an error.
    pause
)
