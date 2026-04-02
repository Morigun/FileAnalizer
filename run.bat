@echo off
REM File Analyzer - Setup and Run Script
REM This script creates a virtual environment, installs dependencies, and runs the application

setlocal enabledelayedexpansion

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Virtual environment directory
set "VENV_DIR=%SCRIPT_DIR%venv"

echo ========================================
echo File Analyzer - Setup and Run
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "%VENV_DIR%" (
    echo Creating virtual environment...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Install/upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install requirements
echo Checking requirements...
if exist "%SCRIPT_DIR%requirements.txt" (
    pip install -r "%SCRIPT_DIR%requirements.txt" --quiet
    echo Requirements installed.
) else (
    echo No requirements.txt found, skipping dependency installation.
)

echo.
echo Starting File Analyzer...
echo ========================================
echo.

REM Run the application
python "%SCRIPT_DIR%main.py"

REM Deactivate when done
deactivate

echo.
echo Application closed.
pause
