# PowerShell test commands for Windows

# Test health endpoint
Write-Host "Testing health endpoint..."
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health" -Method GET
$response | ConvertTo-Json

# Test schema endpoint
Write-Host "`nTesting schema endpoint..."
try {
    $schema = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/schema" -Method GET
    $schema | ConvertTo-Json
} catch {
    Write-Host "Schema error: $($_.Exception.Message)"
}

# Test query endpoint
Write-Host "`nTesting query endpoint..."
$body = @{
    query = "How many clients are there?"
} | ConvertTo-Json

try {
    $queryResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body -ContentType "application/json"
    $queryResponse | ConvertTo-Json
} catch {
    Write-Host "Query error: $($_.Exception.Message)"
}