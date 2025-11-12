#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database.neo4j_client import Neo4jClient

def debug_israel_clients():
    client = Neo4jClient()
    
    print("=== Debugging Israel Clients Query ===")
    
    # 1. Check what regions exist
    print("\n1. Available regions:")
    regions = client.execute_query("MATCH (r:Region) RETURN r.name, r.code LIMIT 10")
    for region in regions:
        print(f"  - {region}")
    
    # 2. Check client properties for location info
    print("\n2. Client location properties:")
    client_props = client.execute_query("""
        MATCH (c:Client) 
        WHERE c.sf_billing_country IS NOT NULL OR c.region IS NOT NULL
        RETURN c.sf_name, c.sf_billing_country, c.region 
        LIMIT 10
    """)
    for client in client_props:
        print(f"  - {client}")
    
    # 3. Check if LOCATED_IN relationships exist
    print("\n3. LOCATED_IN relationships:")
    located_in = client.execute_query("""
        MATCH (c:Client)-[:LOCATED_IN]->(r:Region) 
        RETURN c.sf_name, r.name 
        LIMIT 5
    """)
    print(f"Found {len(located_in)} LOCATED_IN relationships")
    for rel in located_in:
        print(f"  - {rel}")
    
    # 4. Look for Israel-related clients by country
    print("\n4. Clients with Israel-related country:")
    israel_clients = client.execute_query("""
        MATCH (c:Client) 
        WHERE toLower(c.sf_billing_country) CONTAINS 'israel' 
           OR toLower(c.sf_billing_country) CONTAINS 'il'
           OR c.sf_billing_country = 'IL'
        RETURN c.sf_name, c.sf_billing_country, c.sf_account_status
        LIMIT 10
    """)
    print(f"Found {len(israel_clients)} Israel clients by country")
    for client in israel_clients:
        print(f"  - {client}")
    
    # 5. Check active status field
    print("\n5. Client active status fields:")
    active_fields = client.execute_query("""
        MATCH (c:Client) 
        WHERE c.sf_account_status IS NOT NULL
        RETURN DISTINCT c.sf_account_status
        LIMIT 10
    """)
    print("Available account statuses:")
    for status in active_fields:
        print(f"  - {status}")

if __name__ == "__main__":
    debug_israel_clients()