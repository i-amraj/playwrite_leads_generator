@echo off
echo =========================================
echo    🚀 Raj Leads Generator Starter (Windows)
echo =========================================

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

echo.
echo Starting Lead Generator Backend (FastAPI)...
start "Backend" cmd /c "python backend/python/api_main.py"

echo.
echo Starting Frontend Server on port 8005...
echo App will be available at: http://localhost:8005/
echo.
echo ==============================================================
echo Keep this window open. Press Ctrl+C or close to stop the app.
echo ==============================================================
echo.

python -m http.server 8005
