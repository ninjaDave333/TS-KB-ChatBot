"""
Test Teams Recording API integration.
"""

import requests
import json

def test_api():
    """Test Teams Recording queries via API."""
    
    base_url = "http://localhost:8000/api/v1"
    
    queries = [
        "How many external meetings recorded?",
        "David Gidony meetings breakdown internal external", 
        "Most active employee meeting wise",
        "Top 3 clients most recorded meetings"
    ]
    
    print("=== API Integration Test ===\n")
    
    for i, query in enumerate(queries, 1):
        print(f"{i}. Testing: {query}")
        
        try:
            response = requests.post(
                f"{base_url}/query",
                json={"query": query, "use_ai": True},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Status: SUCCESS")
                print(f"   Method: {data.get('method', 'unknown')}")
                print(f"   Answer: {data.get('answer', 'No answer')}")
                print(f"   Data Count: {len(data.get('data', []))}")
            else:
                print(f"   Status: FAILED ({response.status_code})")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"   Status: ERROR - {e}")
            
        print()
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    test_api()