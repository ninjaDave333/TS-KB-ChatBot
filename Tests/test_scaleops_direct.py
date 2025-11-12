#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database.neo4j_client import Neo4jClient

def test_scaleops_direct():
    client = Neo4jClient()
    
    print("=== Testing ScaleOps Direct Query ===")
    
    # Test the correct query directly
    print("\n1. Direct ScaleOps query:")
    direct_query = """
        MATCH (c:Client)-[rel:OPPORTUNITY|HAS_INSTALLED]->(p:Product)
        WHERE toLower(p.name) CONTAINS 'scaleops'
        WITH DISTINCT c
        WITH count(c) as total, collect(c.sf_name)[0..5] as samples
        RETURN total, samples
    """
    
    results = client.execute_query(direct_query)
    print(f"Results: {results}")

if __name__ == "__main__":
    test_scaleops_direct()