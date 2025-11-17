#!/usr/bin/env python3
"""
Debug Cypher Generation for Teams Recording Queries
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.bedrock_client import BedrockClient
from app.database.neo4j_client import Neo4jClient

def test_cypher_generation():
    """Test Cypher generation for Teams Recording queries"""
    
    bedrock = BedrockClient()
    neo4j = Neo4jClient()
    
    test_queries = [
        "How many external meetings recorded during 2024?",
        "David Gidony meetings breakdown 2024 internal external", 
        "Most active employee meeting wise 2024"
    ]
    
    for query in test_queries:
        print(f"\n=== Testing: {query} ===")
        
        try:
            # Generate Cypher
            cypher = bedrock.generate_cypher(query, {})
            print(f"Generated Cypher: {cypher}")
            
            # Test execution
            result = neo4j.execute_query(cypher)
            print(f"Result count: {len(result)}")
            if result:
                print(f"Sample result: {result[0]}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_cypher_generation()