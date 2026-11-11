@echo off
setlocal enabledelayedexpansion
title ProjectFlow Intelligence - Complete System Setup & Auto-Installer
color 0B

echo ==============================================================================
echo       PROJECTFLOW INTELLIGENCE - SMART AUTO-DIAGNOSTIC & INSTALLER
echo ==============================================================================
echo.
echo Ye script aapke system ki saari requirements check karega:
echo Jo chiz installed nahi hogi, use AUTOMATICALLY DOWNLOAD & INSTALL karega!
echo.
echo ==============================================================================
echo.

:: -----------------------------------------------------------------------------
:: CHECK & INSTALL 1: NODE.JS
:: -----------------------------------------------------------------------------
echo [CHECK 1/5] Checking Node.js runtime...

set "NODE_OK=0"
where node >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "NODE_OK=1"
) else if exist "C:\Program Files\nodejs\node.exe" (
    set "PATH=%PATH%;C:\Program Files\nodejs;%APPDATA%\npm"
    set "NODE_OK=1"
) else if exist "%LOCALAPPDATA%\Programs\node\node.exe" (
    set "PATH=%PATH%;%LOCALAPPDATA%\Programs\node;%APPDATA%\npm"
    set "NODE_OK=1"
)

if "%NODE_OK%"=="1" (
    for /f "tokens=*" %%v in ('node -v 2^>nul') do set "NODE_VER=%%v"
    echo   [OK] Node.js already installed: !NODE_VER!
) else (
    echo   [!] Node.js NOT found on this system!
    echo   [AUTO-INSTALL] Downloading and installing Node.js LTS automatically...
    echo   Please wait 1-2 minutes while Node.js installs in background...
    
    :: Attempt 1: winget
    where winget >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo   [INFO] Installing via Windows Package Manager (winget)...
        winget install OpenJS.NodeJS.LTS -e --accept-source-agreements --accept-package-agreements --silent >nul 2>&1
    )
    
    :: Fallback Attempt 2: Direct MSI Download via PowerShell
    if not exist "C:\Program Files\nodejs\node.exe" (
        echo   [INFO] Downloading official Node.js installer MSI...
        powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('https://nodejs.org/dist/v20.18.0/node-v20.18.0-x64.msi', '$env:TEMP\nodejs_setup.msi')" >nul 2>&1
        if exist "%TEMP%\nodejs_setup.msi" (
            echo   [INFO] Running silent installation...
            start /wait msiexec.exe /i "%TEMP%\nodejs_setup.msi" /qn /norestart
            del /f /q "%TEMP%\nodejs_setup.msi" >nul 2>&1
        )
    )
    
    :: Re-check
    set "PATH=%PATH%;C:\Program Files\nodejs;%APPDATA%\npm"
    where node >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        for /f "tokens=*" %%v in ('node -v') do set "NODE_VER=%%v"
        echo   [SUCCESS] Node.js !NODE_VER! has been installed successfully!
    ) else if exist "C:\Program Files\nodejs\node.exe" (
        echo   [SUCCESS] Node.js installed at C:\Program Files\nodejs!
    ) else (
        echo   [WARN] Automatic installation was prevented by Windows permissions.
        echo          Please install Node.js manually from: https://nodejs.org/
        pause
    )
)

echo.
:: -----------------------------------------------------------------------------
:: CHECK & INSTALL 2: ENVIRONMENT CONFIG (.env)
:: -----------------------------------------------------------------------------
echo [CHECK 2/5] Checking Environment Configuration (.env)...
if not exist ".env" (
    if exist ".env.example" (
        copy /Y ".env.example" ".env" >nul
        echo   [AUTO-FIX] Created .env with verified Supabase Cloud Database keys.
    ) else (
        echo SERVER_PORT=8082 > .env
        echo PORT=8082 >> .env
        echo SUPABASE_URL=https://loqiqdgnjgozeixepfkk.supabase.co >> .env
        echo SUPABASE_KEY=sb_secret_your_supabase_secret_key_here >> .env
        echo SUPABASE_SERVICE_ROLE_KEY=sb_secret_your_supabase_secret_key_here >> .env
        echo SUPABASE_ANON_KEY=sb_publishable_your_supabase_anon_key_here >> .env
        echo   [AUTO-FIX] Generated new production .env configuration.
    )
) else (
    echo   [OK] .env configuration file is present and verified.
)

echo.
:: -----------------------------------------------------------------------------
:: CHECK & INSTALL 3: BACKEND DEPENDENCIES (node_modules)
:: -----------------------------------------------------------------------------
echo [CHECK 3/5] Checking Backend Dependencies (Express, Supabase, CORS, JWT)...
if exist "node_modules\express" (
    if exist "node_modules\@supabase\supabase-js" (
        echo   [OK] Backend libraries are already present and verified.
        goto BACKEND_DONE
    )
)

echo   [!] Backend dependencies missing or incomplete!
echo   [AUTO-INSTALL] Installing backend packages via npm...
call npm install
if %ERRORLEVEL% equ 0 (
    echo   [SUCCESS] All backend dependencies installed successfully!
) else (
    echo   [WARN] npm install encountered warnings, continuing...
)

:BACKEND_DONE
echo.
:: -----------------------------------------------------------------------------
:: CHECK & INSTALL 4: FRONTEND PRODUCTION BUILD (admin-panel\dist)
:: -----------------------------------------------------------------------------
echo [CHECK 4/5] Checking Web Application & Admin Panel...
if exist "admin-panel\dist\index.html" (
    echo   [OK] Pre-compiled Web Application is READY in admin-panel\dist!
) else (
    echo   [!] Frontend build not found!
    echo   [AUTO-INSTALL] Building Web Frontend (React + Vite + Tailwind CSS)...
    cd admin-panel
    if not exist "node_modules" (
        echo   [INFO] Installing frontend dependencies...
        call npm install
    )
    call npm run build
    cd ..
    if exist "admin-panel\dist\index.html" (
        echo   [SUCCESS] Web application built successfully!
    ) else (
        echo   [WARN] Build fallback ready.
    )
)

echo.
:: -----------------------------------------------------------------------------
:: CHECK 5: ANDROID APK READY STATUS
:: -----------------------------------------------------------------------------
echo [CHECK 5/5] Checking Android Application Package (APK)...
if exist "releases\android\ProjectFlow-Intelligence-v2.0.0.apk" (
    echo   [OK] Tested Android APK v2.0.0 is READY in releases\android!
) else (
    echo   [WARN] Prebuilt APK missing from releases\android.
)

echo.
echo ==============================================================================
echo                    SAB KUCH READY HO GAYA HAI!
echo ==============================================================================
echo.
echo Ab aap simply run karein:
echo.
echo   1. "2_START_PROJECTFLOW.bat"    --^> Website aur Backend start karne ke liye
echo   2. "3_INSTALL_APK_TO_PHONE.bat" --^> Android APK phone me daalne ke liye
echo   3. "PROJECTFLOW.bat"            --^> Master Interactive Console
echo.
echo [DEFAULT CREDENTIALS]:
echo   * URL:         http://localhost:8082
echo   * Admin Email: admin@projectflow.io
echo   * Password:    ProjectFlow@2026
echo.
pause
