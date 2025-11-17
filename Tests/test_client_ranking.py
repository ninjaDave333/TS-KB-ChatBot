#!/usr/bin/env python3
"""
Test client ranking fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

def test_client_ranking():
    """Test the client ranking query"""
    
    response = requests.post(
        "http://localhost:8000/api/v1/query",
        json={"query": "Top 3 clients most recorded meetings"},
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        print("SUCCESS")
        print(f"Answer: {result['answer']}")
        print(f"Data: {result['data']}")
    else:
        print(f"FAILED: {response.text}")

if __name__ == "__main__":
    test_client_ranking()