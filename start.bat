@echo off
chcp 65001 > nul
title Campus IBN NMS
echo.
echo ========================================
echo    Campus IBN NMS - Starting...
echo ========================================
echo.

:: Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found.
    echo Please run setup.bat first.
    pause
    exit /b 1
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Run the application
echo [INFO] Starting Campus IBN NMS...
echo [INFO] Web Interface: http://localhost:5000
echo [INFO] Metrics: http://localhost:8000
echo [INFO] Press Ctrl+C to stop the application
echo.
python main.py

pause