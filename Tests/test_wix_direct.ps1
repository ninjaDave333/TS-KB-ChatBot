# Direct test for WIX using schema knowledge

Write-Host "Testing WIX with schema knowledge..."

# From your schema docs, Client has sf_name field
# Test 1: Find WIX using exact match
Write-Host "`n1. Find WIX (exact):"
$body1 = @{
    query = "MATCH (c:Client {sf_name: 'WIX'}) RETURN c.sf_name"
    use_ai = $false
} | ConvertTo-Json

try {
    $response1 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body1 -ContentType "application/json"
    Write-Host "Exact WIX match:"
    $response1.data | ForEach-Object { Write-Host "  - '$($_.sf_name)'" }
} catch {
    Write-Host "Exact match failed: $($_.Exception.Message)"
}

# Test 2: Find WIX opportunities
Write-Host "`n2. WIX opportunities:"
$body2 = @{
    query = "MATCH (c:Client {sf_name: 'WIX'})-[:OPPORTUNITY]->(p:Product) RETURN p.name LIMIT 5"
    use_ai = $false
} | ConvertTo-Json

try {
    $response2 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body2 -ContentType "application/json"
    Write-Host "WIX products:"
    $response2.data | ForEach-Object { Write-Host "  - '$($_.name)'" }
} catch {
    Write-Host "WIX opportunities failed: $($_.Exception.Message)"
}

# Test 3: Count WIX opportunities
Write-Host "`n3. Count WIX opportunities:"
$body3 = @{
    query = "MATCH (c:Client {sf_name: 'WIX'})-[:OPPORTUNITY]->(p:Product) RETURN count(p) as total"
    use_ai = $false
} | ConvertTo-Json

try {
    $response3 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body3 -ContentType "application/json"
    Write-Host "WIX opportunity count: $($response3.data[0].total)"
} catch {
    Write-Host "Count failed: $($_.Exception.Message)"
}