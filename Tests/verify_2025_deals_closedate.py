#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database.neo4j_client import Neo4jClient

def verify_2025_deals():
    client = Neo4jClient()
    
    print("=== Verifying 2025 Deals with close_date ===\n")
    
    # Get all 2025 deals using close_date
    deals_2025 = client.execute_query("""
        MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
        WHERE o.opportunity_stage = 'Closed Won'
        AND o.close_date >= '2025-01-01' AND o.close_date < '2026-01-01'
        RETURN c.sf_name as client,
               p.name as product,
               p.vendor as vendor,
               o.close_date as close_date,
               o.total_price as value
        ORDER BY o.close_date DESC
    """)
    
    print(f"Total deals closed in 2025: {len(deals_2025)}\n")
    
    if deals_2025:
        total_revenue = sum(d['value'] or 0 for d in deals_2025)
        print(f"Total 2025 Revenue: ${total_revenue:,.2f}\n")
        
        for i, deal in enumerate(deals_2025, 1):
            print(f"{i}. {deal['client']}")
            print(f"   Product: {deal['product']}")
            print(f"   Vendor: {deal['vendor']}")
            print(f"   Close Date: {deal['close_date']}")
            print(f"   Value: ${deal['value']:,.2f}\n")
    
    # Check HashiCorp deals in 2025
    hc_deals = client.execute_query("""
        MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
        WHERE o.opportunity_stage = 'Closed Won'
        AND (toLower(p.vendor) CONTAINS 'hashicorp' OR toLower(p.name) CONTAINS 'hashicorp')
        AND o.close_date >= '2025-01-01' AND o.close_date < '2026-01-01'
        RETURN c.sf_name as client, p.name as product, o.close_date as close_date
    """)
    
    print(f"{'='*60}")
    print(f"HashiCorp deals closed in 2025: {len(hc_deals)}")
    if hc_deals:
        for deal in hc_deals:
            print(f"  - {deal['client']}: {deal['product']} ({deal['close_date']})")

if __name__ == "__main__":
    verify_2025_deals()
