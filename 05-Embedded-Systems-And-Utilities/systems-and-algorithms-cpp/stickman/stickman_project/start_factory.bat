@echo off
:: ============================================================
::  STICKMAN FACTORY — WINDOWS AUTO-STARTUP LAUNCHER
::  Place this file in:
::  shell:startup   (Win+R -> type: shell:startup -> Enter)
::  Ya manually run karo ek baar setup ke baad.
:: ============================================================

title STICKMAN FACTORY - AUTONOMOUS YOUTUBE SHORTS ENGINE
color 0A

echo.
echo ========================================================
echo    AI STICKMAN FACTORY - AUTONOMOUS ENGINE STARTING
echo ========================================================
echo.

:: --- Step 1: Project folder me jao ---
cd /d "C:\Users\abdul\source\repos\stickman\stickman_project"

:: --- Step 2: Internet check (loop until connected) ---
echo [NETWORK] Internet connection ka wait kar rahe hain...
:PING_LOOP
ping -n 1 8.8.8.8 >nul 2>&1
if errorlevel 1 (
    echo [WAITING] No internet... 5 seconds baad retry...
    timeout /t 5 /nobreak >nul
    goto PING_LOOP
)
echo [OK] Internet connected!

:: --- Step 3: Chrome ko debug mode mein launch karo ---
echo [CHROME] Remote debugging Chrome launch ho raha hai (port 9222)...

:: Pehle check karo koi purana chrome debug port pe chal raha hai ya nahi
netstat -ano | findstr :9222 >nul 2>&1
if not errorlevel 1 (
    echo [CHROME] Port 9222 already active - existing session reuse hogi.
    goto START_FACTORY
)

:: Chrome ka path dhundo
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set CHROME_EXE="C:\Program Files\Google\Chrome\Application\chrome.exe"
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set CHROME_EXE="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
) else (
    set CHROME_EXE="chrome.exe"
)

:: Chrome launch (persistent profile, debug port, no extra prompts)
start "" %CHROME_EXE% ^
    --remote-debugging-port=9222 ^
    --user-data-dir="C:\chrome_dev" ^
    --no-first-run ^
    --no-default-browser-check ^
    --disable-popup-blocking ^
    https://chat.deepseek.com https://studio.youtube.com

echo [CHROME] Chrome launching... 8 seconds wait...
timeout /t 8 /nobreak >nul

:: --- Step 4: DeepSeek login check (user ke liye) ---
echo.
echo [ACTION REQUIRED] Agar pehli baar chal raha hai:
echo   1. Chrome window mein chat.deepseek.com par login kar lo
echo   2. YouTube Studio mein apna channel logged-in confirm karo
echo.
echo [*] 15 seconds mein factory automatically shuru ho jayegi...
timeout /t 15 /nobreak >nul

:START_FACTORY
:: --- Step 5: Main factory pipeline run karo ---
echo.
echo [FACTORY] auto_factory_batch.py shuru ho raha hai...
echo ========================================================

python auto_factory_batch.py

:: --- Agar script khatam ho jaye toh 5 min baad restart ---
echo.
echo [DONE] Batch complete. 5 minute baad restart hoga...
timeout /t 300 /nobreak >nul
goto START_FACTORY
