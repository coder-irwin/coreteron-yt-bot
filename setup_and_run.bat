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

REM 1. Detect Python Interpreter
set "PYTHON_CMD="

python --version >nul 2>&1
if %errorlevel% equ 0 set "PYTHON_CMD=python"

if "%PYTHON_CMD%"=="" (
    py --version >nul 2>&1
    if %errorlevel% equ 0 set "PYTHON_CMD=py"
)

if "%PYTHON_CMD%"=="" (
    if exist "%LocalAppData%\Programs\Python\Python311\python.exe" set "PYTHON_CMD=%LocalAppData%\Programs\Python\Python311\python.exe"
    if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PYTHON_CMD=%LocalAppData%\Programs\Python\Python312\python.exe"
    if exist "C:\Program Files\Python311\python.exe" set "PYTHON_CMD=C:\Program Files\Python311\python.exe"
    if exist "C:\Program Files\Python312\python.exe" set "PYTHON_CMD=C:\Program Files\Python312\python.exe"
)

REM 2. Auto-Install Python 3.11 if completely missing (no admin rights needed)
if "%PYTHON_CMD%"=="" (
    echo [!] Python is not detected on your system.
    echo [*] Downloading and installing Python 3.11 automatically...
    powershell -Command "Write-Host 'Downloading Python 3.11...'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile 'python_setup.exe'; Write-Host 'Installing Python 3.11...'; Start-Process -FilePath 'python_setup.exe' -ArgumentList '/quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_test=0' -Wait; Remove-Item 'python_setup.exe'"
    
    if exist "%LocalAppData%\Programs\Python\Python311\python.exe" (
        set "PYTHON_CMD=%LocalAppData%\Programs\Python\Python311\python.exe"
    ) else if exist "C:\Program Files\Python311\python.exe" (
        set "PYTHON_CMD=C:\Program Files\Python311\python.exe"
    ) else (
        python --version >nul 2>&1
        if %errorlevel% equ 0 set "PYTHON_CMD=python"
    )
)

if "%PYTHON_CMD%"=="" (
    echo [-] Python installation could not be completed automatically.
    echo [!] Please install Python manually from https://www.python.org/downloads/
    echo [!] Ensure you check: 'Add python.exe to PATH'
    pause
    exit /b 1
)

echo [+] Python interpreter detected:
"%PYTHON_CMD%" --version

REM 3. Create Isolated Virtual Environment
if not exist ".venv" (
    echo [+] Creating isolated virtual environment (.venv)...
    "%PYTHON_CMD%" -m venv .venv
)

REM 4. Locate Virtual Environment Executables
set "VENV_PYTHON=.venv\Scripts\python.exe"
if not exist "%VENV_PYTHON%" (
    set "VENV_PYTHON=%PYTHON_CMD%"
)

REM 5. Install / Update Dependencies
echo [+] Installing all required packages from requirements.txt...
"%VENV_PYTHON%" -m pip install -q --upgrade pip setuptools wheel
"%VENV_PYTHON%" -m pip install -q -r requirements.txt

REM 6. Install Playwright Chromium Browser
echo [+] Installing Playwright Chromium browser binary...
"%VENV_PYTHON%" -m playwright install chromium

REM 7. Ensure .env exists
if not exist ".env" (
    if exist ".env.example" (
        echo [+] Copying .env.example to .env...
        copy .env.example .env >nul
    )
)

REM 8. Launch Dashboard and Open Browser
echo ==================================================================
echo [+] Launching Web Dashboard at http://127.0.0.1:5055 ...
echo ==================================================================

start "" "http://127.0.0.1:5055"
"%VENV_PYTHON%" app.py

if %errorlevel% neq 0 (
    echo.
    echo [-] Application stopped with an exit code: %errorlevel%
    pause
)
