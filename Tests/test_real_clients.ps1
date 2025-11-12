# Find real client names

Write-Host "Finding actual client names..."

# Test 1: Get some client names
Write-Host "`n1. Sample client names:"
$body1 = @{
    query = "MATCH (c:Client) RETURN c.name LIMIT 10"
    use_ai = $false
} | ConvertTo-Json

$response1 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body1 -ContentType "application/json"
Write-Host "Sample clients:"
$response1.data | ForEach-Object { Write-Host "  - $($_.name)" }

# Test 2: Find clients with "wix" in name (case insensitive)
Write-Host "`n2. Clients containing 'wix':"
$body2 = @{
    query = "MATCH (c:Client) WHERE toLower(c.name) CONTAINS 'wix' RETURN c.name"
    use_ai = $false
} | ConvertTo-Json

$response2 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body2 -ContentType "application/json"
if ($response2.data.Count -gt 0) {
    $response2.data | ForEach-Object { Write-Host "  - $($_.name)" }
} else {
    Write-Host "  No clients with 'wix' found"
}

# Test 3: Test with a real client that has opportunities
Write-Host "`n3. First client with opportunities:"
$body3 = @{
    query = "MATCH (c:Client)-[:OPPORTUNITY]->(p:Product) RETURN c.name, count(p) as product_count ORDER BY product_count DESC LIMIT 1"
    use_ai = $false
} | ConvertTo-Json

$response3 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body3 -ContentType "application/json"
Write-Host "Client with most opportunities: $($response3.data[0].name) ($($response3.data[0].product_count) products)"