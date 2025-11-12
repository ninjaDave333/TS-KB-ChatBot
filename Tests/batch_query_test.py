#!/usr/bin/env python3

import requests
import json
import time
from datetime import datetime

def batch_query_test():
    print("=== RAG Batch Query Testing ===")
    print("Testing 10 different query patterns...")
    
    # Test queries
    test_queries = [
        {
            "id": 1,
            "query": "how many successful deals were conducted during 2025, show 5 examples",
            "expected_filters": ["2025", "Closed Won"],
            "category": "temporal_deals"
        },
        {
            "id": 2,
            "query": "list 5 clients in israel with their account managers",
            "expected_filters": ["IL", "MANAGED_BY"],
            "category": "location_relationships"
        },
        {
            "id": 3,
            "query": "how many hashicorp products were purchased in 2025, show client names",
            "expected_filters": ["hashicorp", "2025", "Closed Won"],
            "category": "vendor_temporal"
        },
        {
            "id": 4,
            "query": "show me 5 employees who manage the most clients",
            "expected_filters": ["MANAGED_BY", "count"],
            "category": "aggregation_relationships"
        },
        {
            "id": 5,
            "query": "what products does wix have installed, show installation dates",
            "expected_filters": ["wix", "HAS_INSTALLED"],
            "category": "client_installations"
        },
        {
            "id": 6,
            "query": "how many clients are using aws products from different business units",
            "expected_filters": ["aws", "BELONGS_TO"],
            "category": "vendor_bu_analysis"
        },
        {
            "id": 7,
            "query": "list successful opportunities for microsoft products in 2025",
            "expected_filters": ["microsoft", "2025", "Closed Won"],
            "category": "vendor_year_success"
        },
        {
            "id": 8,
            "query": "show me 5 products that require devops skills",
            "expected_filters": ["devops", "REQUIRES_SKILL"],
            "category": "skill_requirements"
        },
        {
            "id": 9,
            "query": "how many clients in each region purchased products in 2025",
            "expected_filters": ["region", "2025", "group by"],
            "category": "regional_analysis"
        },
        {
            "id": 10,
            "query": "what are the top 5 most purchased products by israeli clients",
            "expected_filters": ["IL", "count", "order by"],
            "category": "location_popularity"
        }
    ]
    
    # Results tracking
    results = []
    success_count = 0
    syntax_errors = 0
    empty_results = 0
    
    for test in test_queries:
        print(f"\n--- Test {test['id']}: {test['category']} ---")
        print(f"Query: {test['query']}")
        
        try:
            # Execute query
            start_time = time.time()
            response = requests.post(
                "http://localhost:8000/api/v1/query",
                json={"query": test["query"], "use_ai": True},
                headers={"Content-Type": "application/json"}
            )
            end_time = time.time()
            duration = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                # Analyze response
                status = "SUCCESS"
                issues = []
                
                # Check for data
                if len(data.get("data", [])) == 0:
                    status = "EMPTY_RESULTS"
                    empty_results += 1
                    issues.append("No data returned")
                else:
                    success_count += 1
                
                # Check for expected filters in Cypher
                cypher = data.get("cypher_query", "")
                for filter_term in test["expected_filters"]:
                    if filter_term.lower() not in cypher.lower():
                        issues.append(f"Missing expected filter: {filter_term}")
                
                # Check for common issues
                if cypher.endswith(","):
                    issues.append("Potential trailing comma")
                
                if "close_date" in cypher:
                    issues.append("Using wrong date field (close_date instead of purchased_date)")
                
                if "LOCATED_IN" in cypher:
                    issues.append("Using non-existent LOCATED_IN relationship")
                
                # Store results
                results.append({
                    "id": test["id"],
                    "category": test["category"],
                    "query": test["query"],
                    "status": status,
                    "duration_ms": round(duration, 2),
                    "method": data.get("method", "unknown"),
                    "cypher": cypher,
                    "data_count": len(data.get("data", [])),
                    "issues": issues,
                    "error": None
                })
                
                print(f"Status: {status}")
                print(f"Duration: {round(duration, 2)}ms")
                print(f"Method: {data.get('method', 'unknown')}")
                print(f"Data Count: {len(data.get('data', []))}")
                if issues:
                    print(f"Issues: {', '.join(issues)}")
                    
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            syntax_errors += 1
            error_msg = str(e)
            
            results.append({
                "id": test["id"],
                "category": test["category"],
                "query": test["query"],
                "status": "SYNTAX_ERROR",
                "duration_ms": 0,
                "method": "failed",
                "cypher": "N/A",
                "data_count": 0,
                "issues": ["Syntax error"],
                "error": error_msg
            })
            
            print(f"Status: SYNTAX_ERROR")
            print(f"Error: {error_msg}")
    
    # Summary Report
    print(f"\n=== BATCH TEST SUMMARY ===")
    print(f"Total Tests: {len(test_queries)}")
    print(f"Successful: {success_count}")
    print(f"Empty Results: {empty_results}")
    print(f"Syntax Errors: {syntax_errors}")
    print(f"Success Rate: {round((success_count / len(test_queries)) * 100, 1)}%")
    
    # Category Analysis
    print(f"\n=== CATEGORY ANALYSIS ===")
    categories = {}
    for result in results:
        cat = result["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "success": 0}
        categories[cat]["total"] += 1
        if result["status"] == "SUCCESS":
            categories[cat]["success"] += 1
    
    for cat, stats in categories.items():
        success_rate = round((stats["success"] / stats["total"]) * 100, 1)
        print(f"{cat}: {stats['success']}/{stats['total']} ({success_rate}%)")
    
    # Common Issues Analysis
    print(f"\n=== COMMON ISSUES ===")
    all_issues = []
    for result in results:
        all_issues.extend(result["issues"])
    
    issue_counts = {}
    for issue in all_issues:
        issue_counts[issue] = issue_counts.get(issue, 0) + 1
    
    for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{issue}: {count} occurrences")
    
    # Export results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"Tests/batch_test_results_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results exported to: {results_file}")
    
    # Recommendations
    print(f"\n=== RECOMMENDATIONS ===")
    if syntax_errors > 2:
        print("- High syntax error rate: Review schema descriptions and AI prompts")
    if empty_results > 3:
        print("- High empty result rate: Check data availability and filter accuracy")
    if success_count < 7:
        print("- Low success rate: Consider implementing query validation layer")
    
    print("\nBatch testing completed!")

if __name__ == "__main__":
    batch_query_test()