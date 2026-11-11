@echo off
TITLE "AURA - Autonomous Local AI System"
CHCP 65001 > NUL
SETLOCAL EnableDelayedExpansion

:: Change directory to script directory
CD /D "%~dp0"

IF NOT "%~1"=="" (
    python main.py %*
    GOTO :EOF
)

:MENU
CLS
ECHO ================================================================
ECHO      AURA - Autonomous Local AI Research & Learning System
ECHO ================================================================
ECHO.
ECHO  [1] Start AURA (Live Ollama LLM Mode)
ECHO  [2] Start AURA (Mock Mode for Fast Testing)
ECHO  [3] Run Full Unit & Integration Test Suite
ECHO  [4] Exit
ECHO.
ECHO ================================================================
SET /P CHOICE="Select an option [1-4]: "

IF "%CHOICE%"=="1" GOTO RUN_LIVE
IF "%CHOICE%"=="2" GOTO RUN_MOCK
IF "%CHOICE%"=="3" GOTO RUN_TESTS
IF "%CHOICE%"=="4" GOTO END

ECHO Invalid choice. Please select 1, 2, 3, or 4.
TIMEOUT /T 2 > NUL
GOTO MENU

:RUN_LIVE
CLS
ECHO ================================================================
ECHO Starting AURA with Live Ollama Engine...
ECHO ================================================================
SET /P USER_GOAL="Enter learning goal (or press Enter for default): "
IF "!USER_GOAL!"=="" (
    python main.py --steps 5
) ELSE (
    python main.py --goal "!USER_GOAL!" --steps 5
)
PAUSE
GOTO MENU

:RUN_MOCK
CLS
ECHO ================================================================
ECHO Starting AURA with Mock Engine...
ECHO ================================================================
SET /P USER_GOAL="Enter learning goal (or press Enter for default): "
IF "!USER_GOAL!"=="" (
    python main.py --mock --steps 3
) ELSE (
    python main.py --goal "!USER_GOAL!" --mock --steps 3
)
PAUSE
GOTO MENU

:RUN_TESTS
CLS
ECHO ================================================================
ECHO Running AURA PyTest Suite...
ECHO ================================================================
python -m pytest -v
PAUSE
GOTO MENU

:END
ENDLOCAL
EXIT /B 0
