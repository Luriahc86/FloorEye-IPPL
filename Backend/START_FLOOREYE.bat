@echo off
REM FloorEye Startup Script - Windows
REM This script starts both Backend and Frontend servers

echo.
echo ============================================================
echo   FloorEye Monitoring System - Startup Script
echo ============================================================
echo.

REM Check if running from correct directory
if not exist "Backend" (
    echo ERROR: Backend folder not found!
    echo This script must be run from D:\IPPL\FloorEye directory
    echo.
    pause
    exit /b 1
)

if not exist "Frontend" (
    echo ERROR: Frontend folder not found!
    echo This script must be run from D:\IPPL\FloorEye directory
    echo.
    pause
    exit /b 1
)

echo [1/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)
echo OK - Python found

echo.
echo [2/4] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found!
    echo Please install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
)
echo OK - Node.js found

echo.
echo [3/4] Starting Backend (FastAPI + Monitor Thread)...
echo.
cd Backend
start "FloorEye Backend" cmd /k python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
timeout /t 3

echo.
echo [4/4] Starting Frontend (React/Vue + Vite)...
echo.
cd ..\Frontend
start "FloorEye Frontend" cmd /k npm run dev

echo.
echo ============================================================
echo   Startup Complete!
echo ============================================================
echo.
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://127.0.0.1:5173
echo.
echo Monitor thread is running. Check Backend terminal for logs.
echo.
echo Next steps:
echo   1. Open http://127.0.0.1:5173 in your browser
echo   2. Click "Kelola Kamera" to add a camera
echo   3. Click "Notifikasi Email" to add email recipient
echo   4. Wait for monitor to detect dirty floor
echo   5. Check your Gmail inbox for notification email
echo.
echo For detailed help, see:
echo   - README_COMPLETE.md
echo   - EMAIL_NOTIFICATION_GUIDE.md
echo   - QUICK_CHECKLIST.md
echo.
pause
