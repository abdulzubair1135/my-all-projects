@echo off
chcp 65001 >nul
title DeepSeek Web Login Assistant
cls

echo ====================================================================
echo               DEEPSEEK WEB ONE-CLICK LOGIN ASSISTANT
echo ====================================================================
echo.
echo Launching persistent Chromium browser window...
echo Please log in with your DeepSeek account (Email/Google/Phone).
echo Once logged in, your session is saved permanently in browser-profile/!
echo.

cd /d %~dp0agent
python browser/login_helper.py https://chat.deepseek.com

echo.
pause
