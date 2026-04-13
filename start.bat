: <<'BATCH'
@echo off
setlocal
echo =========================================
echo    🚀 Raj Leads Generator (Windows)
echo =========================================

REM 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

REM 2. Install Dependencies
echo.
echo [1/3] Installing/Updating dependencies...
python -m pip install --upgrade pip
python -m pip install fastapi uvicorn playwright pandas openpyxl fake-useragent

REM 3. Setup Playwright
echo.
echo [2/3] Setting up Playwright...
python -m playwright install chromium

REM 4. Start Unified Server
echo.
echo [3/3] Starting Unified Server (Port 8000)...
echo.
echo ==============================================================
echo    ✅ Application is starting! 
echo    👉 URL: http://localhost:8000/
echo.
echo    Keep this window open. Press Ctrl+C or close to stop.
echo ==============================================================
echo.

REM Automatically open the application in the default browser
start http://localhost:8000/

REM Start the server
python backend/python/api_main.py

endlocal
exit /b
BATCH
#!/bin/bash
# Unified Start Script (Linux/macOS)

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}   🚀 Raj Leads Generator (Linux)       ${NC}"
echo -e "${BLUE}=========================================${NC}"

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 is not installed!${NC}"
    exit 1
fi

# 2. Install Dependencies
echo -e "${BLUE}[1/3] Installing/Updating Python dependencies...${NC}"
python3 -m pip install --upgrade pip
python3 -m pip install fastapi uvicorn playwright pandas openpyxl fake-useragent

# 3. Setup Playwright
echo -e "${BLUE}[2/3] Setting up Playwright...${NC}"
python3 -m playwright install chromium

# 4. Start Unified Server
echo -e "${BLUE}[3/3] Starting Unified Server (Port 8000)...${NC}"
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}   ✅ Application is READY!              ${NC}"
echo -e "${GREEN}   👉 URL: http://localhost:8000/        ${NC}"
echo -e "${GREEN}=========================================${NC}"

# Automatically open browser if xdg-open is available
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8000/ &
fi

# Start the server
python3 backend/python/api_main.py
