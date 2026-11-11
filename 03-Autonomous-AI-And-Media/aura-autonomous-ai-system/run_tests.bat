@echo off
TITLE "AURA - Run Unit & Integration Tests"
CD /D "%~dp0"
python -m pytest -v
PAUSE
