"""
Test Teams Recording queries with 2024 date ranges.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.neo4j_client import Neo4jClient

def test_2024_queries():
    """Test the 5 required queries with 2024 date ranges."""
    
    client = Neo4jClient()
    
    print("=== Teams Recording 2024 Queries Test ===\n")
    
    # Query 1: External meetings recorded during 2024
    print("1. External meetings recorded during 2024:")
    query1 = """
    MATCH (r:Recording)-[:LINKED_TO]->(c:CalendarEvent)
    WHERE r.createdDateTime >= '2024-01-01T00:00:00Z' 
    AND r.createdDateTime < '2025-01-01T00:00:00Z'
    AND size(c.externalParticipants) > 0
    RETURN count(r) as external_meetings_recorded
    """
    
    try:
        result1 = client.execute_query(query1)
        count = result1[0]['external_meetings_recorded'] if result1 else 0
        print(f"   ✓ {count} external meetings recorded in 2024")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Query 2: David's meetings breakdown (flexible name matching)
    print("\n2. Employee meeting breakdown (David):")
    query2 = """
    MATCH (e:Employee)-[:OWNER_OF]->(c:CalendarEvent)<-[:LINKED_TO]-(r:Recording)
    WHERE toLower(e.name) CONTAINS 'david'
    AND r.createdDateTime >= '2024-01-01T00:00:00Z' 
    AND r.createdDateTime < '2025-01-01T00:00:00Z'
    WITH c, r
    RETURN 
      count(r) as total_recorded_meetings,
      sum(CASE WHEN size(c.externalParticipants) = 0 THEN 1 ELSE 0 END) as internal_meetings,
      sum(CASE WHEN size(c.externalParticipants) > 0 THEN 1 ELSE 0 END) as external_meetings
    """
    
    try:
        result2 = client.execute_query(query2)
        if result2:
            total = result2[0]['total_recorded_meetings']
            internal = result2[0]['internal_meetings']
            external = result2[0]['external_meetings']
            print(f"   ✓ Total: {total}, Internal: {internal}, External: {external}")
        else:
            print("   ✓ No meetings found for David")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Query 3: Most active employee in 2024
    print("\n3. Most active employee in 2024:")
    query3 = """
    MATCH (e:Employee)-[rel:OWNER_OF|INVITED_TO]->(c:CalendarEvent)
    WHERE c.startTime >= '2024-01-01T00:00:00Z' 
    AND c.startTime < '2025-01-01T00:00:00Z'
    WITH e, count(DISTINCT c) as total_meetings,
         sum(CASE WHEN type(rel) = 'OWNER_OF' THEN 1 ELSE 0 END) as owned_meetings,
         sum(CASE WHEN type(rel) = 'INVITED_TO' THEN 1 ELSE 0 END) as participated_meetings
    RETURN e.name, total_meetings, owned_meetings, participated_meetings
    ORDER BY total_meetings DESC LIMIT 1
    """
    
    try:
        result3 = client.execute_query(query3)
        if result3:
            name = result3[0]['e.name']
            total = result3[0]['total_meetings']
            owned = result3[0]['owned_meetings']
            participated = result3[0]['participated_meetings']
            print(f"   ✓ Most active: {name} ({total} total: {owned} owned, {participated} participated)")
        else:
            print("   ✓ No 2024 meeting data found")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Query 4: Most active employee in July 2024
    print("\n4. Most active employee in July 2024:")
    query4 = """
    MATCH (e:Employee)-[rel:OWNER_OF|INVITED_TO]->(c:CalendarEvent)
    WHERE c.startTime >= '2024-07-01T00:00:00Z' 
    AND c.startTime < '2024-08-01T00:00:00Z'
    WITH e, count(DISTINCT c) as total_meetings,
         sum(CASE WHEN type(rel) = 'OWNER_OF' THEN 1 ELSE 0 END) as owned_meetings,
         sum(CASE WHEN type(rel) = 'INVITED_TO' THEN 1 ELSE 0 END) as participated_meetings
    RETURN e.name, total_meetings, owned_meetings, participated_meetings
    ORDER BY total_meetings DESC LIMIT 1
    """
    
    try:
        result4 = client.execute_query(query4)
        if result4:
            name = result4[0]['e.name']
            total = result4[0]['total_meetings']
            owned = result4[0]['owned_meetings']
            participated = result4[0]['participated_meetings']
            print(f"   ✓ Most active in July 2024: {name} ({total} total: {owned} owned, {participated} participated)")
        else:
            print("   ✓ No July 2024 meeting data found")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Query 5: Top 3 clients with most recorded meetings in 2024
    print("\n5. Top 3 clients with most recorded meetings in 2024:")
    query5 = """
    MATCH (c:Client)-[:MANAGED_BY]->(e:Employee)-[:OWNER_OF|INVITED_TO]->(ce:CalendarEvent)<-[:LINKED_TO]-(r:Recording)
    WHERE r.createdDateTime >= '2024-01-01T00:00:00Z' 
    AND r.createdDateTime < '2025-01-01T00:00:00Z'
    WITH c, count(DISTINCT r) as recorded_meetings, collect(DISTINCT ce.title)[0..3] as sample_subjects
    RETURN c.sf_name as client_name, recorded_meetings, sample_subjects
    ORDER BY recorded_meetings DESC LIMIT 3
    """
    
    try:
        result5 = client.execute_query(query5)
        if result5:
            print("   ✓ Top 3 clients:")
            for i, row in enumerate(result5, 1):
                client_name = row['client_name']
                meetings = row['recorded_meetings']
                subjects = row['sample_subjects']
                print(f"      {i}. {client_name}: {meetings} meetings")
                if subjects:
                    print(f"         Subjects: {', '.join(subjects)}")
        else:
            print("   ✓ No client meeting data found")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n=== 2024 Test Complete ===")

if __name__ == "__main__":
    test_2024_queries()