"""
Test performance monitoring functionality.
"""

import time
import requests
import json

def test_performance_monitoring():
    """Test that performance monitoring is working correctly."""
    
    base_url = "http://localhost:8000"
    
    print("Testing Performance Monitoring...")
    
    # Test 1: Make a few queries to generate metrics
    test_queries = [
        "How many clients do we have?",
        "Who are the Israeli clients?",
        "What HashiCorp products were purchased in 2025?"
    ]
    
    print("\n1. Generating test queries...")
    for i, query in enumerate(test_queries, 1):
        try:
            response = requests.post(f"{base_url}/api/v1/query", 
                                   json={"query": query})
            if response.status_code == 200:
                print(f"   ✓ Query {i}: {response.json().get('method', 'unknown')}")
            else:
                print(f"   ✗ Query {i} failed: {response.status_code}")
        except Exception as e:
            print(f"   ✗ Query {i} error: {e}")
        
        time.sleep(0.5)  # Small delay between requests
    
    # Test 2: Check metrics endpoint
    print("\n2. Checking metrics endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/metrics")
        if response.status_code == 200:
            metrics = response.json()
            print(f"   ✓ Total queries: {metrics.get('total_queries', 0)}")
            print(f"   ✓ Success rate: {metrics.get('success_rate', 0)}%")
            print(f"   ✓ Avg execution time: {metrics.get('average_execution_time', 0)}s")
            print(f"   ✓ Query types: {metrics.get('query_type_breakdown', {})}")
        else:
            print(f"   ✗ Metrics endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Metrics endpoint error: {e}")
    
    # Test 3: Check detailed health endpoint
    print("\n3. Checking detailed health endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/health/detailed")
        if response.status_code == 200:
            health = response.json()
            print(f"   ✓ System status: {health.get('status', 'unknown')}")
            print(f"   ✓ Neo4j status: {health.get('neo4j', 'unknown')}")
            perf = health.get('performance', {})
            print(f"   ✓ Performance status: {perf.get('status', 'unknown')}")
        else:
            print(f"   ✗ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Health endpoint error: {e}")
    
    print("\nPerformance monitoring test completed!")

if __name__ == "__main__":
    test_performance_monitoring()