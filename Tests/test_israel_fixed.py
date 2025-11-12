#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database.neo4j_client import Neo4jClient
from app.core.bedrock_client import BedrockClient

def test_israel_query():
    client = Neo4jClient()
    bedrock = BedrockClient()
    
    print("=== Testing Fixed Israel Clients Query ===")
    
    # Test the corrected query directly
    print("\n1. Direct query for Israel clients:")
    direct_query = """
        MATCH (c:Client) 
        WHERE c.region = 'IL' AND c.sf_name IS NOT NULL
        RETURN c.sf_name, c.sf_account_status, c.sf_billing_country
        ORDER BY c.sf_name
    """
    
    results = client.execute_query(direct_query)
    print(f"Found {len(results)} Israel clients:")
    for result in results:
        print(f"  - {result}")
    
    # Test AI query with updated schema
    print("\n2. Testing AI query with updated schema:")
    schema = client.get_schema()
    query = "list the names of all active clients we have in israel"
    
    try:
        ai_cypher = bedrock.generate_cypher(query, schema)
        print(f"AI Generated Cypher: {ai_cypher}")
        
        ai_results = client.execute_query(ai_cypher)
        print(f"AI Query Results: {len(ai_results)} clients found")
        for result in ai_results[:5]:  # Show first 5
            print(f"  - {result}")
            
    except Exception as e:
        print(f"AI query failed: {e}")

if __name__ == "__main__":
    test_israel_query()