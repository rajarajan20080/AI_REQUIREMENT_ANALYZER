# PowerShell Startup Script for AI-Based Software Requirement Analyzer
$ErrorActionPreference = "Continue"

# 1. Set working directory to project folder
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path $ProjectRoot

Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "          AI-BASED SOFTWARE REQUIREMENT ANALYZER — SERVER LAUNCHER            " -ForegroundColor Cyan
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host ""

# 2. Detect Python
$PythonExe = "python"
if (Test-Path "$ProjectRoot\.venv\Scripts\python.exe") {
    $PythonExe = "$ProjectRoot\.venv\Scripts\python.exe"
    Write-Host "[OK] Using virtual environment: .venv" -ForegroundColor Green
} elseif (Test-Path "$ProjectRoot\venv\Scripts\python.exe") {
    $PythonExe = "$ProjectRoot\venv\Scripts\python.exe"
    Write-Host "[OK] Using virtual environment: venv" -ForegroundColor Green
} else {
    Write-Host "[OK] Using system Python" -ForegroundColor Green
}

# 3. Check trained model
if (-not (Test-Path "$ProjectRoot\models\classifier.pkl")) {
    Write-Host "[INFO] Training models..." -ForegroundColor Yellow
    & $PythonExe "$ProjectRoot\train_model.py"
}

Write-Host ""
Write-Host "Application is starting!" -ForegroundColor Green
Write-Host "  * Web Interface: http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  * API Docs:      http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press CTRL+C to stop the server at any time." -ForegroundColor Gray
Write-Host ""

# 4. Open browser in background job
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 2
    Start-Process "http://127.0.0.1:8000"
} | Out-Null

# 5. Run uvicorn
& $PythonExe -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
