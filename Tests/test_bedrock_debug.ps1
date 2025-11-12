# Debug Bedrock connection

Write-Host "Testing Bedrock connection..."

# Simple AI query to see error details
$body = @{
    query = "How many clients are there?"
    use_ai = $true
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body -ContentType "application/json"
    Write-Host "Method: $($response.method)"
    Write-Host "Error: $($response.error)"
    Write-Host "Cypher: $($response.cypher_query)"
    Write-Host "Answer: $($response.answer)"
} catch {
    Write-Host "Request failed: $($_.Exception.Message)"
}

# Test AWS credentials
Write-Host "`nTesting AWS credentials..."
try {
    aws sts get-caller-identity
} catch {
    Write-Host "AWS CLI not configured or no credentials"
}