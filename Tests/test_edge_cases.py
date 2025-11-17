#!/usr/bin/env python3
"""
Test edge cases for Teams Recording queries
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

def test_query(query_text, description):
    """Test a single query"""
    print(f"\n{description}")
    print(f"Query: {query_text}")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/query",
            json={"query": query_text},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS - Method: {result.get('method')}")
            print(f"Answer: {result['answer'][:100]}...")
            print(f"Data Count: {len(result.get('data', []))}")
            return True
        else:
            print(f"FAILED - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    print("=== Edge Case Testing ===")
    
    edge_cases = [
        ("John Doe meetings breakdown", "1. Invalid employee name"),
        ("How many meetings recorded in 1999?", "2. Invalid date range"),
        ("Most active employee meeting wise in 2030", "3. Future date"),
        ("External meetings recorded yesterday", "4. Relative date"),
        ("Top 100 clients most recorded meetings", "5. Large result set")
    ]
    
    results = []
    for query, description in edge_cases:
        success = test_query(query, description)
        results.append(success)
    
    print(f"\n=== Edge Case Summary ===")
    print(f"Handled: {sum(results)}/{len(results)}")

if __name__ == "__main__":
    main()