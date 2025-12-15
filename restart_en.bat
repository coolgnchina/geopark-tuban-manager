@echo off
echo Restarting Geopark Tuban Management System...
echo.

REM Stop Python processes
echo Stopping Python processes...
taskkill /F /IM python.exe 2>nul

REM Wait 2 seconds
timeout /t 2 /nobreak > nul

REM Start new service
echo Starting service...
start python app.py

echo.
echo Service started!
echo Visit: http://127.0.0.1:5000
echo.
pause