@echo off
chcp 65001 > nul
title Campus IBN NMS - Setup
echo.
echo ========================================
echo    Campus IBN NMS - Setup
echo ========================================
echo.

echo [1/5] Creating virtual environment...
python -m venv venv

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo [4/5] Creating directories...
if not exist logs mkdir logs
if not exist data mkdir data
if not exist configs mkdir configs
if not exist src\web_ui\templates mkdir src\web_ui\templates

echo [5/5] Creating default configuration...
echo # Campus IBN NMS Configuration > configs\default.yaml
echo netconf_devices: >> configs\default.yaml
echo   - host: "localhost" >> configs\default.yaml
echo     port: 830 >> configs\default.yaml
echo     username: "admin" >> configs\default.yaml
echo     password: "admin" >> configs\default.yaml
echo     device_type: "default" >> configs\default.yaml

echo.
echo ========================================
echo    SETUP COMPLETED SUCCESSFULLY!
echo ========================================
echo.
echo To start the application:
echo   .\start.bat
echo.
echo Access points:
echo   Web Interface: http://localhost:5000
echo   Metrics:       http://localhost:8000
echo.
pause