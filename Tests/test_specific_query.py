#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.bedrock_client import BedrockClient
from app.database.neo4j_client import Neo4jClient
from app.core.query_validator import CypherValidator

def test_query():
    client = Neo4jClient()
    bedrock = BedrockClient()
    validator = CypherValidator()
    
    query = "how many successful deals were conducted during 2025, show 5 examples of hashicorp deals"
    
    print(f"Query: {query}\n")
    
    # Generate
    schema = client.get_schema()
    cypher = bedrock.generate_cypher(query, schema)
    print(f"Generated Cypher:\n{cypher}\n")
    
    # Validate
    is_valid, fixed, issues = validator.validate_and_fix(cypher)
    print(f"Validation:")
    print(f"  Valid: {is_valid}")
    print(f"  Issues: {issues}")
    print(f"  Fixed: {fixed}\n")
    
    # Execute
    try:
        result = client.execute_query(fixed if is_valid else cypher)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Execution error: {e}")

if __name__ == "__main__":
    test_query()