# Test clean Cypher generation

Write-Host "Testing CLEAN Cypher generation..."

# Test 1: Simple relationship
Write-Host "`n1. Which employees manage clients?"
$body1 = @{
    query = "Which employees manage clients?"
    use_ai = $true
} | ConvertTo-Json

try {
    $response1 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body1 -ContentType "application/json"
    Write-Host "Cypher: $($response1.cypher_query)"
    Write-Host "Answer: $($response1.answer)"
} catch {
    Write-Host "Error: $($_.Exception.Message)"
}

# Test 2: Wix opportunities (purchased products)
Write-Host "`n2. What products did Wix purchase?"
$body2 = @{
    query = "What products did Wix purchase?"
    use_ai = $true
} | ConvertTo-Json

try {
    $response2 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body2 -ContentType "application/json"
    Write-Host "Cypher: $($response2.cypher_query)"
    Write-Host "Answer: $($response2.answer)"
} catch {
    Write-Host "Error: $($_.Exception.Message)"
}

# Test 3: Simple count
Write-Host "`n3. How many employees are there?"
$body3 = @{
    query = "How many employees are there?"
    use_ai = $true
} | ConvertTo-Json

try {
    $response3 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body3 -ContentType "application/json"
    Write-Host "Cypher: $($response3.cypher_query)"
    Write-Host "Answer: $($response3.answer)"
} catch {
    Write-Host "Error: $($_.Exception.Message)"
}