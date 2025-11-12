#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database.neo4j_client import Neo4jClient
from app.core.bedrock_client import BedrockClient

def test_hashicorp_fixed():
    client = Neo4jClient()
    bedrock = BedrockClient()
    
    print("=== Testing Fixed HashiCorp Query ===")
    
    # 1. Test the corrected query directly
    print("\n1. Direct query - Count HashiCorp clients:")
    count_query = """
        MATCH (c:Client)-[rel:OPPORTUNITY|HAS_INSTALLED]->(p:Product)
        WHERE toLower(p.vendor) CONTAINS 'hashicorp' 
           OR toLower(p.name) CONTAINS 'hashicorp'
        RETURN count(DISTINCT c) as total_clients
    """
    
    count_result = client.execute_query(count_query)
    total_clients = count_result[0]['total_clients']
    print(f"Total clients with HashiCorp products: {total_clients}")
    
    # 2. Get sample client names
    print("\n2. Sample HashiCorp clients:")
    sample_query = """
        MATCH (c:Client)-[rel:OPPORTUNITY|HAS_INSTALLED]->(p:Product)
        WHERE toLower(p.vendor) CONTAINS 'hashicorp' 
           OR toLower(p.name) CONTAINS 'hashicorp'
        WITH DISTINCT c
        RETURN c.sf_name
        LIMIT 5
    """
    
    sample_results = client.execute_query(sample_query)
    print(f"Sample clients:")
    for result in sample_results:
        print(f"  - {result['c.sf_name']}")
    
    # 3. Test AI query with updated schema
    print("\n3. Testing AI query with updated schema:")
    schema = client.get_schema()
    query = "how many clients have or using a hashicorp product ? list random 5 names out of these clients"
    
    try:
        ai_cypher = bedrock.generate_cypher(query, schema)
        print(f"AI Generated Cypher:\n{ai_cypher}")
        
        ai_results = client.execute_query(ai_cypher)
        print(f"AI Query Results: {len(ai_results)} results")
        for result in ai_results:
            print(f"  - {result}")
            
    except Exception as e:
        print(f"AI query failed: {e}")

if __name__ == "__main__":
    test_hashicorp_fixed()