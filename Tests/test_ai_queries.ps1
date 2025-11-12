# Test AI-powered queries

Write-Host "Testing AI-powered queries..."

# Test 1: Complex relationship query
Write-Host "`n1. Testing: Which employees manage clients?"
$body1 = @{
    query = "Which employees manage clients?"
    use_ai = $true
} | ConvertTo-Json

$response1 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body1 -ContentType "application/json"
Write-Host "Method: $($response1.method)"
Write-Host "Cypher: $($response1.cypher_query)"
Write-Host "Answer: $($response1.answer)"

# Test 2: Product query
Write-Host "`n2. Testing: What products does Wix have?"
$body2 = @{
    query = "What products does Wix have?"
    use_ai = $true
} | ConvertTo-Json

$response2 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body2 -ContentType "application/json"
Write-Host "Method: $($response2.method)"
Write-Host "Cypher: $($response2.cypher_query)"
Write-Host "Answer: $($response2.answer)"

# Test 3: Compare AI vs Basic
Write-Host "`n3. Testing same query with basic method:"
$body3 = @{
    query = "How many employees are there?"
    use_ai = $false
} | ConvertTo-Json

$response3 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body3 -ContentType "application/json"
Write-Host "Method: $($response3.method)"
Write-Host "Cypher: $($response3.cypher_query)"
Write-Host "Answer: $($response3.answer)"