@echo off
echo Starting Geopark Tuban Management System (Optimized Version)...
echo.

REM Set production environment variables
set FLASK_ENV=production
set FLASK_DEBUG=0

echo [1] Stopping any existing Python processes...
taskkill /F /IM python.exe 2>nul

echo [2] Waiting for port release...
timeout /t 2 /nobreak > nul

echo [3] Starting optimized service...
cd /d "%~dp0"
start "Geopark Tuban Service (Optimized)" python app_prod.py

echo.
echo ========================================
echo [SUCCESS] Optimized service started!
echo URL: http://127.0.0.1:5000
echo Features:
echo   - Debug mode: OFF
echo   - Auto-reload: OFF
echo   - Threading: ON
echo ========================================
echo.
pause