# Simple client property check

Write-Host "Simple client check..."

# Test 1: Check specific fields one by one
Write-Host "`n1. Check sf_name:"
$body1 = @{
    query = "MATCH (c:Client) RETURN c.sf_name LIMIT 3"
    use_ai = $false
} | ConvertTo-Json

try {
    $response1 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body1 -ContentType "application/json"
    Write-Host "sf_name results:"
    $response1.data | ForEach-Object { Write-Host "  - '$($_.sf_name)'" }
} catch {
    Write-Host "sf_name failed: $($_.Exception.Message)"
}

# Test 2: Check name field
Write-Host "`n2. Check name:"
$body2 = @{
    query = "MATCH (c:Client) RETURN c.name LIMIT 3"
    use_ai = $false
} | ConvertTo-Json

try {
    $response2 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body2 -ContentType "application/json"
    Write-Host "name results:"
    $response2.data | ForEach-Object { Write-Host "  - '$($_.name)'" }
} catch {
    Write-Host "name failed: $($_.Exception.Message)"
}

# Test 3: Try different field names from schema docs
Write-Host "`n3. Check sf_id:"
$body3 = @{
    query = "MATCH (c:Client) RETURN c.sf_id LIMIT 3"
    use_ai = $false
} | ConvertTo-Json

try {
    $response3 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body3 -ContentType "application/json"
    Write-Host "sf_id results:"
    $response3.data | ForEach-Object { Write-Host "  - '$($_.sf_id)'" }
} catch {
    Write-Host "sf_id failed: $($_.Exception.Message)"
}