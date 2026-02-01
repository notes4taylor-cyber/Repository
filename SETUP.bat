@echo off
title MasterFlow Setup
echo.
echo  ========================================
echo    MasterFlow - Setup Script
echo  ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Download it from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

echo [1/3] Creating virtual environment...
python -m venv venv

echo [2/3] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/3] Installing dependencies...
pip install --upgrade pip
pip install fastapi==0.115.0 uvicorn[standard] python-multipart jinja2
pip install numpy scipy pydub soundfile
pip install greenlet sqlalchemy==2.0.36 aiosqlite
pip install python-jose[cryptography] passlib[bcrypt]
pip install python-dotenv aiofiles
pip install pydantic-settings email-validator

echo.
echo  ========================================
echo    Setup Complete!
echo  ========================================
echo.
echo  To start MasterFlow, double-click:
echo    RUN_MASTERFLOW.bat
echo.
pause
