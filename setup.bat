@echo off
REM Border Threat Detection System - Windows Setup Script
REM Run this script to set up everything automatically

echo ====================================================================
echo   Border Threat Detection System - Automated Setup
echo ====================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Python found
python --version

REM Create virtual environment
echo.
echo [2/5] Creating virtual environment...
if not exist venv (
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
echo.
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo [4/5] Installing dependencies...
echo This may take a few minutes...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

REM Download YOLO model
echo.
echo [5/5] Downloading YOLO model...
python models\training\download_model.py

if %errorlevel% neq 0 (
    echo [WARNING] Model download failed, but will auto-download on first run
)

REM Create necessary directories
if not exist logs mkdir logs
if not exist uploads mkdir uploads
if not exist snapshots mkdir snapshots

echo.
echo ====================================================================
echo   Setup Complete!
echo ====================================================================
echo.
echo To run the application:
echo   1. Activate virtual environment: venv\Scripts\activate.bat
echo   2. Run the server: python run.py
echo   3. Open browser: http://localhost:5000
echo.
echo Or simply run: start.bat
echo.
pause
