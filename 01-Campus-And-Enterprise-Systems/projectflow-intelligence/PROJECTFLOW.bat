@echo off
setlocal enabledelayedexpansion
title ProjectFlow Intelligence - Master Control
color 0A

:: Safety mapping for non-ASCII or deep OneDrive paths
if not exist "P:\" (
    subst P: "%~dp0" >nul 2>&1
)
if exist "P:\" (
    cd /d "P:\"
) else (
    cd /d "%~dp0"
)

:MENU
cls
echo ======================================================================
echo              PROJECTFLOW INTELLIGENCE - MASTER CONSOLE
echo ======================================================================
echo.
echo   [1] Start Website & Full-Stack Server (Opens http://localhost:8082)
echo   [2] Open Live Render Cloud Website (https://projectflow-intelligence.onrender.com)
echo   [3] Compile & Install Android App on Phone (ADB)
echo   [4] Stop / Close All Running Services
echo   [5] Check System Health & Database Status
echo   [6] Exit Console
echo.
echo ======================================================================
set /p OPT="Enter your choice (1-6) [Default: 1]: "
if "%OPT%"=="" set OPT=1

if "%OPT%"=="1" goto START_WEBSITE
if "%OPT%"=="2" goto OPEN_RENDER
if "%OPT%"=="3" goto INSTALL_ANDROID
if "%OPT%"=="4" goto STOP_SERVICES
if "%OPT%"=="5" goto CHECK_STATUS
if "%OPT%"=="6" goto EXIT_SCRIPT

echo.
echo [!] Invalid option. Please enter a number between 1 and 6.
timeout /t 2 >nul
goto MENU

:START_WEBSITE
cls
echo ======================================================================
echo                  STARTING PROJECTFLOW WEBSITE
echo ======================================================================
echo.
netstat -aon | findstr :8082 | findstr LISTENING >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [OK] ProjectFlow Server is already running on port 8082.
) else (
    echo [INFO] Starting Full-Stack Node.js Server on port 8082...
    start "ProjectFlow Web Server [Port 8082]" cmd /k "node server.js"
    timeout /t 3 >nul
)

echo [INFO] Launching Web Control Panel in your default browser...
start http://localhost:8082

echo.
echo [SUCCESS] Website opened successfully!
echo   * URL:         http://localhost:8082
echo   * Credentials: admin@projectflow.io / ProjectFlow@2026
echo.
pause
goto MENU

:OPEN_RENDER
cls
echo ======================================================================
echo              OPENING LIVE RENDER PRODUCTION CLOUD
echo ======================================================================
echo.
echo [INFO] Opening https://projectflow-intelligence.onrender.com...
start https://projectflow-intelligence.onrender.com
echo.
echo [OK] Opened in your default browser.
echo.
pause
goto MENU

:INSTALL_ANDROID
cls
echo ======================================================================
echo              BUILD & INSTALL ANDROID APP ON PHONE
echo ======================================================================
echo.
set "ADB_EXE=%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe"
if not exist "%ADB_EXE%" (
    echo [ERROR] ADB not found at %ADB_EXE%.
    pause
    goto MENU
)

echo [INFO] Checking connected devices...
"%ADB_EXE%" devices
echo.

echo [INFO] Compiling updated Android APK via Gradle...
call .\gradlew.bat assembleDebug -PbuildDir=C:/temp/projectflow_build
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Build failed! Check Gradle output above.
    pause
    goto MENU
)

set "APK_SRC=C:\temp\projectflow_build\android-app\outputs\apk\debug\android-app-debug.apk"
set "APK_DST=releases\android\ProjectFlow-Intelligence-v2.0.0.apk"
if exist "%APK_SRC%" (
    copy /Y "%APK_SRC%" "%APK_DST%" >nul 2>&1
)

echo [INFO] Installing APK on your device...
"%ADB_EXE%" install -r "%APK_SRC%"

echo [INFO] Starting ProjectFlow on device...
"%ADB_EXE%" shell am start -n com.projectflow.android/.ui.MainActivity >nul 2>&1

echo.
echo [SUCCESS] App installed and launched on your phone!
echo.
pause
goto MENU

:STOP_SERVICES
cls
echo ======================================================================
echo                    STOPPING ALL SERVICES
echo ======================================================================
echo.
echo [INFO] Terminating processes on port 8082...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8082 ^| findstr LISTENING') do (
    echo   Stopping PID %%a
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo [OK] All ProjectFlow services have been terminated.
echo.
pause
goto MENU

:CHECK_STATUS
cls
echo ======================================================================
echo                    SYSTEM HEALTH & DIAGNOSTICS
echo ======================================================================
echo.
echo [1] Checking Local Server (Port 8082)...
netstat -aon | findstr :8082 | findstr LISTENING >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo   [OK] Local Server: ONLINE (Port 8082)
) else (
    echo   [OFFLINE] Local Server is not currently running.
)

echo.
echo [2] Checking Render Cloud Service...
curl.exe -m 10 -s -o - https://projectflow-intelligence.onrender.com/api/v1/admin/overview
echo.

echo.
echo [3] Checking Android ADB Connection...
set "ADB_EXE=%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe"
if exist "%ADB_EXE%" (
    "%ADB_EXE%" devices
) else (
    echo   [WARN] ADB path not found.
)

echo.
pause
goto MENU

:EXIT_SCRIPT
exit /b 0
