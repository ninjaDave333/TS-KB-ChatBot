# TSKB RAGAS Evaluation with Ollama Runner
param(
    [string]$OllamaHost = "172.16.10.250",
    [string]$OllamaModel = "llama3.1"
)

Write-Host "=== TSKB RAGAS Evaluation (Ollama) ===" -ForegroundColor Green
Write-Host "Ollama Host: $OllamaHost" -ForegroundColor Cyan
Write-Host "Model: $OllamaModel" -ForegroundColor Cyan

# Check venv
if (-not (Test-Path "venv\Scripts\activate.ps1")) {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    & "venv\Scripts\activate.ps1"
    pip install -r requirements.txt
} else {
    Write-Host "Activating virtual environment..." -ForegroundColor Blue
    & "venv\Scripts\activate.ps1"
}

# Test TSKB API
Write-Host "Testing TSKB API..." -ForegroundColor Blue
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    Write-Host "✓ TSKB API connected" -ForegroundColor Green
} catch {
    Write-Host "✗ TSKB API not running. Start with:" -ForegroundColor Red
    Write-Host "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Yellow
    exit 1
}

# Run evaluation
Write-Host "Starting RAGAS evaluation with Ollama..." -ForegroundColor Blue
Write-Host "This will take several minutes with local LLM processing..." -ForegroundColor Yellow

$env:OLLAMA_HOST = $OllamaHost
$env:OLLAMA_MODEL = $OllamaModel

python Tests\ragas_evaluation_ollama.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ RAGAS evaluation completed successfully!" -ForegroundColor Green
    Write-Host "Check Tests\ folder for results files" -ForegroundColor Cyan
} else {
    Write-Host "✗ Evaluation failed" -ForegroundColor Red
}