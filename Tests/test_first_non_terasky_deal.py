#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database.neo4j_client import Neo4jClient

def test_first_deal():
    client = Neo4jClient()
    
    print("=== First Non-TeraSky Deal ===\n")
    
    result = client.execute_query("""
        MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
        WHERE o.opportunity_stage = 'Closed Won'
        AND NOT toLower(p.vendor) CONTAINS 'terasky'
        WITH o.close_date as date, c.sf_name as client, p.name as product, p.vendor as vendor
        ORDER BY date ASC
        LIMIT 1
        RETURN substring(date, 0, 4) as year, client, product, vendor, date
    """)
    
    if result:
        deal = result[0]
        print(f"Year: {deal['year']}")
        print(f"Client: {deal['client']}")
        print(f"Product: {deal['product']}")
        print(f"Vendor: {deal['vendor']}")
        print(f"Close Date: {deal['date']}")

if __name__ == "__main__":
    test_first_deal()
