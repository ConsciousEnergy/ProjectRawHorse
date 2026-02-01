@echo off
REM ================================================================
REM Project RawHorse - Windows 1-Click Installer
REM This script automatically installs and runs Project RawHorse
REM ================================================================

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo.
echo  ____            _           _     ____              _   _                     
echo ^|  _ \ _ __ ___ ^| ^| ___  ___^| ^|_  ^|  _ \ __ ___      ^| ^| ^| ^| ___  _ __ ___  ___ 
echo ^| ^|_^) ^| '__/ _ \^| ^|/ _ \/ __^| __^| ^| ^|_) / _` \ \ /\ / / ^| ^|/ _ \^| '__/ __^|/ _ \
echo ^|  __/^| ^| ^| (_) ^| ^|  __/ (__^| ^|_  ^|  _ ^< (_^| ^|\ V  V /^| ^| ^| (_) ^| ^|  \__ \  __/
echo ^|_^|   ^|_^|  \___/^|_^|\___^|\___^|\__^| ^|_^| \_\__,_^| \_/\_/ ^|_^|_\___/^|_^|  ^|___/\___^|
echo.
echo ================================================================
echo       Automated Installer for Windows
echo ================================================================
echo.
echo This will install Python dependencies and start the application.
echo Installation typically takes 5-10 minutes on first run.
echo.
pause

REM ================================================================
REM Step 1: Check Python
REM ================================================================
echo.
echo [1/6] Checking Python installation...

python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.10 or higher from:
    echo   https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo        Python %PYVER% found [OK]

REM ================================================================
REM Step 2: Check Node.js
REM ================================================================
echo.
echo [2/6] Checking Node.js installation...

node --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Node.js is not installed or not in PATH!
    echo.
    echo Please install Node.js 18 or higher from:
    echo   https://nodejs.org/
    echo.
    pause
    exit /b 1
)

for /f %%v in ('node --version 2^>^&1') do set NODEVER=%%v
echo        Node.js %NODEVER% found [OK]

REM ================================================================
REM Step 3: Create Virtual Environment
REM ================================================================
echo.
echo [3/6] Setting up Python virtual environment...

REM Check if venv already exists
if exist "%SCRIPT_DIR%venv\Scripts\activate.bat" (
    echo        Virtual environment already exists [OK]
    set "VENV_PATH=%SCRIPT_DIR%venv"
    goto :install_backend
)

REM Check one level up (for some setups)
if exist "%SCRIPT_DIR%..\venv\Scripts\activate.bat" (
    echo        Found existing virtual environment [OK]
    set "VENV_PATH=%SCRIPT_DIR%..\venv"
    goto :install_backend
)

REM Create new virtual environment
echo        Creating new virtual environment...
python -m venv venv
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to create virtual environment
    echo Try running: python -m pip install --upgrade pip virtualenv
    pause
    exit /b 1
)
set "VENV_PATH=%SCRIPT_DIR%venv"
echo        Virtual environment created [OK]

:install_backend
REM ================================================================
REM Step 4: Install Backend Dependencies
REM ================================================================
echo.
echo [4/6] Installing backend dependencies...
echo        This may take a few minutes...

call "%VENV_PATH%\Scripts\activate.bat"

cd "%SCRIPT_DIR%backend"
pip install --upgrade pip --quiet 2>nul
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install backend dependencies
    echo.
    echo Try running manually:
    echo   cd backend
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)
echo        Backend dependencies installed [OK]

REM ================================================================
REM Step 5: Install Frontend Dependencies
REM ================================================================
echo.
echo [5/6] Installing frontend dependencies...

cd "%SCRIPT_DIR%frontend"

if exist "node_modules" (
    echo        Frontend dependencies already installed [OK]
) else (
    echo        Running npm install...
    call npm install --silent 2>nul
    if errorlevel 1 (
        echo.
        echo [WARNING] npm install had issues, trying without --silent...
        call npm install
    )
    echo        Frontend dependencies installed [OK]
)

REM ================================================================
REM Step 6: Build Frontend
REM ================================================================
echo.
echo [6/6] Building frontend...

call npm run build 2>nul
if errorlevel 1 (
    echo.
    echo [WARNING] Frontend build had issues, trying alternative approach...
    call npm run build
)

if exist "dist\index.html" (
    echo        Frontend built [OK]
    
    REM Copy to backend static folder
    echo        Copying to backend...
    if not exist "%SCRIPT_DIR%backend\static" mkdir "%SCRIPT_DIR%backend\static"
    xcopy /E /I /Y dist "%SCRIPT_DIR%backend\static" >nul 2>&1
    echo        Frontend deployed [OK]
) else (
    echo.
    echo [WARNING] Frontend build incomplete - application may run in API-only mode
)

cd "%SCRIPT_DIR%"

REM ================================================================
REM Installation Complete!
REM ================================================================
echo.
echo ================================================================
echo             Installation Complete!
echo ================================================================
echo.
echo You can now:
echo   - Double-click START.bat to launch the application
echo   - Double-click LaunchRawHorse.vbs for icon support
echo.
echo Starting Project RawHorse now...
echo Your browser will open automatically at http://127.0.0.1:8000
echo.
echo Press Ctrl+C to stop the server when done.
echo ================================================================
echo.

REM Start the application
cd "%SCRIPT_DIR%backend"
python main.py

pause
