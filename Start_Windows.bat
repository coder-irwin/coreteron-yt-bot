@echo off
REM ==============================================================================
REM Coreteron YouTube View Automation Suite - Autonomous 1-Click Launcher (Windows)
REM ==============================================================================

setlocal enabledelayedexpansion
title Coreteron YouTube View Automation Dashboard

echo ========================================================================
echo     Coreteron Automation Labs - YouTube View Automation Dashboard
echo ========================================================================

cd /d "%~dp0"

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python 3 was not found in PATH.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo Initializing virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    playwright install chromium
) else (
    call .venv\Scripts\activate.bat
)

start "" http://127.0.0.1:5055

python app.py

pause
