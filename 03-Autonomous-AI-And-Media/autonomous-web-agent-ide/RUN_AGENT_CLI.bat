@echo off
title Autonomous Web-Agent (Direct Python Mode)
cls

echo ====================================================================
echo          AUTONOMOUS WEB-AGENT - DIRECT PYTHON BROWSER RUNNER
echo ====================================================================
echo.

set /p PROMPT_INPUT="Enter your project requirement: "

if "%PROMPT_INPUT%"=="" (
    set PROMPT_INPUT=Build a full stack modern expense tracker application with React, Express, SQLite and tests
)

echo.
echo Running Python Agent with Playwright Browser LLM...
echo Project requirement: "%PROMPT_INPUT%"
echo.

cd /d %~dp0agent
python main.py --project-id project_one --run-id 1 --project-path ../workspace/project_one --prompt "%PROMPT_INPUT%" --provider smart --approval-mode AUTO

echo.
echo [DONE] Execution finished. Check your workspace/project_one folder!
pause
