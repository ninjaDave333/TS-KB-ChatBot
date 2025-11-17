"""
Test Teams Recording integration with TSKB-RAG system.
"""

import requests
import json

def test_recording_queries():
    """Test various recording-related queries."""
    
    base_url = "http://localhost:8000/api/v1"
    
    test_queries = [
        "How many recordings have been processed?",
        "Show me recent terraform meeting recordings",
        "List failed recordings with error messages",
        "Find meetings organized by employees with 'john' in their name",
        "Show recordings from the last week"
    ]
    
    print("=== Testing Teams Recording Integration ===\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"{i}. Testing: {query}")
        
        try:
            response = requests.post(
                f"{base_url}/query",
                json={"query": query, "use_ai": True},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Status: SUCCESS")
                print(f"   Method: {data.get('method', 'unknown')}")
                print(f"   Data Count: {len(data.get('data', []))}")
                print(f"   Answer: {data.get('answer', 'No answer')[:100]}...")
                
                # Show sample data
                if data.get('data'):
                    print(f"   Sample: {data['data'][0] if data['data'] else 'No data'}")
                    
            else:
                print(f"   Status: FAILED ({response.status_code})")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"   Status: ERROR - {e}")
            
        print()
    
    print("=== Integration Test Complete ===")

if __name__ == "__main__":
    test_recording_queries()