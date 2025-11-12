# Find ANY non-empty fields

Write-Host "Looking for ANY non-empty data..."

# Test 1: Check if nodes have ANY string properties with data
Write-Host "`n1. Sample Client with all fields:"
$body1 = @{
    query = "MATCH (c:Client) RETURN c LIMIT 1"
    use_ai = $false
} | ConvertTo-Json

try {
    $response1 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body1 -ContentType "application/json"
    Write-Host "Full Client node:"
    $response1.data[0] | ConvertTo-Json -Depth 3
} catch {
    Write-Host "Failed to get client: $($_.Exception.Message)"
}

# Test 2: Check Employee with all fields
Write-Host "`n2. Sample Employee with all fields:"
$body2 = @{
    query = "MATCH (e:Employee) RETURN e LIMIT 1"
    use_ai = $false
} | ConvertTo-Json

try {
    $response2 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body2 -ContentType "application/json"
    Write-Host "Full Employee node:"
    $response2.data[0] | ConvertTo-Json -Depth 3
} catch {
    Write-Host "Failed to get employee: $($_.Exception.Message)"
}

# Test 3: Check Product with all fields
Write-Host "`n3. Sample Product with all fields:"
$body3 = @{
    query = "MATCH (p:Product) RETURN p LIMIT 1"
    use_ai = $false
} | ConvertTo-Json

try {
    $response3 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body3 -ContentType "application/json"
    Write-Host "Full Product node:"
    $response3.data[0] | ConvertTo-Json -Depth 3
} catch {
    Write-Host "Failed to get product: $($_.Exception.Message)"
}