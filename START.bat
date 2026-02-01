@echo off
REM ================================================================
REM Project RawHorse - One-Click Starter (Windows)
REM Double-click this file to launch the application
REM ================================================================

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo.
echo  =====================================================================
echo   _____           _           _     _____            _    _                     
echo  ^|  __ \         ^(_^)         ^| ^|   ^|  __ \          ^| ^|  ^| ^|                    
echo  ^| ^|__^) ^|_ __ ___  _  ___  ___^| ^|_  ^| ^|__^) ^|__ ___      __^| ^|__^| ^| ___  _ __ ___  ___ 
echo  ^|  ___/^| '__/ _ \^| ^|/ _ \/ __^| __^| ^|  _  // _` \ \ /\ / /^| '__^| ^|/ _ \^| '__/ __^|/ _ \
echo  ^| ^|    ^| ^| ^| (_) ^| ^|  __/ (__^| ^|_  ^| ^| \ \ (_^| ^|\ V  V / ^| ^|  ^| ^| (_) ^| ^|  \__ \  __/
echo  ^|_^|    ^|_^|  \___/^| ^|\___^|\___^|\__^| ^|_^|  \_\__,_^| \_/\_/  ^|_^|  ^|_^|\___/^|_^|  ^|___/\___^|
echo                  _/ ^|                                                           
echo                 ^|__/                      UAP Data Intelligence Platform                                       
echo  =====================================================================
echo.
echo ================================================================
echo            Starting Application - Please Wait
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

REM No venv found - offer to install
echo [!] Virtual environment not found.
echo.
echo Would you like to install Project RawHorse now?
echo This requires Python 3.10+ and Node.js 18+ to be installed.
echo.
choice /C YN /M "Install now"
if errorlevel 2 goto :install_help
if errorlevel 1 goto :run_install

:install_help
echo.
echo To install manually, run: install.bat
echo.
pause
exit /b 1

:run_install
echo.
echo Starting installation...
call "%SCRIPT_DIR%install.bat"
exit /b %errorlevel%

:found_venv
echo [OK] Found virtual environment
echo.

REM Check if backend exists
if not exist "%SCRIPT_DIR%backend\main.py" (
    echo [ERROR] Backend not found at: %SCRIPT_DIR%backend
    echo.
    echo Please ensure you're running this from the Project RawHorse directory.
    pause
    exit /b 1
)

echo [OK] Backend found
echo.

REM Check if static files exist (frontend build)
if not exist "%SCRIPT_DIR%backend\static\index.html" (
    echo [!] Frontend not built - building now...
    echo.
    if exist "%SCRIPT_DIR%frontend\package.json" (
        cd "%SCRIPT_DIR%frontend"
        call npm install
        call npm run build
        if exist "dist\index.html" (
            xcopy /E /I /Y dist "%SCRIPT_DIR%backend\static" >nul
            echo [OK] Frontend built successfully
        ) else (
            echo [WARNING] Frontend build may have issues, continuing anyway...
        )
        cd "%SCRIPT_DIR%"
    )
)

echo.
echo ================================================================
echo Starting server at http://127.0.0.1:8000
echo Your browser will open automatically.
echo.
echo Press Ctrl+C to stop the server when done.
echo ================================================================
echo.

REM Activate virtual environment and start backend
call "%VENV_PATH%\Scripts\activate.bat"
cd "%SCRIPT_DIR%backend"
python main.py

pause
