#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database.neo4j_client import Neo4jClient

def check_total_price():
    client = Neo4jClient()
    
    print("=== Checking total_price Field ===\n")
    
    # Sample deals with total_price
    deals = client.execute_query("""
        MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
        WHERE o.opportunity_stage = 'Closed Won' AND o.total_price IS NOT NULL
        RETURN c.sf_name as client,
               p.name as product,
               o.total_price as cost,
               o.purchased_date as date
        ORDER BY o.total_price DESC
        LIMIT 10
    """)
    
    print(f"Top 10 deals by cost:\n")
    for i, deal in enumerate(deals, 1):
        print(f"{i}. {deal['client']} - ${deal['cost']:,.2f}")
        print(f"   Product: {deal['product']}")
        print(f"   Date: {deal['date']}\n")
    
    # Stats
    stats = client.execute_query("""
        MATCH ()-[o:OPPORTUNITY]->()
        WHERE o.opportunity_stage = 'Closed Won'
        WITH count(o) as total,
             sum(CASE WHEN o.total_price IS NOT NULL THEN 1 ELSE 0 END) as with_price,
             sum(toFloat(o.total_price)) as total_revenue
        RETURN total, with_price, total_revenue
    """)
    
    print(f"{'='*60}")
    print(f"Statistics:")
    print(f"  Total Closed Won: {stats[0]['total']}")
    print(f"  With total_price: {stats[0]['with_price']}")
    print(f"  Total Revenue: ${stats[0]['total_revenue']:,.2f}")

if __name__ == "__main__":
    check_total_price()
