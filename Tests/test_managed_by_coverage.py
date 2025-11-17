#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database.neo4j_client import Neo4jClient

def test_coverage():
    neo4j = Neo4jClient()
    
    print("=== MANAGED_BY Relationship Coverage ===\n")
    
    # Check which client has AWS EDP deals
    aws_clients = neo4j.execute_query("""
        MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product {name: 'AWS EDP Year 1'})
        WHERE o.opportunity_stage = 'Closed Won'
        AND o.close_date >= '2025-01-01' AND o.close_date < '2026-01-01'
        RETURN c.sf_name as client, c.sf_owner_email as owner_email
    """)
    
    print("Clients with AWS EDP Year 1 deals:")
    for client in aws_clients:
        print(f"  - {client['client']} (owner: {client['owner_email']})")
    
    # Check if they have MANAGED_BY
    if aws_clients:
        client_name = aws_clients[0]['client']
        managed = neo4j.execute_query("""
            MATCH (c:Client {sf_name: $name})-[:MANAGED_BY]->(e:Employee)
            RETURN e.name as manager, e.email as email
        """, {"name": client_name})
        
        print(f"\n{client_name} MANAGED_BY:")
        if managed:
            for m in managed:
                print(f"  - {m['manager']} ({m['email']})")
        else:
            print("  - NO MANAGED_BY relationship")

if __name__ == "__main__":
    test_coverage()
