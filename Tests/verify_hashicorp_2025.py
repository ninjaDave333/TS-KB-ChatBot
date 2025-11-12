#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database.neo4j_client import Neo4jClient

def verify_hashicorp_2025():
    client = Neo4jClient()
    
    print("=== Verifying HashiCorp 2025 Deals ===\n")
    
    # 1. Check all 2025 deals
    print("1. All 2025 deals:")
    all_2025 = client.execute_query("""
        MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
        WHERE o.opportunity_stage = 'Closed Won' 
          AND o.purchased_date CONTAINS '2025'
        RETURN count(o) as total, collect(DISTINCT p.name)[0..10] as products
    """)
    print(f"   Total 2025 deals: {all_2025[0]['total']}")
    print(f"   Products: {all_2025[0]['products']}\n")
    
    # 2. Check HashiCorp products
    print("2. HashiCorp products in system:")
    hashicorp_products = client.execute_query("""
        MATCH (p:Product)
        WHERE toLower(p.name) CONTAINS 'hashicorp' 
           OR toLower(p.vendor) CONTAINS 'hashicorp'
        RETURN p.name, p.vendor
    """)
    print(f"   Found {len(hashicorp_products)} HashiCorp products:")
    for prod in hashicorp_products:
        print(f"     - {prod}\n")
    
    # 3. Check HashiCorp deals (any year)
    print("3. HashiCorp deals (any year):")
    hashicorp_deals = client.execute_query("""
        MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
        WHERE (toLower(p.name) CONTAINS 'hashicorp' OR toLower(p.vendor) CONTAINS 'hashicorp')
          AND o.opportunity_stage = 'Closed Won'
        RETURN c.sf_name, p.name, o.purchased_date
        ORDER BY o.purchased_date DESC
        LIMIT 10
    """)
    print(f"   Found {len(hashicorp_deals)} HashiCorp deals:")
    for deal in hashicorp_deals:
        print(f"     - {deal}\n")
    
    # 4. Check HashiCorp 2025 deals with different filters
    print("4. HashiCorp 2025 deals (trying different filters):")
    
    # Try with p.name
    query1 = client.execute_query("""
        MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
        WHERE toLower(p.name) CONTAINS 'hashicorp'
          AND o.opportunity_stage = 'Closed Won'
          AND o.purchased_date CONTAINS '2025'
        RETURN count(o) as total
    """)
    print(f"   By p.name: {query1[0]['total']} deals")
    
    # Try with p.vendor
    query2 = client.execute_query("""
        MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
        WHERE toLower(p.vendor) CONTAINS 'hashicorp'
          AND o.opportunity_stage = 'Closed Won'
          AND o.purchased_date CONTAINS '2025'
        RETURN count(o) as total
    """)
    print(f"   By p.vendor: {query2[0]['total']} deals")
    
    # Try with both
    query3 = client.execute_query("""
        MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
        WHERE (toLower(p.name) CONTAINS 'hashicorp' OR toLower(p.vendor) CONTAINS 'hashicorp')
          AND o.opportunity_stage = 'Closed Won'
          AND o.purchased_date CONTAINS '2025'
        RETURN c.sf_name, p.name, p.vendor, o.purchased_date
    """)
    print(f"   By both: {len(query3)} deals")
    if query3:
        for deal in query3:
            print(f"     - {deal}")

if __name__ == "__main__":
    verify_hashicorp_2025()