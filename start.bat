@echo off
REM Quick start script for Border Threat Detection System

echo Starting Border Threat Detection System...
echo.

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Run the application
python run.py

pause
