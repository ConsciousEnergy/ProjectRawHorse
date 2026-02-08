@echo off
REM Build frontend and deploy to backend/static so the running app serves the latest UI.
REM Run this from the project root (folder that contains frontend and backend).

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo Building frontend...
cd frontend
call npm run build
if errorlevel 1 (
  echo Build failed.
  exit /b 1
)
cd ..

echo Deploying to backend/static...
if exist "backend\static" rd /s /q "backend\static"
mkdir "backend\static"
xcopy /E /I /Y frontend\dist\* backend\static\
echo Done. Restart the backend and hard-refresh the browser (Ctrl+Shift+R).
