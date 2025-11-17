#!/usr/bin/env python3
"""
Final Teams Recording API Test
Tests both with and without year restrictions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

def test_query(query_text, description):
    """Test a single query against the API"""
    print(f"\n{description}")
    print(f"Query: {query_text}")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/query",
            json={"query": query_text},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS")
            print(f"   Method: {result.get('method', 'unknown')}")
            print(f"   Answer: {result['answer'][:150]}...")
            print(f"   Data Count: {len(result.get('data', []))}")
            print(f"   Execution Time: {result.get('execution_time', 0):.2f}s")
            return True
        else:
            print(f"FAILED - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    print("=== Final Teams Recording API Test ===")
    
    # Test queries without year restrictions (should work)
    test_queries_no_year = [
        ("How many external meetings recorded?", "1. External meetings count (no year)"),
        ("David Gidony meetings breakdown internal external", "2. David Gidony breakdown (no year)"),
        ("Most active employee meeting wise", "3. Most active employee (no year)"),
        ("Top 3 clients most recorded meetings", "4. Top 3 clients meetings (no year)")
    ]
    
    # Test queries with available date range
    test_queries_available_range = [
        ("How many external meetings recorded since August 2024?", "5. External meetings since Aug 2024"),
        ("Most active employee meeting wise in 2025", "6. Most active employee 2025")
    ]
    
    all_queries = test_queries_no_year + test_queries_available_range
    
    results = []
    for query, description in all_queries:
        success = test_query(query, description)
        results.append(success)
    
    print(f"\n=== Test Summary ===")
    print(f"Passed: {sum(results)}/{len(results)}")
    print(f"Success Rate: {sum(results)/len(results)*100:.1f}%")
    
    if all(results):
        print("All Teams Recording queries working!")
    else:
        print("Some queries need attention")

if __name__ == "__main__":
    main()