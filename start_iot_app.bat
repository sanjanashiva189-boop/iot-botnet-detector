@echo off
title IoT Botnet Detection System
color 0A
echo ========================================
echo    IoT BOTNET DETECTION SYSTEM
echo ========================================
echo.
echo Starting server...
echo.

cd /d D:\BOTNET_DETECTION_IOT

echo Activating virtual environment...
call venv\Scripts\activate

echo Starting Flask server...
echo.
echo ========================================
echo    Server is running!
echo    Open browser: http://localhost:5000
echo    Press Ctrl+C to stop the server
echo ========================================
echo.

start http://localhost:5000

python app.py

pause