#!/usr/bin/env python3
"""
Check Teams Recording Data Range
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.neo4j_client import Neo4jClient

def check_data_range():
    """Check the actual date range of Teams Recording data"""
    
    neo4j = Neo4jClient()
    
    queries = [
        # Check CalendarEvent date range
        "MATCH (c:CalendarEvent) RETURN min(c.startTime) as min_date, max(c.startTime) as max_date, count(c) as total_events",
        
        # Check Recording date range  
        "MATCH (r:Recording) RETURN min(r.createdDateTime) as min_date, max(r.createdDateTime) as max_date, count(r) as total_recordings",
        
        # Check external meetings
        "MATCH (c:CalendarEvent) WHERE size(c.externalParticipants) > 0 RETURN count(c) as external_meetings",
        
        # Check employees with meetings
        "MATCH (e:Employee)-[rel:OWNER_OF|INVITED_TO]->(c:CalendarEvent) RETURN e.name as employee, count(rel) as meeting_count ORDER BY meeting_count DESC LIMIT 5",
        
        # Check David Gidony specifically
        "MATCH (e:Employee {name: 'David Gidony'})-[rel:OWNER_OF|INVITED_TO]->(c:CalendarEvent) RETURN count(rel) as david_meetings"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n=== Query {i}: {query} ===")
        try:
            result = neo4j.execute_query(query)
            print(f"Results: {result}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_data_range()