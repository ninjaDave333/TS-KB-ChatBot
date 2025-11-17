"""
Check actual data distribution in Teams Recording.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.neo4j_client import Neo4jClient

def check_data():
    """Check actual data distribution."""
    
    client = Neo4jClient()
    
    print("=== Data Distribution Check ===\n")
    
    # Basic counts
    print("1. Basic counts:")
    queries = [
        ("Recordings", "MATCH (r:Recording) RETURN count(r) as count"),
        ("Calendar Events", "MATCH (c:CalendarEvent) RETURN count(c) as count"),
        ("Linked Recordings", "MATCH (r:Recording)-[:LINKED_TO]->(c:CalendarEvent) RETURN count(r) as count"),
        ("External Meetings", "MATCH (c:CalendarEvent) WHERE size(c.externalParticipants) > 0 RETURN count(c) as count"),
        ("Employee Owners", "MATCH (e:Employee)-[:OWNER_OF]->(c:CalendarEvent) RETURN count(DISTINCT e) as count"),
        ("Employee Participants", "MATCH (e:Employee)-[:INVITED_TO]->(c:CalendarEvent) RETURN count(DISTINCT e) as count")
    ]
    
    for name, query in queries:
        try:
            result = client.execute_query(query)
            count = result[0]['count'] if result else 0
            print(f"   {name}: {count}")
        except Exception as e:
            print(f"   {name}: ERROR - {e}")
    
    # Sample data
    print("\n2. Sample recordings with meetings:")
    sample_query = """
    MATCH (r:Recording)-[:LINKED_TO]->(c:CalendarEvent)
    RETURN r.name, r.createdDateTime, c.title, c.startTime, size(c.externalParticipants) as external_count
    ORDER BY r.createdDateTime DESC LIMIT 5
    """
    
    try:
        results = client.execute_query(sample_query)
        for row in results:
            name = row['r.name'][:50] + "..." if len(row['r.name']) > 50 else row['r.name']
            created = str(row['r.createdDateTime'])[:10]
            title = row['c.title'][:30] + "..." if len(row['c.title']) > 30 else row['c.title']
            start = str(row['c.startTime'])[:10]
            external = row['external_count']
            print(f"   {name} | {created} | {title} | {start} | Ext: {external}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Employee activity sample
    print("\n3. Employee activity sample:")
    employee_query = """
    MATCH (e:Employee)-[rel:OWNER_OF|INVITED_TO]->(c:CalendarEvent)
    WITH e, count(DISTINCT c) as total_meetings,
         sum(CASE WHEN type(rel) = 'OWNER_OF' THEN 1 ELSE 0 END) as owned_meetings
    WHERE total_meetings > 0
    RETURN e.name, total_meetings, owned_meetings
    ORDER BY total_meetings DESC LIMIT 5
    """
    
    try:
        results = client.execute_query(employee_query)
        for row in results:
            name = row['e.name']
            total = row['total_meetings']
            owned = row['owned_meetings']
            print(f"   {name}: {total} total ({owned} owned)")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test working query patterns
    print("\n4. Working query test:")
    
    # Simple external meeting count (all time)
    ext_query = """
    MATCH (r:Recording)-[:LINKED_TO]->(c:CalendarEvent)
    WHERE size(c.externalParticipants) > 0
    RETURN count(r) as external_recordings
    """
    
    try:
        result = client.execute_query(ext_query)
        count = result[0]['external_recordings'] if result else 0
        print(f"   Total external recordings: {count}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Most active employee (all time)
    active_query = """
    MATCH (e:Employee)-[rel:OWNER_OF|INVITED_TO]->(c:CalendarEvent)
    WITH e, count(DISTINCT c) as total_meetings,
         sum(CASE WHEN type(rel) = 'OWNER_OF' THEN 1 ELSE 0 END) as owned_meetings,
         sum(CASE WHEN type(rel) = 'INVITED_TO' THEN 1 ELSE 0 END) as participated_meetings
    RETURN e.name, total_meetings, owned_meetings, participated_meetings
    ORDER BY total_meetings DESC LIMIT 1
    """
    
    try:
        result = client.execute_query(active_query)
        if result:
            name = result[0]['e.name']
            total = result[0]['total_meetings']
            owned = result[0]['owned_meetings']
            participated = result[0]['participated_meetings']
            print(f"   Most active employee: {name} ({total} total: {owned} owned, {participated} participated)")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n=== Check Complete ===")

if __name__ == "__main__":
    check_data()