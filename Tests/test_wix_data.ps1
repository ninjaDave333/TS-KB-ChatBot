# Check what data exists for Wix

Write-Host "Checking Wix data in database..."

# Test 1: Does Wix exist?
Write-Host "`n1. Does Wix client exist?"
$body1 = @{
    query = "MATCH (c:Client) WHERE c.name CONTAINS 'Wix' RETURN c.name"
    use_ai = $false
} | ConvertTo-Json

$response1 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body1 -ContentType "application/json"
Write-Host "Cypher: $($response1.cypher_query)"
Write-Host "Data: $($response1.data | ConvertTo-Json)"

# Test 2: Check OPPORTUNITY relationships
Write-Host "`n2. Any OPPORTUNITY relationships?"
$body2 = @{
    query = "MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product) RETURN count(o) as total_opportunities LIMIT 5"
    use_ai = $false
} | ConvertTo-Json

$response2 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body2 -ContentType "application/json"
Write-Host "Cypher: $($response2.cypher_query)"
Write-Host "Data: $($response2.data | ConvertTo-Json)"

# Test 3: Check HAS_INSTALLED relationships
Write-Host "`n3. Any HAS_INSTALLED relationships?"
$body3 = @{
    query = "MATCH (c:Client)-[h:HAS_INSTALLED]->(p:Product) RETURN count(h) as total_installed LIMIT 5"
    use_ai = $false
} | ConvertTo-Json

$response3 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body3 -ContentType "application/json"
Write-Host "Cypher: $($response3.cypher_query)"
Write-Host "Data: $($response3.data | ConvertTo-Json)"