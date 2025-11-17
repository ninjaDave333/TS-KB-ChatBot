# TSKB RAGAS Evaluation Runner
# Activates virtual environment and runs RAGAS evaluation

Write-Host "=== TSKB RAGAS Evaluation ===" -ForegroundColor Green

# Check if venv exists
if (-not (Test-Path "venv\Scripts\activate.ps1")) {
    Write-Host "Virtual environment not found. Please create it first:" -ForegroundColor Red
    Write-Host "python -m venv venv" -ForegroundColor Yellow
    Write-Host "venv\Scripts\activate" -ForegroundColor Yellow
    Write-Host "pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Blue
& "venv\Scripts\activate.ps1"

# Check if server is running
Write-Host "Checking if TSKB server is running..." -ForegroundColor Blue
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    Write-Host "✓ Server is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Server not running. Please start it first:" -ForegroundColor Red
    Write-Host "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Yellow
    exit 1
}

# Run RAGAS evaluation
Write-Host "Running RAGAS evaluation..." -ForegroundColor Blue
python Tests\ragas_evaluation.py

Write-Host "RAGAS evaluation completed!" -ForegroundColor Green