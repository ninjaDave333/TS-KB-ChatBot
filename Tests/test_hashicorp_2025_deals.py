#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database.neo4j_client import Neo4jClient

def test_hashicorp_2025_deals():
    client = Neo4jClient()
    
    print("=== Testing HashiCorp 2025 Deals Query ===")
    
    # Correct query with all filters
    print("\n1. Correct query with all filters:")
    correct_query = """
        MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
        WHERE o.opportunity_stage = 'Closed Won' 
          AND (toLower(p.vendor) CONTAINS 'hashicorp' OR toLower(p.name) CONTAINS 'hashicorp')
          AND o.purchased_date CONTAINS '2025'
        WITH count(o) as total, collect({client: c.sf_name, product: p.name, date: o.purchased_date})[0..5] as samples
        RETURN total, samples
    """
    
    results = client.execute_query(correct_query)
    print(f"Results: {results}")
    
    # Check if we have any 2025 data at all
    print("\n2. Check 2025 opportunities:")
    year_check = client.execute_query("""
        MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
        WHERE o.opportunity_stage = 'Closed Won' 
          AND o.purchased_date IS NOT NULL
          AND o.purchased_date CONTAINS '2025'
        RETURN count(o) as total_2025
    """)
    print(f"Total 2025 deals: {year_check}")
    
    # Check HashiCorp deals (any year)
    print("\n3. Check HashiCorp deals (any year):")
    hashicorp_check = client.execute_query("""
        MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
        WHERE o.opportunity_stage = 'Closed Won' 
          AND (toLower(p.vendor) CONTAINS 'hashicorp' OR toLower(p.name) CONTAINS 'hashicorp')
        RETURN count(o) as total_hashicorp, collect(o.purchased_date)[0..5] as sample_dates
    """)
    print(f"HashiCorp deals: {hashicorp_check}")

if __name__ == "__main__":
    test_hashicorp_2025_deals()