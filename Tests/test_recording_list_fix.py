#!/usr/bin/env python3
"""
Test the recording list answer generation fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

def test_recording_list():
    """Test the recording list query with owner names"""
    
    query = "list names of the latest 5 recordings added to the db, and their owner name"
    
    print(f"Testing: {query}")
    
    try:
        response = requests.post(
            "http://localhost:8002/api/v1/query",
            json={"query": query},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS")
            print(f"Method: {result.get('method')}")
            print(f"Answer: {result['answer']}")
            print(f"Data Count: {len(result.get('data', []))}")
            
            # Check if owner names are included
            if "Owner:" in result['answer']:
                print("✓ Owner names are properly included in the answer")
            else:
                print("✗ Owner names are missing from the answer")
                
        else:
            print(f"FAILED - Status: {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_recording_list()