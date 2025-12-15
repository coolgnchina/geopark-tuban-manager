@echo off
echo ========================================
echo Geopark Tuban Management System - Service Restart
echo ========================================
echo.

REM Stop Python processes
echo [1] Stopping Python processes...
taskkill /F /IM python.exe 2>nul
echo    Python processes stopped.
echo.

REM Wait for port release
echo [2] Waiting for port 5000 to be released...
timeout /t 2 /nobreak > nul

REM Check if port is still in use
netstat -ano | findstr ":5000" > nul
if %errorlevel% equ 0 (
    echo    Port 5000 still in use, waiting...
    timeout /t 2 /nobreak > nul
) else (
    echo    Port 5000 is free.
)
echo.

REM Start new service
echo [3] Starting new service instance...
cd /d "%~dp0"
start "Geopark Tuban Service" python app.py
echo    Service start command sent.
echo.

REM Wait for service to start
echo [4] Waiting for service to start...
timeout /t 3 /nobreak > nul

REM Check service status
echo [5] Checking service status...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://127.0.0.1:5000/login' -TimeoutSec 5; if ($response.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }"

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo [SUCCESS] Service restarted successfully!
    echo System URL: http://127.0.0.1:5000
    echo Default Username: admin
    echo Default Password: admin123
    echo ========================================
) else (
    echo.
    echo ========================================
    echo [WARNING] Service may not be fully ready.
    echo Please wait a moment and try accessing:
    echo http://127.0.0.1:5000
    echo ========================================
)

echo.
echo Press any key to exit...
pause > nul