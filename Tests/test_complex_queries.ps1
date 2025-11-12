# Test complex AI queries

Write-Host "Testing complex AI-generated queries..."

# Test 1: Relationship query
Write-Host "`n1. Which employees manage clients?"
$body1 = @{
    query = "Which employees manage clients?"
    use_ai = $true
} | ConvertTo-Json

$response1 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body1 -ContentType "application/json"
Write-Host "Cypher: $($response1.cypher_query)"
Write-Host "Answer: $($response1.answer)"

# Test 2: Specific client query
Write-Host "`n2. What products does Wix have?"
$body2 = @{
    query = "What products does Wix have?"
    use_ai = $true
} | ConvertTo-Json

$response2 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body2 -ContentType "application/json"
Write-Host "Cypher: $($response2.cypher_query)"
Write-Host "Answer: $($response2.answer)"

# Test 3: Complex relationship
Write-Host "`n3. Which clients are managed by employees in Israel?"
$body3 = @{
    query = "Which clients are managed by employees in Israel?"
    use_ai = $true
} | ConvertTo-Json

$response3 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body3 -ContentType "application/json"
Write-Host "Cypher: $($response3.cypher_query)"
Write-Host "Answer: $($response3.answer)"

# Test 4: Product vendor query
Write-Host "`n4. How many HashiCorp products are there?"
$body4 = @{
    query = "How many HashiCorp products are there?"
    use_ai = $true
} | ConvertTo-Json

$response4 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body4 -ContentType "application/json"
Write-Host "Cypher: $($response4.cypher_query)"
Write-Host "Answer: $($response4.answer)"