#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app.database.neo4j_client import Neo4jClient

c = Neo4jClient()
r = c.execute_query("""
    MATCH (cl:Client)-[o:OPPORTUNITY]->(p:Product)
    WHERE o.opportunity_stage = 'Closed Won'
    AND (toLower(p.vendor) CONTAINS 'hashicorp' OR toLower(p.name) CONTAINS 'hashicorp')
    AND o.close_date >= '2024-01-01' AND o.close_date < '2025-01-01'
    WITH cl.sf_name as client, 
         count(DISTINCT p) as product_count,
         count(o) as deal_count,
         sum(toFloat(o.total_price)) as total_spent
    ORDER BY product_count DESC, total_spent DESC
    LIMIT 5
    RETURN client, product_count, deal_count, total_spent
""")

print("Top 5 Clients by HashiCorp Products Purchased in 2024:\n")
for i, row in enumerate(r, 1):
    print(f"{i}. {row['client']}")
    print(f"   Products: {row['product_count']}")
    print(f"   Deals: {row['deal_count']}")
    print(f"   Total Spent: ${row['total_spent']:,.2f}\n")
