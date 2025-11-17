#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database.neo4j_client import Neo4jClient

def test_query():
    client = Neo4jClient()
    
    print("=== 2025 Top Selling Product & Account Manager ===\n")
    
    # Most selling product by revenue
    top_product = client.execute_query("""
        MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
        WHERE o.opportunity_stage = 'Closed Won' 
        AND o.close_date >= '2025-01-01' AND o.close_date < '2026-01-01'
        WITH p.name as product, sum(toFloat(o.total_price)) as total_revenue
        ORDER BY total_revenue DESC
        LIMIT 1
        RETURN product, total_revenue
    """)
    
    if top_product:
        product = top_product[0]['product']
        revenue = top_product[0]['total_revenue']
        print(f"Top Product: {product}")
        print(f"Total Revenue: ${revenue:,.2f}\n")
        
        # Top account manager for that product
        top_manager = client.execute_query("""
            MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product {name: $product})
            MATCH (c)-[:MANAGED_BY]->(e:Employee)
            WHERE o.opportunity_stage = 'Closed Won'
            AND o.close_date >= '2025-01-01' AND o.close_date < '2026-01-01'
            WITH e.name as manager, count(o) as deal_count, sum(toFloat(o.total_price)) as manager_revenue
            ORDER BY manager_revenue DESC
            LIMIT 1
            RETURN manager, deal_count, manager_revenue
        """, {"product": product})
        
        if top_manager:
            print(f"Top Account Manager: {top_manager[0]['manager']}")
            print(f"Deal Count: {top_manager[0]['deal_count']}")
            print(f"Manager Revenue: ${top_manager[0]['manager_revenue']:,.2f}")
        else:
            print("No account manager found for this product")

if __name__ == "__main__":
    test_query()
