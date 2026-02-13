@echo off
setlocal enabledelayedexpansion
title Project RawHorse Uninstaller

REM Get project root (directory where this script lives)
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
cd /d "%SCRIPT_DIR%"

REM Check for /force to skip prompts
set "FORCE=0"
if /i "%~1"=="/force" set "FORCE=1"
if /i "%~1"=="-y" set "FORCE=1"

echo ============================================================
echo   Project RawHorse - Uninstaller
echo ============================================================
echo.
echo This will remove:
echo   - Python virtual environment (venv/ or ../venv/)
echo   - Node modules (frontend/node_modules/)
echo   - Compiled frontend (backend/static/, frontend/dist/)
echo   - Build artifacts (dist/, build/, rawhorse.spec)
echo   - Environment config (.env)
echo   - Cache and logs (data/scripts/.cache/, __pycache__/, logs/, *.log)
echo   - Enrichment outputs (enriched_flows_*.csv, test_*.csv, *.backup)
echo.

if "%FORCE%"=="0" (
    set /p CONFIRM="Continue with uninstall? (y/n): "
    if /i not "!CONFIRM!"=="y" (
        echo Cancelled.
        pause
        exit /b 0
    )
) else (
    echo Running in force mode (no prompts).
)

REM Check if port 8000 is in use (server running)
netstat -ano 2>nul | findstr ":8000.*LISTENING" >nul 2>&1
if !errorlevel! equ 0 (
    echo.
    echo WARNING: A process is listening on port 8000 (Project RawHorse may be running).
    if "%FORCE%"=="0" (
        set /p KILL="Stop the server first? (y/n): "
        if /i "!KILL!"=="y" (
            for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING"') do taskkill /F /PID %%a 2>nul
        )
    )
    echo.
)

if "%FORCE%"=="0" (
    set /p KEEPDB="Keep your database (data\prh.db) for future use? (y/n): "
) else (
    set "KEEPDB=n"
)

echo.
echo Removing artifacts...
echo.

REM Track summary: R=removed, K=kept, N=not found
set "SUM_VENV=N"
set "SUM_NM=N"
set "SUM_DIST=N"
set "SUM_BUILD=N"
set "SUM_STATIC=N"
set "SUM_FDIST=N"
set "SUM_SPEC=N"
set "SUM_ENV=N"
set "SUM_DB=N"
set "SUM_CACHE=N"
set "SUM_PYC=N"
set "SUM_LOGS=N"
set "SUM_CSV=N"
set "SUM_BACKUP=N"

REM 1. venv/ or ../venv/
if exist "%SCRIPT_DIR%\venv\Scripts\activate.bat" (
    echo Removing virtual environment (venv/)...
    rmdir /s /q "%SCRIPT_DIR%\venv" 2>nul
    if exist "%SCRIPT_DIR%\venv" rmdir /s /q "%SCRIPT_DIR%\venv"
    set "SUM_VENV=R"
) else if exist "%SCRIPT_DIR%\..\venv\Scripts\activate.bat" (
    echo Removing virtual environment (../venv/)...
    rmdir /s /q "%SCRIPT_DIR%\..\venv" 2>nul
    if exist "%SCRIPT_DIR%\..\venv" rmdir /s /q "%SCRIPT_DIR%\..\venv"
    set "SUM_VENV=R"
) else (
    set "SUM_VENV=N"
)

REM 2. frontend/node_modules (with long-path fallback)
if exist "%SCRIPT_DIR%\frontend\node_modules" (
    echo Removing node_modules...
    rmdir /s /q "%SCRIPT_DIR%\frontend\node_modules" 2>nul
    if exist "%SCRIPT_DIR%\frontend\node_modules" (
        echo Long path detected, using robocopy workaround...
        mkdir "%TEMP%\prh_empty" 2>nul
        robocopy "%TEMP%\prh_empty" "%SCRIPT_DIR%\frontend\node_modules" /MIR /NFL /NDL /NJH /NJS >nul 2>&1
        rmdir /s /q "%SCRIPT_DIR%\frontend\node_modules" 2>nul
        rmdir "%TEMP%\prh_empty" 2>nul
    )
    set "SUM_NM=R"
)

REM 3. dist/, build/
if exist "%SCRIPT_DIR%\dist" (
    echo Removing dist/...
    rmdir /s /q "%SCRIPT_DIR%\dist" 2>nul
    set "SUM_DIST=R"
)
if exist "%SCRIPT_DIR%\build" (
    echo Removing build/...
    rmdir /s /q "%SCRIPT_DIR%\build" 2>nul
    set "SUM_BUILD=R"
)

REM 4. backend/static/, frontend/dist/
if exist "%SCRIPT_DIR%\backend\static" (
    echo Removing backend/static/...
    rmdir /s /q "%SCRIPT_DIR%\backend\static" 2>nul
    set "SUM_STATIC=R"
)
if exist "%SCRIPT_DIR%\frontend\dist" (
    echo Removing frontend/dist/...
    rmdir /s /q "%SCRIPT_DIR%\frontend\dist" 2>nul
    set "SUM_FDIST=R"
)

REM 5. rawhorse.spec
if exist "%SCRIPT_DIR%\rawhorse.spec" (
    del /q "%SCRIPT_DIR%\rawhorse.spec" 2>nul
    set "SUM_SPEC=R"
)

REM 6. .env
if exist "%SCRIPT_DIR%\.env" (
    echo Removing .env...
    del /q "%SCRIPT_DIR%\.env" 2>nul
    set "SUM_ENV=R"
)

REM 7. data/prh.db (if user chose to delete)
if /i not "!KEEPDB!"=="y" (
    if exist "%SCRIPT_DIR%\data\prh.db" (
        echo Removing database...
        del /q "%SCRIPT_DIR%\data\prh.db" 2>nul
        set "SUM_DB=R"
    ) else (
        set "SUM_DB=N"
    )
) else (
    if exist "%SCRIPT_DIR%\data\prh.db" (set "SUM_DB=K") else (set "SUM_DB=N")
)

REM 8. data/scripts/.cache/
if exist "%SCRIPT_DIR%\data\scripts\.cache" (
    echo Removing data/scripts/.cache/...
    rmdir /s /q "%SCRIPT_DIR%\data\scripts\.cache" 2>nul
    set "SUM_CACHE=R"
)

REM 9. __pycache__ in backend
set "SUM_PYC=N"
for /d /r "%SCRIPT_DIR%\backend" %%d in (__pycache__) do (
    rmdir /s /q "%%d" 2>nul
    set "SUM_PYC=R"
)

REM 10. logs/ and *.log in project root
if exist "%SCRIPT_DIR%\logs" (
    rmdir /s /q "%SCRIPT_DIR%\logs" 2>nul
    set "SUM_LOGS=R"
)
del "%SCRIPT_DIR%\*.log" 2>nul
if exist "%SCRIPT_DIR%\*.log" set "SUM_LOGS=R"
if "%SUM_LOGS%"=="N" set "SUM_LOGS=N"

REM 11. data/financial enriched_flows_*.csv, test_*.csv
if exist "%SCRIPT_DIR%\data\financial" (
    del "%SCRIPT_DIR%\data\financial\enriched_flows_*.csv" 2>nul
    del "%SCRIPT_DIR%\data\financial\test_*.csv" 2>nul
    set "SUM_CSV=R"
) else (
    set "SUM_CSV=N"
)

REM 12. *.backup, *_backup.py, *_backup*.csv (project root and data)
set "SUM_BACKUP=N"
del "%SCRIPT_DIR%\*.backup" 2>nul
del "%SCRIPT_DIR%\*_backup.py" 2>nul
del "%SCRIPT_DIR%\*_backup*.csv" 2>nul
if exist "%SCRIPT_DIR%\data" for /r "%SCRIPT_DIR%\data" %%f in (*.backup *_backup*.csv) do (del "%%f" 2>nul & set "SUM_BACKUP=R")
if exist "%SCRIPT_DIR%\*.backup" set "SUM_BACKUP=R"
if exist "%SCRIPT_DIR%\*_backup.py" set "SUM_BACKUP=R"

echo.
echo ============================================================
echo   Removal summary
echo ============================================================
echo   venv/ or ../venv/     : !SUM_VENV!
echo   frontend/node_modules : !SUM_NM!
echo   dist/                 : !SUM_DIST!
echo   build/                : !SUM_BUILD!
echo   backend/static/       : !SUM_STATIC!
echo   frontend/dist/        : !SUM_FDIST!
echo   rawhorse.spec         : !SUM_SPEC!
echo   .env                  : !SUM_ENV!
echo   data/prh.db           : !SUM_DB!
echo   data/scripts/.cache/  : !SUM_CACHE!
echo   __pycache__/          : !SUM_PYC!
echo   logs, *.log           : !SUM_LOGS!
echo   enrichment outputs    : !SUM_CSV!
echo   backups               : !SUM_BACKUP!
echo   R=removed  K=kept  N=not found
echo ============================================================
echo.
echo Uninstall complete. To finish, delete this project folder:
echo   %SCRIPT_DIR%
echo.
pause
