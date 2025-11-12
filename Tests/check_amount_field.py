#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database.neo4j_client import Neo4jClient

def check_amount_field():
    client = Neo4jClient()
    
    print("=== Checking OPPORTUNITY Amount Field ===\n")
    
    # Get all properties of OPPORTUNITY relationships
    props = client.execute_query("""
        MATCH ()-[o:OPPORTUNITY]->()
        WITH o LIMIT 1
        RETURN keys(o) as properties
    """)
    print(f"OPPORTUNITY properties: {props[0]['properties']}\n")
    
    # Sample 10 deals with all amount-related fields
    deals = client.execute_query("""
        MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
        WHERE o.opportunity_stage = 'Closed Won'
        RETURN c.sf_name as client,
               p.name as product,
               o.amount as amount,
               o.purchased_date as date
        LIMIT 10
    """)
    
    print(f"Sample of 10 Closed Won deals:\n")
    for i, deal in enumerate(deals, 1):
        print(f"{i}. {deal['client']} - {deal['product']}")
        print(f"   Amount: {deal['amount']} (type: {type(deal['amount']).__name__})")
        print(f"   Date: {deal['date']}\n")
    
    # Count deals with/without amount
    stats = client.execute_query("""
        MATCH ()-[o:OPPORTUNITY]->()
        WHERE o.opportunity_stage = 'Closed Won'
        WITH count(o) as total,
             sum(CASE WHEN o.amount IS NOT NULL THEN 1 ELSE 0 END) as with_amount,
             sum(CASE WHEN o.amount IS NULL THEN 1 ELSE 0 END) as without_amount
        RETURN total, with_amount, without_amount
    """)
    
    print(f"{'='*60}")
    print(f"Closed Won deals statistics:")
    print(f"  Total: {stats[0]['total']}")
    print(f"  With amount: {stats[0]['with_amount']}")
    print(f"  Without amount: {stats[0]['without_amount']}")

if __name__ == "__main__":
    check_amount_field()
