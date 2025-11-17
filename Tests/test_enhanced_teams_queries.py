#!/usr/bin/env python3
"""
Enhanced Teams Recording Query Test
Tests the improved query patterns with corrected date ranges
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
            print(f"   Answer: {result['answer'][:100]}...")
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
    print("=== Enhanced Teams Recording Query Test ===")
    
    # Test queries with corrected date ranges
    test_queries = [
        ("How many external meetings recorded during 2024?", "1. External meetings count 2024"),
        ("David Gidony meetings breakdown 2024 internal external", "2. David Gidony breakdown 2024"),
        ("Most active employee meeting wise 2024", "3. Most active employee 2024"),
        ("Most active employee July 2024", "4. Most active employee July 2024"),
        ("Top 3 clients most recorded meetings 2024", "5. Top 3 clients meetings 2024")
    ]
    
    results = []
    for query, description in test_queries:
        success = test_query(query, description)
        results.append(success)
    
    print(f"\n=== Test Summary ===")
    print(f"Passed: {sum(results)}/{len(results)}")
    print(f"Success Rate: {sum(results)/len(results)*100:.1f}%")
    
    if all(results):
        print("All enhanced Teams Recording queries working!")
    else:
        print("Some queries need attention")

if __name__ == "__main__":
    main()