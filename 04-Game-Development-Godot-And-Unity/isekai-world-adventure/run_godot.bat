@echo off
title OmniDev Godot 4 Launcher - iseaki_world_a_man_c
echo ========================================================
echo   OmniDev Sovereign Godot 4 Engine Launcher
echo   Project: iseaki_world_a_man_c
echo ========================================================
echo.

set GODOT_EXE=
where godot >nul 2>nul
if %ERRORLEVEL% equ 0 set GODOT_EXE=godot
where godot4 >nul 2>nul
if %ERRORLEVEL% equ 0 set GODOT_EXE=godot4

if "%GODOT_EXE%"=="" (
    for /r "%USERPROFILE%\Downloads" %%f in (Godot_v4*.exe) do if exist "%%f" set "GODOT_EXE=%%f"
)
if "%GODOT_EXE%"=="" (
    for /r "C:\Godot" %%f in (Godot*.exe) do if exist "%%f" set "GODOT_EXE=%%f"
)

if "%GODOT_EXE%"=="" (
    echo [INFO] Godot 4 executable was not found in PATH or Downloads.
    echo [INFO] Opening 3D First-Person Web Simulator in your browser...
    start "" "%~dp0simulator.html"
    echo.
    echo To open in Godot Engine:
    echo 1. Download Godot 4 from: https://godotengine.org/download
    echo 2. Open Godot -> Click 'Import' -> Select project.godot in this directory:
    echo    %~dp0
    echo.
    pause
    exit /b 0
)

echo [LAUNCH] Found Godot at: %GODOT_EXE%
echo [LAUNCH] Opening project in Godot 4 Editor...
start "" "%GODOT_EXE%" --path "%~dp0" -e
exit /b 0
