@echo off
REM Project RawHorse - Windows 1-Click Installer
REM This script automatically installs and runs Project RawHorse

echo ================================================================
echo Project RawHorse - Automated Installer for Windows
echo ================================================================
echo.
echo This will install Python dependencies and start the application.
echo.
pause

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python 3.10 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [1/5] Python found!
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed!
    echo.
    echo Please install Node.js 18 or higher from:
    echo https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo [2/5] Node.js found!
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [3/5] Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
) else (
    echo [3/5] Virtual environment already exists
)
echo.

REM Activate virtual environment and install backend dependencies
echo [4/5] Installing backend dependencies...
call venv\Scripts\activate.bat
cd backend
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)
cd ..

REM Install frontend dependencies
echo [5/5] Installing frontend dependencies...
cd frontend
if not exist "node_modules" (
    call npm install
    if errorlevel 1 (
        echo ERROR: Failed to install frontend dependencies
        pause
        exit /b 1
    )
) else (
    echo Frontend dependencies already installed
)

REM Build frontend
echo.
echo Building frontend...
call npm run build
if errorlevel 1 (
    echo ERROR: Failed to build frontend
    pause
    exit /b 1
)

REM Copy frontend to backend static
echo.
echo Copying frontend to backend...
xcopy /E /I /Y dist ..\backend\static >nul

cd ..

echo.
echo ================================================================
echo Installation Complete!
echo ================================================================
echo.
echo Starting Project RawHorse...
echo Your browser will open automatically.
echo.
echo Press Ctrl+C to stop the server when done.
echo.

REM Start the application
cd backend
python main.py

pause
