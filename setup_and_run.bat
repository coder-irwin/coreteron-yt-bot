@echo off
REM ==============================================================================
REM Coreteron YouTube View Automation Suite - Autonomous End-to-End Setup & Runner (Windows)
REM Zero technical expertise, signup, or login required.
REM Double-click this file to install everything and start the web dashboard!
REM ==============================================================================

cd /d "%~dp0"
title Coreteron YouTube View Automation Suite

echo ==================================================================
echo     CORETERON YOUTUBE VIEW SUITE - AUTONOMOUS INSTALLER (WINDOWS)
echo ==================================================================

REM 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=py
    ) else (
        echo [!] Python is not detected on your system.
        echo [*] Attempting automated Python 3 installation via PowerShell...
        powershell -Command "Write-Host 'Downloading Python installer...'; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile 'python_setup.exe'; Write-Host 'Installing Python (please wait)...'; Start-Process -FilePath 'python_setup.exe' -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait; Remove-Item 'python_setup.exe'"
        python --version >nul 2>&1
        if %errorlevel% neq 0 (
            echo [-] Automated installer finished, but Python is not yet in current session PATH.
            echo [!] Please restart this file or download Python from https://www.python.org/downloads/
            echo [!] Ensure you check: 'Add python.exe to PATH'
            pause
            exit /b 1
        )
        set PYTHON_CMD=python
    )
) else (
    set PYTHON_CMD=python
)

echo [+] Python detected:
%PYTHON_CMD% --version

REM 2. Create Virtual Environment
if not exist ".venv" (
    echo [+] Creating isolated virtual environment (.venv)...
    %PYTHON_CMD% -m venv .venv
)

REM 3. Activate Virtual Environment
call .venv\Scripts\activate.bat

REM 4. Install / Update Dependencies
echo [+] Installing all required packages from requirements.txt...
python -m pip install -q --upgrade pip setuptools wheel
python -m pip install -q -r requirements.txt

REM 5. Install Playwright Chromium Browser
echo [+] Installing Playwright Chromium browser...
python -m playwright install chromium

REM 6. Ensure .env exists
if not exist ".env" (
    if exist ".env.example" (
        echo [+] Copying .env.example to .env...
        copy .env.example .env >nul
    )
)

REM 7. Launch Dashboard and Open Browser
echo ==================================================================
echo [+] Launching Web Dashboard at http://127.0.0.1:5055 ...
echo ==================================================================

start "" "http://127.0.0.1:5055"
python app.py

pause
