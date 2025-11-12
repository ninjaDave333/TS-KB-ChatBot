#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database.neo4j_client import Neo4jClient

def check_vault_deals():
    client = Neo4jClient()
    
    print("=== Checking Vault Product Deals ===\n")
    
    # Get 20 newest Vault deals
    vault_deals = client.execute_query("""
        MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
        WHERE toLower(p.name) CONTAINS 'vault'
        RETURN c.sf_name as client, 
               p.name as product, 
               p.vendor as vendor,
               o.purchased_date as date,
               o.opportunity_stage as stage
        ORDER BY o.purchased_date DESC
        LIMIT 20
    """)
    
    print(f"Found {len(vault_deals)} Vault deals (20 newest):\n")
    
    for i, deal in enumerate(vault_deals, 1):
        print(f"{i}. {deal['client']}")
        print(f"   Product: {deal['product']}")
        print(f"   Vendor: {deal['vendor']}")
        print(f"   Date: {deal['date']}")
        print(f"   Stage: {deal['stage']}\n")
    
    # Check if any are in 2025
    deals_2025 = [d for d in vault_deals if '2025' in str(d['date'])]
    print(f"\n{'='*60}")
    print(f"Vault deals in 2025: {len(deals_2025)}")
    if deals_2025:
        for deal in deals_2025:
            print(f"  - {deal}")

if __name__ == "__main__":
    check_vault_deals()