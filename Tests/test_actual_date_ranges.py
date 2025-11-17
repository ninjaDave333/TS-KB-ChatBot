"""
Test actual date ranges in Teams Recording data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.neo4j_client import Neo4jClient

def test_actual_dates():
    """Test actual date ranges and adjust queries accordingly."""
    
    client = Neo4jClient()
    
    print("=== Actual Date Range Analysis ===\n")
    
    # Check recording date distribution
    print("1. Recording date distribution:")
    query1 = """
    MATCH (r:Recording)
    WITH substring(r.createdDateTime, 0, 7) as month, count(r) as recordings
    RETURN month, recordings
    ORDER BY month DESC
    """
    
    try:
        result1 = client.execute_query(query1)
        for row in result1[:10]:
            print(f"   {row['month']}: {row['recordings']} recordings")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Check meeting date distribution  
    print("\n2. Meeting date distribution:")
    query2 = """
    MATCH (c:CalendarEvent)
    WITH substring(c.startTime, 0, 7) as month, count(c) as meetings
    RETURN month, meetings
    ORDER BY month DESC
    """
    
    try:
        result2 = client.execute_query(query2)
        for row in result2[:10]:
            print(f"   {row['month']}: {row['meetings']} meetings")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test with recent date ranges (last 3 months)
    print("\n3. Testing with recent date ranges:")
    
    # External meetings in last 3 months
    query3 = """
    MATCH (r:Recording)-[:LINKED_TO]->(c:CalendarEvent)
    WHERE r.createdDateTime >= '2024-09-01T00:00:00Z'
    AND size(c.externalParticipants) > 0
    RETURN count(r) as external_meetings_recorded
    """
    
    try:
        result3 = client.execute_query(query3)
        count = result3[0]['external_meetings_recorded'] if result3 else 0
        print(f"   External meetings (Sep 2024+): {count}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Most active employee in recent months
    query4 = """
    MATCH (e:Employee)-[rel:OWNER_OF|INVITED_TO]->(c:CalendarEvent)
    WHERE c.startTime >= '2024-09-01T00:00:00Z'
    WITH e, count(DISTINCT c) as total_meetings,
         sum(CASE WHEN type(rel) = 'OWNER_OF' THEN 1 ELSE 0 END) as owned_meetings,
         sum(CASE WHEN type(rel) = 'INVITED_TO' THEN 1 ELSE 0 END) as participated_meetings
    RETURN e.name, total_meetings, owned_meetings, participated_meetings
    ORDER BY total_meetings DESC LIMIT 3
    """
    
    try:
        result4 = client.execute_query(query4)
        if result4:
            print("   Most active employees (Sep 2024+):")
            for i, row in enumerate(result4, 1):
                name = row['e.name']
                total = row['total_meetings']
                owned = row['owned_meetings']
                participated = row['participated_meetings']
                print(f"      {i}. {name}: {total} total ({owned} owned, {participated} participated)")
        else:
            print("   No recent employee activity found")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Client meetings via employees
    query5 = """
    MATCH (c:Client)-[:MANAGED_BY]->(e:Employee)-[:OWNER_OF|INVITED_TO]->(ce:CalendarEvent)<-[:LINKED_TO]-(r:Recording)
    WHERE r.createdDateTime >= '2024-09-01T00:00:00Z'
    WITH c, count(DISTINCT r) as recorded_meetings, collect(DISTINCT ce.title)[0..2] as sample_subjects
    RETURN c.sf_name as client_name, recorded_meetings, sample_subjects
    ORDER BY recorded_meetings DESC LIMIT 3
    """
    
    try:
        result5 = client.execute_query(query5)
        if result5:
            print("   Top clients with recorded meetings (Sep 2024+):")
            for i, row in enumerate(result5, 1):
                client_name = row['client_name']
                meetings = row['recorded_meetings']
                subjects = row['sample_subjects']
                print(f"      {i}. {client_name}: {meetings} meetings")
                if subjects:
                    print(f"         Subjects: {', '.join(subjects)}")
        else:
            print("   No client meeting data found")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    print("\n=== Analysis Complete ===")

if __name__ == "__main__":
    test_actual_dates()