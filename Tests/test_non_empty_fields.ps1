# Find fields that actually have data

Write-Host "Finding non-empty fields..."

# Test 1: Check other Client fields from schema
Write-Host "`n1. Check Client sf_type:"
$body1 = @{
    query = "MATCH (c:Client) WHERE c.sf_type IS NOT NULL AND c.sf_type <> '' RETURN c.sf_type LIMIT 5"
    use_ai = $false
} | ConvertTo-Json

try {
    $response1 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body1 -ContentType "application/json"
    Write-Host "sf_type values:"
    $response1.data | ForEach-Object { Write-Host "  - '$($_.sf_type)'" }
} catch {
    Write-Host "sf_type failed"
}

# Test 2: Check Product fields
Write-Host "`n2. Check Product vendor:"
$body2 = @{
    query = "MATCH (p:Product) WHERE p.vendor IS NOT NULL AND p.vendor <> '' RETURN p.vendor LIMIT 5"
    use_ai = $false
} | ConvertTo-Json

try {
    $response2 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body2 -ContentType "application/json"
    Write-Host "Product vendors:"
    $response2.data | ForEach-Object { Write-Host "  - '$($_.vendor)'" }
} catch {
    Write-Host "vendor failed"
}

# Test 3: Check Employee names
Write-Host "`n3. Check Employee names:"
$body3 = @{
    query = "MATCH (e:Employee) WHERE e.name IS NOT NULL AND e.name <> '' RETURN e.name LIMIT 5"
    use_ai = $false
} | ConvertTo-Json

try {
    $response3 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body3 -ContentType "application/json"
    Write-Host "Employee names:"
    $response3.data | ForEach-Object { Write-Host "  - '$($_.name)'" }
} catch {
    Write-Host "employee names failed"
}

# Test 4: Count nodes by type
Write-Host "`n4. Node counts:"
$body4 = @{
    query = "MATCH (n) RETURN labels(n)[0] as type, count(n) as count ORDER BY count DESC"
    use_ai = $false
} | ConvertTo-Json

try {
    $response4 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body4 -ContentType "application/json"
    Write-Host "Node counts:"
    $response4.data | ForEach-Object { Write-Host "  - $($_.type): $($_.count)" }
} catch {
    Write-Host "node counts failed"
}