# Test fixed AI queries with correct relationships

Write-Host "Testing FIXED AI-generated queries..."

# Test 1: Correct relationship direction
Write-Host "`n1. Which employees manage clients? (FIXED)"
$body1 = @{
    query = "Which employees manage clients?"
    use_ai = $true
} | ConvertTo-Json

$response1 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body1 -ContentType "application/json"
Write-Host "Cypher: $($response1.cypher_query)"
Write-Host "Answer: $($response1.answer)"

# Test 2: Use OPPORTUNITY for purchased products
Write-Host "`n2. What products did Wix purchase? (FIXED)"
$body2 = @{
    query = "What products did Wix purchase?"
    use_ai = $true
} | ConvertTo-Json

$response2 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body2 -ContentType "application/json"
Write-Host "Cypher: $($response2.cypher_query)"
Write-Host "Answer: $($response2.answer)"

# Test 3: Correct region name (IL not Israel)
Write-Host "`n3. Which clients are managed by employees in Israel? (FIXED)"
$body3 = @{
    query = "Which clients are managed by employees in Israel?"
    use_ai = $true
} | ConvertTo-Json

$response3 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body3 -ContentType "application/json"
Write-Host "Cypher: $($response3.cypher_query)"
Write-Host "Answer: $($response3.answer)"

# Test 4: Vendor relationship
Write-Host "`n4. How many HashiCorp products are there? (FIXED)"
$body4 = @{
    query = "How many HashiCorp products are there?"
    use_ai = $true
} | ConvertTo-Json

$response4 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body4 -ContentType "application/json"
Write-Host "Cypher: $($response4.cypher_query)"
Write-Host "Answer: $($response4.answer)"