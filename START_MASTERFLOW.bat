@echo off
title MasterFlow - Music Mastering Platform
echo.
echo  ╔═══════════════════════════════════════════╗
echo  ║   MasterFlow - AI Music Mastering         ║
echo  ╚═══════════════════════════════════════════╝
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Download it from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during install.
    pause
    exit
)

:: Install dependencies if needed
if not exist ".deps_installed" (
    echo Installing dependencies... This may take a minute.
    pip install -r requirements.txt
    pip install email-validator
    echo. > .deps_installed
)

echo.
echo Starting MasterFlow...
echo.
echo Open your browser to: http://localhost:8000/app
echo.
echo Press Ctrl+C to stop the server.
echo.

:: Start the server
python run.py

pause
