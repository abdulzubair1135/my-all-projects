@echo off
title START DEEPSEEK CHROME (PORT 9222)
echo ========================================================
echo   LAUNCHING CHROME FOR STICKMAN FACTORY (PORT 9222)
echo ========================================================
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome_dev" --no-first-run --no-default-browser-check https://chat.deepseek.com https://studio.youtube.com
echo Chrome Launched with DeepSeek and YouTube Studio!
