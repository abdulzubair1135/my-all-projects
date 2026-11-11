@echo off
title OmniDev AI - One-Time Chrome Login
echo ================================================================
echo           OmniDev AI - One-Time Chrome Browser Setup
echo ================================================================
echo.
echo Launching Google Chrome with persistent session and debug port 9222...
echo.
echo INSTRUCTIONS:
echo 1. Chrome will open DeepSeek and Gemini.
echo 2. Please log into your DeepSeek account (and Gemini if you wish).
echo 3. Once logged in, your session is permanently saved in:
echo    "%~dp0chrome_profile"
echo 4. You can keep Chrome open, or close it whenever you want.
echo    OmniDev AI will connect to this session automatically!
echo.
echo ================================================================

set "CHROME_PATH="
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set "CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe"
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set "CHROME_PATH=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
) else if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
    set "CHROME_PATH=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
) else (
    set "CHROME_PATH=chrome.exe"
)

start "" "%CHROME_PATH%" --remote-debugging-port=9222 --user-data-dir="%~dp0chrome_profile" "https://chat.deepseek.com" "https://gemini.google.com"

echo.
echo Chrome has been started. Please log in in the browser window.
echo Press any key to exit this helper window...
pause >nul
