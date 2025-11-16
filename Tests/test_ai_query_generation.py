#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.bedrock_client import BedrockClient
from app.database.neo4j_client import Neo4jClient

def test_query():
    bedrock = BedrockClient()
    neo4j = Neo4jClient()
    
    query = "what year is the first successful deal for a non terasky vendor documented in the db ? and for which client and what product"
    
    print(f"User Query: {query}\n")
    
    schema = neo4j.get_schema()
    
    try:
        cypher = bedrock.generate_cypher(query, schema)
        print(f"Generated Cypher:\n{cypher}\n")
        
        # Try to execute
        result = neo4j.execute_query(cypher)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_query()
