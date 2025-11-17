#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app.database.neo4j_client import Neo4jClient

c = Neo4jClient()
r = c.execute_query("""
    MATCH (cl:Client)-[o:OPPORTUNITY]->(p:Product)
    WHERE p.name = 'AWS EDP Year 1'
    AND o.opportunity_stage = 'Closed Won' 
    AND o.close_date >= '2025-01-01'
    RETURN cl.sf_name as client,
           cl.sf_owner_email as owner_email, 
           cl.sf_owner_id as owner_id, 
           cl.sf_account_manager_cloud_id as am_id
    LIMIT 3
""")
for row in r:
    print(f"Client: {row['client']}")
    print(f"  Owner Email: {row['owner_email']}")
    print(f"  Owner ID: {row['owner_id']}")
    print(f"  AM Cloud ID: {row['am_id']}\n")
