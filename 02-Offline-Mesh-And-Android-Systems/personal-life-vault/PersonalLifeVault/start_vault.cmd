@echo off
title PERSONAL LIFE VAULT - SERVER & TUNNEL
color 0A
cls
echo.
echo  =============================================================
echo    🟢 PERSONAL LIFE VAULT SERVER IS STARTING...
echo  =============================================================
echo.
echo    Server URL : http://localhost:8088
echo    Ngrok URL  : https://illusion-roundish-configure.ngrok-free.dev
echo.
echo    Status     : Mobile app will connect automatically within 1 min!
echo    Note       : Do NOT close this window if you want server ON.
echo  =============================================================
echo.

cd /d "C:\Users\abdul\OneDrive\9831~1\sthelp\PersonalLifeVault\server"

:: Open browser after 3 seconds when port 8088 is open
start /b cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:8088"

node --experimental-sqlite server.js

