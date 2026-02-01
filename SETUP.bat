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
pip install fastapi==0.109.0 uvicorn[standard]==0.27.0 python-multipart==0.0.6 jinja2==3.1.3
pip install numpy==1.26.3 scipy==1.12.0 pydub==0.25.1 soundfile==0.12.1
pip install sqlalchemy==2.0.25 aiosqlite==0.19.0
pip install python-jose[cryptography]==3.3.0 passlib[bcrypt]==1.7.4
pip install python-dotenv==1.0.0 aiofiles==23.2.1
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
