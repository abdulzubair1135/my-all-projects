@echo off
title AUTO YT GENERATOR - AI Studio
color 0b

echo ================================================================
echo           AUTO YT GENERATOR - AI Studio Launcher
echo ================================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    color 0c
    echo [ERROR] Python is not found in your system PATH!
    echo Please install Python 3.10+ and check "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

:: Set Python path to current workspace
set PYTHONPATH=%CD%

:: Run interactive CLI menu
python app/main.py info
echo.
echo ================================================================
echo Quick Actions:
echo  1. Launch Graphical Desktop Studio (GUI)
echo  2. Open / Watch Rendered Videos Folder
echo  3. List all projects in Terminal
echo  4. Create a new video project (CLI)
echo  5. Generate and Render FULL 1080p MP4 Video (1-Click)
echo  6. Generate Standalone Phonk Beat (Music Mode)
echo  7. Exit
echo ================================================================
echo.

set /p choice="Enter option (1-7): "

if "%choice%"=="1" (
    cls
    echo Launching Desktop GUI Studio...
    python app/main.py gui
    exit /b 0
)

if "%choice%"=="2" (
    cls
    echo Opening Projects & Videos folder...
    explorer projects
    exit /b 0
)

if "%choice%"=="3" (
    cls
    python app/main.py list-projects
    echo.
    pause
    exit /b 0
)

if "%choice%"=="4" (
    cls
    echo Create New Video Project
    echo ------------------------
    set /p topic="Enter Video Topic: "
    set /p style="Enter Style (dark_cartoon / dark_science / documentary) [default: dark_cartoon]: "
    if "%style%"=="" set style=dark_cartoon
    set /p lang="Enter Language (en / hi / ur) [default: en]: "
    if "%lang%"=="" set lang=en
    set /p dur="Enter Target Duration in seconds [default: 180]: "
    if "%dur%"=="" set dur=180

    python app/main.py new-project --topic "%topic%" --style "%style%" --language "%lang%" --duration %dur%
    echo.
    pause
    exit /b 0
)

if "%choice%"=="5" (
    cls
    python app/main.py list-projects
    echo.
    set /p pid="Enter Project ID to generate and render: "
    if not "%pid%"=="" (
        echo.
        echo Starting 1-Click Automated Generation Pipeline...
        python app/main.py render-video %pid% --fps 30
        echo.
        echo [SUCCESS] 1080p MP4 Video is ready in projects\%pid%\final\video.mp4!
    )
    pause
    exit /b 0
)

if "%choice%"=="6" (
    cls
    echo Generate Phonk Beat
    echo -------------------
    set /p dur="Enter Duration in seconds [default: 30]: "
    if "%dur%"=="" set dur=30
    set /p bpm="Enter BPM [default: 145]: "
    if "%bpm%"=="" set bpm=145

    python app/main.py generate-phonk --duration %dur% --bpm %bpm%
    echo.
    pause
    exit /b 0
)

if "%choice%"=="7" (
    exit /b 0
)

pause
