@echo off
setlocal enabledelayedexpansion
title ProjectFlow Intelligence - Android APK Installer
color 0E

echo ======================================================================
echo          PROJECTFLOW INTELLIGENCE - ANDROID APK INSTALLER
echo ======================================================================
echo.

set "APK_PATH=releases\android\ProjectFlow-Intelligence-v2.0.0.apk"
if not exist "%APK_PATH%" (
    echo [ERROR] APK file not found at: %APK_PATH%
    pause
    exit /b 1
)

echo [INFO] Target APK: %APK_PATH%
echo.

:: Detect ADB
set "ADB_EXE="
where adb >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "ADB_EXE=adb"
) else if exist "%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe" (
    set "ADB_EXE=%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe"
)

if "%ADB_EXE%"=="" (
    echo [NOTICE] ADB command-line tool not found on this system.
    echo.
    echo Aap simply ye karein:
    echo 1. USB cable se phone ko laptop se connect karein.
    echo 2. File Explorer me jaake is file ko phone ke "Download" folder me copy karein:
    echo    "%~dp0releases\android\ProjectFlow-Intelligence-v2.0.0.apk"
    echo 3. Phone me File Manager kholke APK par tap karke "Install" kar lein!
    echo.
    pause
    exit /b 0
)

echo [INFO] Detected ADB at: %ADB_EXE%
echo [INFO] Checking connected Android devices...
echo.
"%ADB_EXE%" devices
echo.

echo Make sure USB Debugging is ENABLED on your phone.
set /p PROCEED="Do you want to install APK now? (Y/N) [Default: Y]: "
if /i "%PROCEED%"=="N" goto CANCEL

echo.
echo [INFO] Installing ProjectFlow APK on phone...
"%ADB_EXE%" install -r "%APK_PATH%"
if %ERRORLEVEL% equ 0 (
    echo.
    echo [SUCCESS] ProjectFlow v2.0.0 APK successfully installed!
    echo [INFO] Launching app on phone...
    "%ADB_EXE%" shell am start -n com.projectflow.android/.ui.SplashActivity >nul 2>&1
    echo [OK] App launched on screen.
) else (
    echo.
    echo [ERROR] Installation failed via ADB.
    echo Tip: Make sure phone screen is unlocked and USB Debugging prompt is accepted.
    echo Alternatively, copy "%APK_PATH%" directly to phone storage.
)

:CANCEL
echo.
pause
