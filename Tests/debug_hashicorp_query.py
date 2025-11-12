#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database.neo4j_client import Neo4jClient
from app.core.bedrock_client import BedrockClient

def debug_hashicorp_query():
    client = Neo4jClient()
    bedrock = BedrockClient()
    
    print("=== Debugging HashiCorp Query ===")
    
    # 1. Check what HashiCorp products exist
    print("\n1. HashiCorp products:")
    hashicorp_products = client.execute_query("""
        MATCH (p:Product) 
        WHERE toLower(p.name) CONTAINS 'hashicorp' 
           OR toLower(p.vendor) CONTAINS 'hashicorp'
           OR toLower(p.sf_vendor) CONTAINS 'hashicorp'
        RETURN p.name, p.vendor, p.sf_vendor
        LIMIT 10
    """)
    print(f"Found {len(hashicorp_products)} HashiCorp products:")
    for product in hashicorp_products:
        print(f"  - {product}")
    
    # 2. Check clients with HashiCorp products (OPPORTUNITY)
    print("\n2. Clients with HashiCorp opportunities:")
    hashicorp_opportunities = client.execute_query("""
        MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
        WHERE toLower(p.name) CONTAINS 'hashicorp' 
           OR toLower(p.vendor) CONTAINS 'hashicorp'
        RETURN DISTINCT c.sf_name
        LIMIT 10
    """)
    print(f"Found {len(hashicorp_opportunities)} clients with HashiCorp opportunities:")
    for client_name in hashicorp_opportunities:
        print(f"  - {client_name}")
    
    # 3. Check clients with HashiCorp installations
    print("\n3. Clients with HashiCorp installations:")
    hashicorp_installs = client.execute_query("""
        MATCH (c:Client)-[i:HAS_INSTALLED]->(p:Product)
        WHERE toLower(p.name) CONTAINS 'hashicorp' 
           OR toLower(p.vendor) CONTAINS 'hashicorp'
        RETURN DISTINCT c.sf_name
        LIMIT 10
    """)
    print(f"Found {len(hashicorp_installs)} clients with HashiCorp installations:")
    for client_name in hashicorp_installs:
        print(f"  - {client_name}")
    
    # 4. Test AI query generation
    print("\n4. Testing AI query generation:")
    schema = client.get_schema()
    query = "how many clients have or using a hashicorp product ? list random 5 names out of these clients"
    
    try:
        ai_cypher = bedrock.generate_cypher(query, schema)
        print(f"AI Generated Cypher:\n{ai_cypher}")
        
        # Try to execute it
        try:
            ai_results = client.execute_query(ai_cypher)
            print(f"AI Query executed successfully: {len(ai_results)} results")
        except Exception as exec_error:
            print(f"AI Query execution failed: {exec_error}")
            
    except Exception as e:
        print(f"AI query generation failed: {e}")

if __name__ == "__main__":
    debug_hashicorp_query()