#!/usr/bin/env python3
"""
Test Teams Recording queries without year restrictions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.bedrock_client import BedrockClient
from app.database.neo4j_client import Neo4jClient

def test_queries_no_year():
    """Test Teams Recording queries without year restrictions"""
    
    bedrock = BedrockClient()
    neo4j = Neo4jClient()
    
    test_queries = [
        "How many external meetings recorded?",
        "David Gidony meetings breakdown internal external", 
        "Most active employee meeting wise",
        "Top 3 clients most recorded meetings"
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
                if len(result) > 1:
                    print(f"All results: {result}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_queries_no_year()