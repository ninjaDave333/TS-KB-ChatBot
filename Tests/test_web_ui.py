#!/usr/bin/env python3
"""
Test the web UI functionality
"""

import requests

def test_web_ui():
    """Test the web UI endpoints"""
    
    print("=== Testing Web UI ===")
    
    # Test UI page
    response = requests.get("http://localhost:8000/promptui")
    if response.status_code == 200 and "TSKB RAG Chat Interface" in response.text:
        print("SUCCESS: /promptui route working")
    else:
        print("FAILED: /promptui route failed")
    
    # Test API integration
    response = requests.post(
        "http://localhost:8000/api/v1/query",
        json={"query": "How many external meetings recorded?"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"SUCCESS: API integration working: {data['answer'][:50]}...")
    else:
        print("FAILED: API integration failed")
    
    print("\nWeb UI available at: http://localhost:8000/promptui")

if __name__ == "__main__":
    test_web_ui()