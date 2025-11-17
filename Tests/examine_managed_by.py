#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app.database.neo4j_client import Neo4jClient

c = Neo4jClient()

print("=== MANAGED_BY Relationship Analysis ===\n")

# Total MANAGED_BY relationships
total = c.execute_query("""
    MATCH (cl:Client)-[r:MANAGED_BY]->(e:Employee)
    RETURN count(r) as total
""")
print(f"Total MANAGED_BY relationships: {total[0]['total']}\n")

# Sample relationships
samples = c.execute_query("""
    MATCH (cl:Client)-[r:MANAGED_BY]->(e:Employee)
    RETURN cl.sf_name as client, 
           cl.sf_owner_email as client_owner_email,
           e.name as employee, 
           e.email as employee_email,
           e.sf_id as employee_sf_id
    LIMIT 5
""")

print("Sample MANAGED_BY relationships:")
for s in samples:
    print(f"  {s['client']} -> {s['employee']}")
    print(f"    Client owner email: {s['client_owner_email']}")
    print(f"    Employee email: {s['employee_email']}")
    print(f"    Employee SF ID: {s['employee_sf_id']}\n")

# Check relationship properties
props = c.execute_query("""
    MATCH (cl:Client)-[r:MANAGED_BY]->(e:Employee)
    WITH r LIMIT 1
    RETURN keys(r) as properties
""")
print(f"MANAGED_BY relationship properties: {props[0]['properties'] if props else 'None'}")
