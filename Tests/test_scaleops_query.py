#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database.neo4j_client import Neo4jClient
from app.core.bedrock_client import BedrockClient

def test_scaleops_query():
    client = Neo4jClient()
    bedrock = BedrockClient()
    
    print("=== Testing ScaleOps Query ===")
    
    # 1. Check if ScaleOps products exist
    print("\n1. ScaleOps products:")
    scaleops_products = client.execute_query("""
        MATCH (p:Product) 
        WHERE toLower(p.name) CONTAINS 'scaleops' 
           OR toLower(p.vendor) CONTAINS 'scaleops'
           OR toLower(p.sf_vendor) CONTAINS 'scaleops'
        RETURN p.name, p.vendor, p.sf_vendor
        LIMIT 10
    """)
    print(f"Found {len(scaleops_products)} ScaleOps products:")
    for product in scaleops_products:
        print(f"  - {product}")
    
    if len(scaleops_products) == 0:
        print("No ScaleOps products found - testing with standard Cypher pattern")
        
        # Test the corrected query pattern without APOC
        print("\n2. Testing standard Cypher pattern:")
        test_query = """
            MATCH (c:Client)-[rel:OPPORTUNITY|HAS_INSTALLED]->(p:Product)
            WHERE toLower(p.vendor) CONTAINS 'hashicorp'
            WITH DISTINCT c
            WITH count(c) as total, collect(c.sf_name)[0..5] as sample_names
            RETURN total, sample_names
        """
        
        test_results = client.execute_query(test_query)
        print(f"Test query results: {test_results}")
    
    # 3. Test AI query with updated schema
    print("\n3. Testing AI query with updated schema:")
    schema = client.get_schema()
    query = "how many clients have or using a scaleops product ? list total number and a random 5 names out of these clients"
    
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
    test_scaleops_query()