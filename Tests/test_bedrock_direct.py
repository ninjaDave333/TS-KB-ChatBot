#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.bedrock_client import BedrockClient
from app.database.neo4j_client import Neo4jClient

def test_bedrock_direct():
    print("=== Testing Bedrock Direct ===")
    
    client = Neo4jClient()
    bedrock = BedrockClient()
    
    schema = client.get_schema()
    query = "how many successful deals were conducted during 2025, show 5 examples"
    
    print(f"\nQuery: {query}")
    print(f"\nAttempting to generate Cypher...")
    
    try:
        cypher = bedrock.generate_cypher(query, schema)
        print(f"\nGenerated Cypher:\n{cypher}")
        
        print(f"\nAttempting to execute...")
        result = client.execute_query(cypher)
        print(f"\nResult: {result}")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bedrock_direct()