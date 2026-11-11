@echo off
title OmniDev Android Deployer - stopwatch_app
echo ========================================================
echo   OmniDev Native Android Builder & Deployer
echo   Project: stopwatch_app
echo ========================================================
echo.

:: 1. Check for ADB
set ADB_PATH=adb
where adb >nul 2>nul
if %ERRORLEVEL% neq 0 (
    if exist "%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe" (
        set "ADB_PATH=%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe"
    ) else if exist "%ANDROID_HOME%\platform-tools\adb.exe" (
        set "ADB_PATH=%ANDROID_HOME%\platform-tools\adb.exe"
    ) else (
        echo [INFO] ADB (Android Debug Bridge) is not installed in PATH.
        echo [INFO] Opening instant Web Mobile Phone Simulator in your browser...
        start "" "%~dp0simulator.html"
        echo.
        echo Project files are ready for Android Studio in: %~dp0
        echo Press any key to exit.
        pause >nul
        exit /b 0
    )
)

:: 2. Check for connected devices
echo [ADB] Checking for connected Android devices...
"%ADB_PATH%" devices

:: 3. Build APK
echo.
echo [BUILD] Building Android APK...
if exist gradlew.bat (
    call gradlew.bat assembleDebug
) else (
    echo [NOTE] Please open this directory in Android Studio to compile APK.
)

:: 4. Install if APK exists
if exist "app\build\outputs\apk\debug\app-debug.apk" (
    echo [INSTALL] Deploying APK to device...
    "%ADB_PATH%" install -r app\build\outputs\apk\debug\app-debug.apk
    echo [DONE] Application successfully installed on phone!
) else (
    echo [INFO] Launching Mobile Phone Simulator for instant preview...
    start "" "%~dp0simulator.html"
)

pause
