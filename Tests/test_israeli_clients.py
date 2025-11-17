#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.neo4j_client import Neo4jClient

def test_israeli_clients():
    """Test correct query for Israeli clients"""
    
    client = Neo4jClient()
    
    # Test the correct query
    correct_query = """
    MATCH (c:Client)-[:MANAGED_BY]->(e:Employee) 
    WHERE c.region = 'IL' 
    RETURN c.sf_name as client, e.name as account_manager 
    LIMIT 5
    """
    
    print("Testing correct Israeli clients query:")
    print(correct_query)
    
    try:
        result = client.execute_query(correct_query)
        print(f"✅ Success: Found {len(result)} Israeli clients with managers")
        
        for record in result:
            print(f"  - {record['client']} managed by {record['account_manager']}")
            
        return len(result) > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_wrong_query():
    """Test the wrong query that AI is generating"""
    
    client = Neo4jClient()
    
    # Test the wrong query
    wrong_query = """
    MATCH (c:Client)-[:MANAGED_BY]->(am:AccountManager) 
    WHERE c.country = 'Israel' 
    RETURN c.sf_name as client, am.name as account_manager 
    LIMIT 5
    """
    
    print("\nTesting wrong query (what AI currently generates):")
    print(wrong_query)
    
    try:
        result = client.execute_query(wrong_query)
        print(f"Result: {len(result)} records (should be 0)")
        return len(result) == 0
        
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return True  # Expected to fail

if __name__ == "__main__":
    print("=== Israeli Clients Query Test ===")
    
    correct_works = test_israeli_clients()
    wrong_fails = test_wrong_query()
    
    print(f"\n=== Results ===")
    print(f"Correct query works: {'✅' if correct_works else '❌'}")
    print(f"Wrong query fails: {'✅' if wrong_fails else '❌'}")
    
    if correct_works:
        print("\n🎯 The correct query finds Israeli clients!")
        print("Next: Restart API server to apply schema fixes")
    else:
        print("\n⚠️ No Israeli clients found - check data or query")