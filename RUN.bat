@echo off
REM Project RawHorse - Quick Launch (Windows)
REM Run this after installation to start the application

echo ================================================================
echo Project RawHorse - Starting Application
echo ================================================================
echo.

REM Check if installed
if not exist "venv" (
    echo ERROR: Project RawHorse is not installed yet!
    echo.
    echo Please run "install.bat" first to install dependencies.
    echo.
    pause
    exit /b 1
)

echo Starting server...
echo Your browser will open automatically.
echo.
echo Press Ctrl+C to stop the server when done.
echo.

REM Activate virtual environment and start
call venv\Scripts\activate.bat
cd backend
python main.py

pause
