@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
title OmniDev AI - Autonomous Development Agent
cd /d "%~dp0"

echo ================================================================
echo           OmniDev AI - Starting Agent Engine
echo ================================================================
echo.

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo [WARNING] .venv not found. Running with global python...
)

python main.py %*

if %errorlevel% neq 0 (
    echo.
    echo [OmniDev] Process exited with code %errorlevel%.
    pause
)
