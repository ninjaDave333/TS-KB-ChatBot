# Batch Query Testing Script for RAG Accuracy Analysis
# Tests various query patterns to identify systematic issues

Write-Host "=== RAG Batch Query Testing ===" -ForegroundColor Green
Write-Host "Testing 10 different query patterns..." -ForegroundColor Yellow

# Test queries array
$testQueries = @(
    @{
        id = 1
        query = "how many successful deals were conducted during 2025, show 5 examples"
        expected_filters = @("2025", "Closed Won")
        category = "temporal_deals"
    },
    @{
        id = 2
        query = "list 5 clients in israel with their account managers"
        expected_filters = @("IL", "MANAGED_BY")
        category = "location_relationships"
    },
    @{
        id = 3
        query = "how many hashicorp products were purchased in 2025, show client names"
        expected_filters = @("hashicorp", "2025", "Closed Won")
        category = "vendor_temporal"
    },
    @{
        id = 4
        query = "show me 5 employees who manage the most clients"
        expected_filters = @("MANAGED_BY", "count")
        category = "aggregation_relationships"
    },
    @{
        id = 5
        query = "what products does wix have installed, show installation dates"
        expected_filters = @("wix", "HAS_INSTALLED")
        category = "client_installations"
    },
    @{
        id = 6
        query = "how many clients are using aws products from different business units"
        expected_filters = @("aws", "BELONGS_TO")
        category = "vendor_bu_analysis"
    },
    @{
        id = 7
        query = "list successful opportunities for microsoft products in 2025"
        expected_filters = @("microsoft", "2025", "Closed Won")
        category = "vendor_year_success"
    },
    @{
        id = 8
        query = "show me 5 products that require devops skills"
        expected_filters = @("devops", "REQUIRES_SKILL")
        category = "skill_requirements"
    },
    @{
        id = 9
        query = "how many clients in each region purchased products in 2025"
        expected_filters = @("region", "2025", "group by")
        category = "regional_analysis"
    },
    @{
        id = 10
        query = "what are the top 5 most purchased products by israeli clients"
        expected_filters = @("IL", "count", "order by")
        category = "location_popularity"
    }
)

# Results tracking
$results = @()
$successCount = 0
$syntaxErrors = 0
$emptyResults = 0

foreach ($test in $testQueries) {
    Write-Host "`n--- Test $($test.id): $($test.category) ---" -ForegroundColor Cyan
    Write-Host "Query: $($test.query)"
    
    try {
        # Prepare request body
        $body = @{
            query = $test.query
            use_ai = $true
        } | ConvertTo-Json -Depth 3
        
        # Execute query
        $startTime = Get-Date
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method POST -Body $body -ContentType "application/json" -ErrorAction Stop
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalMilliseconds
        
        # Analyze response
        $status = "SUCCESS"
        $issues = @()
        
        # Check for data
        if ($response.data.Count -eq 0) {
            $status = "EMPTY_RESULTS"
            $emptyResults++
            $issues += "No data returned"
        } else {
            $successCount++
        }
        
        # Check for expected filters in Cypher
        foreach ($filter in $test.expected_filters) {
            if ($response.cypher_query -notlike "*$filter*") {
                $issues += "Missing expected filter: $filter"
            }
        }
        
        # Check for common issues
        if ($response.cypher_query -like "*,`n*" -or $response.cypher_query -like "*,`r`n*") {
            $issues += "Potential trailing comma"
        }
        
        if ($response.cypher_query -like "*close_date*") {
            $issues += "Using wrong date field (close_date instead of purchased_date)"
        }
        
        if ($response.cypher_query -like "*LOCATED_IN*") {
            $issues += "Using non-existent LOCATED_IN relationship"
        }
        
        # Store results
        $results += @{
            id = $test.id
            category = $test.category
            query = $test.query
            status = $status
            duration_ms = [math]::Round($duration, 2)
            method = $response.method
            cypher = $response.cypher_query
            data_count = $response.data.Count
            issues = $issues
            error = $null
        }
        
        Write-Host "Status: $status" -ForegroundColor $(if ($status -eq "SUCCESS") { "Green" } else { "Yellow" })
        Write-Host "Duration: $([math]::Round($duration, 2))ms"
        Write-Host "Method: $($response.method)"
        Write-Host "Data Count: $($response.data.Count)"
        if ($issues.Count -gt 0) {
            Write-Host "Issues: $($issues -join ', ')" -ForegroundColor Red
        }
        
    } catch {
        $syntaxErrors++
        $errorMsg = $_.Exception.Message
        
        $results += @{
            id = $test.id
            category = $test.category
            query = $test.query
            status = "SYNTAX_ERROR"
            duration_ms = 0
            method = "failed"
            cypher = "N/A"
            data_count = 0
            issues = @("Syntax error")
            error = $errorMsg
        }
        
        Write-Host "Status: SYNTAX_ERROR" -ForegroundColor Red
        Write-Host "Error: $errorMsg" -ForegroundColor Red
    }
}

# Summary Report
Write-Host "`n=== BATCH TEST SUMMARY ===" -ForegroundColor Green
Write-Host "Total Tests: $($testQueries.Count)"
Write-Host "Successful: $successCount" -ForegroundColor Green
Write-Host "Empty Results: $emptyResults" -ForegroundColor Yellow
Write-Host "Syntax Errors: $syntaxErrors" -ForegroundColor Red
Write-Host "Success Rate: $([math]::Round(($successCount / $testQueries.Count) * 100, 1))%"

# Category Analysis
Write-Host "`n=== CATEGORY ANALYSIS ===" -ForegroundColor Green
$categoryStats = $results | Group-Object category | ForEach-Object {
    $successInCategory = ($_.Group | Where-Object { $_.status -eq "SUCCESS" }).Count
    @{
        category = $_.Name
        total = $_.Count
        success = $successInCategory
        success_rate = [math]::Round(($successInCategory / $_.Count) * 100, 1)
    }
} | Sort-Object success_rate

foreach ($cat in $categoryStats) {
    Write-Host "$($cat.category): $($cat.success)/$($cat.total) ($($cat.success_rate)%)"
}

# Common Issues Analysis
Write-Host "`n=== COMMON ISSUES ===" -ForegroundColor Green
$allIssues = $results | ForEach-Object { $_.issues } | Where-Object { $_ -ne $null }
$issueGroups = $allIssues | Group-Object | Sort-Object Count -Descending

foreach ($issue in $issueGroups) {
    Write-Host "$($issue.Name): $($issue.Count) occurrences" -ForegroundColor Yellow
}

# Export detailed results
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$resultsFile = "Tests/batch_test_results_$timestamp.json"
$results | ConvertTo-Json -Depth 5 | Out-File $resultsFile
Write-Host "`nDetailed results exported to: $resultsFile" -ForegroundColor Cyan

Write-Host "`n=== RECOMMENDATIONS ===" -ForegroundColor Green
if ($syntaxErrors -gt 2) {
    Write-Host "- High syntax error rate: Review schema descriptions and AI prompts" -ForegroundColor Red
}
if ($emptyResults -gt 3) {
    Write-Host "- High empty result rate: Check data availability and filter accuracy" -ForegroundColor Yellow
}
if ($successCount -lt 7) {
    Write-Host "- Low success rate: Consider implementing query validation layer" -ForegroundColor Red
}

Write-Host "`nBatch testing completed!" -ForegroundColor Green