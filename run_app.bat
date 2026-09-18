@echo off
setlocal enabledelayedexpansion
title AI-Based Software Requirement Analyzer Server

:: 1. Force working directory to the project folder where this script resides
cd /d "%~dp0"

echo ===============================================================================
echo            AI-BASED SOFTWARE REQUIREMENT ANALYZER — SERVER LAUNCHER
echo ===============================================================================
echo.

:: 2. Detect Python executable
set "PYTHON_EXE="
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
    echo [OK] Using virtual environment: .venv
) else if exist "%~dp0venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0venv\Scripts\python.exe"
    echo [OK] Using virtual environment: venv
) else (
    where python >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=python"
        echo [OK] Using system Python
    ) else (
        where py >nul 2>&1
        if !errorlevel! equ 0 (
            set "PYTHON_EXE=py -3"
            echo [OK] Using Python Launcher (py)
        ) else (
            echo [ERROR] Python was not found on your system PATH!
            echo Please install Python 3.10+ from https://www.python.org/
            echo and ensure 'Add Python to PATH' is checked during installation.
            echo.
            pause
            exit /b 1
        )
    )
)

:: 3. Check port 8000 availability
netstat -ano | findstr :8000 >nul 2>&1
if !errorlevel! equ 0 (
    echo [NOTE] Port 8000 is already active or in use.
    echo If the analyzer server is already running, you can directly visit:
    echo        http://127.0.0.1:8000
    echo.
)

:: 4. Verify trained models exist (auto-train if missing)
if not exist "%~dp0models\classifier.pkl" (
    echo [INFO] Model files not found. Running initial training pipeline...
    !PYTHON_EXE! "%~dp0train_model.py"
    if !errorlevel! neq 0 (
        echo [WARNING] Model training encountered an issue. Starting server anyway...
    )
)

echo.
echo ===============================================================================
echo  Application is starting!
echo  Access URLs:
echo    * Web Interface:  http://127.0.0.1:8000
echo    * Swagger API:    http://127.0.0.1:8000/docs
echo    * ReDoc Docs:     http://127.0.0.1:8000/redoc
echo ===============================================================================
echo.
echo Press CTRL+C to stop the server at any time.
echo.

:: 5. Launch default browser after 2 seconds in a background helper
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:8000"

:: 6. Launch Uvicorn ASGI Server
!PYTHON_EXE! -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload

if !errorlevel! neq 0 (
    echo.
    echo [ERROR] Server terminated with error code !errorlevel!.
    echo Make sure dependencies are installed:
    echo   pip install -r requirements.txt
    echo   python -m spacy download en_core_web_sm
    echo.
    pause
)
