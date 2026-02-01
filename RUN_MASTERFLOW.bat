@echo off
title MasterFlow - Music Mastering Platform
echo.
echo  ========================================
echo    MasterFlow - AI Music Mastering
echo  ========================================
echo.

:: Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found!
    echo Please run SETUP.bat first.
    pause
    exit /b 1
)

:: Activate virtual environment
call venv\Scripts\activate.bat

echo Starting MasterFlow...
echo.
echo  Open your browser to: http://localhost:8000/app
echo.
echo  Press Ctrl+C to stop the server.
echo.

:: Start the server
python run.py

pause
