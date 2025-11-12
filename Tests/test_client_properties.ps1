# Check actual Client node properties

Write-Host "Checking Client node properties..."

# Test 1: Get all properties of first client
Write-Host "`n1. Properties of first client:"
$body1 = @{
    query = "MATCH (c:Client) RETURN properties(c) as props LIMIT 1"
    use_ai = $false
} | ConvertTo-Json

$response1 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body1 -ContentType "application/json"
Write-Host "Client properties:"
$response1.data[0].props | ConvertTo-Json

# Test 2: Check if sf_name exists
Write-Host "`n2. Check sf_name field:"
$body2 = @{
    query = "MATCH (c:Client) WHERE c.sf_name IS NOT NULL RETURN c.sf_name LIMIT 5"
    use_ai = $false
} | ConvertTo-Json

$response2 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body2 -ContentType "application/json"
Write-Host "sf_name values:"
$response2.data | ForEach-Object { Write-Host "  - $($_.sf_name)" }

# Test 3: Find WIX specifically
Write-Host "`n3. Find WIX client:"
$body3 = @{
    query = "MATCH (c:Client) WHERE toLower(c.sf_name) CONTAINS 'wix' RETURN c.sf_name, c.name"
    use_ai = $false
} | ConvertTo-Json

$response3 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body3 -ContentType "application/json"
Write-Host "WIX client found:"
$response3.data | ForEach-Object { Write-Host "  sf_name: $($_.sf_name), name: $($_.name)" }