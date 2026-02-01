@echo off
REM ================================================================
REM Project RawHorse - Quick Launch (Windows)
REM Run this after installation to start the application
REM ================================================================

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ================================================================
echo Project RawHorse - Starting Application
echo ================================================================
echo.

REM Check for venv in current directory first (standard install)
if exist "%SCRIPT_DIR%venv\Scripts\activate.bat" (
    set "VENV_PATH=%SCRIPT_DIR%venv"
    goto :found_venv
)

REM Check for venv one level up (some setups)
if exist "%SCRIPT_DIR%..\venv\Scripts\activate.bat" (
    set "VENV_PATH=%SCRIPT_DIR%..\venv"
    goto :found_venv
)

REM No venv found
echo ERROR: Project RawHorse is not installed yet!
echo.
echo Please run "install.bat" first to install dependencies.
echo Or run "START.bat" for guided installation.
echo.
pause
exit /b 1

:found_venv
echo Starting server...
echo Your browser will open automatically.
echo.
echo Press Ctrl+C to stop the server when done.
echo.

REM Activate virtual environment and start
call "%VENV_PATH%\Scripts\activate.bat"
cd "%SCRIPT_DIR%backend"
python main.py

pause
