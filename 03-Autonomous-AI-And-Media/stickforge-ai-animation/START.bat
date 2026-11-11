@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: STICKFORGE AI - ALL-IN-ONE MASTER STUDIO LAUNCHER
:: ============================================================================

title StickForge AI Studio

:: If arguments were passed directly from command line, run pipeline immediately
if not "%~1"=="" (
    python main.py %*
    goto :end
)

:menu
cls
echo ========================================================================
echo              STICKFORGE AI STUDIO - ALL-IN-ONE LAUNCHER
echo ========================================================================
echo.
echo   [1] Create Stickman Video (Automated AI Pipeline)
echo   [2] Connect DeepSeek Browser (Login Once - Port 9222)
echo   [3] Launch Desktop GUI Studio (Full Visual Workspace)
echo   [4] Run System Diagnostics and Health Check
echo   [5] Setup and Install Dependencies
echo   [0] Exit
echo.
echo ========================================================================
set "CHOICE="
set /p "CHOICE=Select an option [1-5, or 0 to exit] (Default: 1): "

if "%CHOICE%"=="" set "CHOICE=1"
if "%CHOICE%"=="1" goto :opt_pipeline
if "%CHOICE%"=="2" goto :opt_deepseek
if "%CHOICE%"=="3" goto :opt_gui
if "%CHOICE%"=="4" goto :opt_diag
if "%CHOICE%"=="5" goto :opt_setup
if "%CHOICE%"=="0" goto :opt_exit

echo.
echo [!] Invalid option selected. Please choose 1, 2, 3, 4, 5, or 0.
ping -n 2 127.0.0.1 >nul
goto :menu

:: ============================================================================
:: OPTION 1: RUN AUTOMATED PIPELINE
:: ============================================================================
:opt_pipeline
cls
echo ========================================================================
echo   [1] STICKFORGE AI - CREATE STICKMAN VIDEO
echo ========================================================================
echo.
python main.py
echo.
echo ========================================================================
echo Press any key to return to main menu...
pause >nul
goto :menu

:: ============================================================================
:: OPTION 2: CONNECT DEEPSEEK BROWSER
:: ============================================================================
:opt_deepseek
cls
echo ========================================================================
echo   [2] CONNECT DEEPSEEK BROWSER (PORT 9222)
echo ========================================================================
echo.

:: Define Profile Directory
set "PROFILE_DIR=%LOCALAPPDATA%\StickForgeAI\deepseek_profile"
if not exist "%PROFILE_DIR%" (
    mkdir "%PROFILE_DIR%" 2>nul
)

:: Locate Chrome / Chromium
set "CHROME_BIN="
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set "CHROME_BIN=C:\Program Files\Google\Chrome\Application\chrome.exe"
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set "CHROME_BIN=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
) else if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
    set "CHROME_BIN=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
) else if exist "C:\Program Files\Microsoft\Edge\Application\msedge.exe" (
    set "CHROME_BIN=C:\Program Files\Microsoft\Edge\Application\msedge.exe"
)

if "%CHROME_BIN%"=="" (
    where chrome.exe >nul 2>&1
    if !errorlevel! equ 0 (
        set "CHROME_BIN=chrome.exe"
    ) else (
        for /d %%D in ("%LOCALAPPDATA%\ms-playwright\chromium-*") do (
            if exist "%%D\chrome-win64\chrome.exe" set "CHROME_BIN=%%D\chrome-win64\chrome.exe"
        )
    )
)

if "%CHROME_BIN%"=="" (
    echo [ERROR] No compatible Chrome or Chromium browser installation found.
    echo Please install Google Chrome to use DeepSeek browser automation.
    pause
    goto :menu
)

echo [*] Browser: %CHROME_BIN%
echo [*] Profile: %PROFILE_DIR%
echo [*] Remote Debugging Port: 9222
echo [*] Opening https://chat.deepseek.com...
echo.
echo Please log into DeepSeek once in the opened window.
echo Your session and cookies will persist permanently.
echo.

start "" "%CHROME_BIN%" --remote-debugging-port=9222 --user-data-dir="%PROFILE_DIR%" --no-first-run --no-default-browser-check "https://chat.deepseek.com"

echo [OK] Chrome launched on port 9222.
echo.
echo Press any key to return to main menu...
pause >nul
goto :menu

:: ============================================================================
:: OPTION 3: LAUNCH DESKTOP GUI STUDIO
:: ============================================================================
:opt_gui
cls
echo ========================================================================
echo   [3] LAUNCHING STICKFORGE AI DESKTOP GUI STUDIO...
echo ========================================================================
echo.
python -m app.main
if !errorlevel! neq 0 (
    echo.
    echo [ERROR] Desktop GUI exited with error code !errorlevel!.
    pause
)
goto :menu

:: ============================================================================
:: OPTION 4: SYSTEM DIAGNOSTICS & TESTS
:: ============================================================================
:opt_diag
cls
echo ========================================================================
echo   [4] SYSTEM DIAGNOSTICS AND AUTOMATED TESTS
echo ========================================================================
echo.
python -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); from main import run_environment_check; run_environment_check()"
echo.
echo [*] Running full test suite (pytest)...
echo.
pytest -q
echo.
echo ========================================================================
echo Press any key to return to main menu...
pause >nul
goto :menu

:: ============================================================================
:: OPTION 5: SETUP DEPENDENCIES
:: ============================================================================
:opt_setup
cls
echo ========================================================================
echo   [5] SETUP AND DEPENDENCY INSTALLATION
echo ========================================================================
echo.
echo [*] Installing requirements from requirements.txt...
python -m pip install -r requirements.txt --upgrade
echo.
echo [*] Installing Playwright Chromium browser...
python -m playwright install chromium
echo.
echo [OK] All dependencies successfully verified and up to date!
echo.
echo Press any key to return to main menu...
pause >nul
goto :menu

:opt_exit
cls
echo.
echo Thank you for using StickForge AI Studio!
echo.
exit /b 0

:end
