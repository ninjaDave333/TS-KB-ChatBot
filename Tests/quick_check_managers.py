#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app.database.neo4j_client import Neo4jClient

c = Neo4jClient()
r = c.execute_query("""
    MATCH (cl:Client)-[o:OPPORTUNITY]->(p:Product)
    MATCH (cl)-[:MANAGED_BY]->(e:Employee)
    WHERE o.opportunity_stage = 'Closed Won' 
    AND o.close_date >= '2025-01-01' AND o.close_date < '2026-01-01'
    RETURN count(DISTINCT cl) as clients_with_managers, 
           count(DISTINCT e) as unique_managers, 
           count(o) as total_deals
""")
print(f"Clients with managers: {r[0]['clients_with_managers']}")
print(f"Unique managers: {r[0]['unique_managers']}")
print(f"Total deals: {r[0]['total_deals']}")
