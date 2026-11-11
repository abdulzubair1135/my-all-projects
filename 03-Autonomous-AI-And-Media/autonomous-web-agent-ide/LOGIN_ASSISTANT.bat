@echo off
chcp 65001 >nul
title AI Browser Login Assistant
cls

echo ====================================================================
echo             AUTONOMOUS WEB-AGENT - BROWSER LOGIN ASSISTANT
echo ====================================================================
echo.
echo Select which AI provider you want to log in to:
echo.
echo  [1] DeepSeek Web   (chat.deepseek.com)
echo  [2] Google Gemini  (gemini.google.com)
echo  [3] ChatGPT Web    (chatgpt.com)
echo.
set /p CHOICE="Enter choice (1, 2, or 3) [default=1]: "

if "%CHOICE%"=="" set CHOICE=1

echo.
cd /d %~dp0agent
python browser/login_helper.py %CHOICE%

echo.
pause
