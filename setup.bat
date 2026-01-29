@echo off
REM Agent700 API CLI Setup Script for Windows
REM This script sets up a Python virtual environment and installs dependencies

echo 🚀 Setting up Agent700 API CLI environment...

REM Check if Python 3 is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python 3 is not installed or not in PATH
    echo Please install Python 3 and try again
    pause
    exit /b 1
)

REM Check if virtual environment already exists
if exist "venv" (
    echo ⚠️  Virtual environment already exists
    set /p recreate="Do you want to recreate it? (y/N): "
    if /i "%recreate%"=="y" (
        echo 🗑️  Removing existing virtual environment...
        rmdir /s /q venv
    ) else (
        echo ✅ Using existing virtual environment
    )
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  No .env file found
    if exist ".env.example" (
        echo 📋 Copying .env.example to .env...
        copy .env.example .env
        echo ✅ Created .env file from template
        echo 📝 Please edit .env with your actual credentials
    ) else (
        echo ❌ No .env.example file found
        pause
        exit /b 1
    )
) else (
    echo ✅ .env file already exists
)

echo.
echo 🎉 Setup complete!
echo.
echo To use the Agent700 CLI:
echo 1. Activate the virtual environment: venv\Scripts\activate.bat
echo 2. Edit .env with your credentials
echo 3. Run: a700cli "Your message here"
echo.
echo To deactivate the virtual environment: deactivate
pause
