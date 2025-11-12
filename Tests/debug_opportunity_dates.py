#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database.neo4j_client import Neo4jClient

def debug_opportunity_dates():
    client = Neo4jClient()
    
    print("=== Debugging OPPORTUNITY Date Fields ===")
    
    # 1. Check OPPORTUNITY relationship properties
    print("\n1. OPPORTUNITY relationship properties:")
    opp_props = client.execute_query("""
        MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
        WHERE o.opportunity_stage = 'Closed Won'
        RETURN keys(o) as properties
        LIMIT 1
    """)
    print(f"Available properties: {opp_props}")
    
    # 2. Check actual date field names
    print("\n2. Sample OPPORTUNITY with all properties:")
    sample_opp = client.execute_query("""
        MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
        WHERE o.opportunity_stage = 'Closed Won'
        RETURN o
        LIMIT 3
    """)
    for i, opp in enumerate(sample_opp):
        print(f"  Sample {i+1}: {opp}")
    
    # 3. Check for date-related fields
    print("\n3. Date-related fields in OPPORTUNITY:")
    date_fields = client.execute_query("""
        MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
        WHERE o.opportunity_stage = 'Closed Won'
        RETURN o.close_date, o.purchased_date, o.created_date, o.modified_date
        LIMIT 5
    """)
    for i, dates in enumerate(date_fields):
        print(f"  Record {i+1}: {dates}")
    
    # 4. Check 2025 filtering
    print("\n4. Testing 2025 date filtering:")
    year_2025 = client.execute_query("""
        MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
        WHERE o.opportunity_stage = 'Closed Won' 
          AND o.purchased_date IS NOT NULL
          AND o.purchased_date CONTAINS '2025'
        RETURN count(o) as total_2025, o.purchased_date
        LIMIT 5
    """)
    print(f"2025 opportunities: {year_2025}")

if __name__ == "__main__":
    debug_opportunity_dates()