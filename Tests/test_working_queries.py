"""
Test working Teams Recording queries with actual data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.neo4j_client import Neo4jClient

def test_working_queries():
    """Test the 5 required queries with working patterns."""
    
    client = Neo4jClient()
    
    print("=== Working Teams Recording Queries ===\n")
    
    # Query 1: External meetings recorded (all time)
    print("1. External meetings recorded:")
    query1 = """
    MATCH (r:Recording)-[:LINKED_TO]->(c:CalendarEvent)
    WHERE size(c.externalParticipants) > 0
    RETURN count(r) as external_meetings_recorded
    """
    
    try:
        result1 = client.execute_query(query1)
        count = result1[0]['external_meetings_recorded']
        print(f"   Result: {count} external meetings recorded")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Query 2: David Gidony's meetings breakdown
    print("\n2. David Gidony's recorded meetings breakdown:")
    query2 = """
    MATCH (e:Employee)-[:OWNER_OF]->(c:CalendarEvent)<-[:LINKED_TO]-(r:Recording)
    WHERE toLower(e.name) CONTAINS 'david gidony'
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
            print(f"   Result: Total: {total}, Internal: {internal}, External: {external}")
        else:
            print("   Result: No meetings found")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Query 3: Most active employee (all time)
    print("\n3. Most active employee meeting wise:")
    query3 = """
    MATCH (e:Employee)-[rel:OWNER_OF|INVITED_TO]->(c:CalendarEvent)
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
            print(f"   Result: {name} ({total} total: {owned} owned, {participated} participated)")
        else:
            print("   Result: No meeting data found")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Query 4: Top 3 clients with most recorded meetings
    print("\n4. Top 3 clients with most recorded meetings:")
    query4 = """
    MATCH (c:Client)-[:MANAGED_BY]->(e:Employee)-[:OWNER_OF|INVITED_TO]->(ce:CalendarEvent)<-[:LINKED_TO]-(r:Recording)
    WITH c, count(DISTINCT r) as recorded_meetings, collect(DISTINCT ce.title)[0..3] as sample_subjects
    RETURN c.sf_name as client_name, recorded_meetings, sample_subjects
    ORDER BY recorded_meetings DESC LIMIT 3
    """
    
    try:
        result4 = client.execute_query(query4)
        if result4:
            print("   Results:")
            for i, row in enumerate(result4, 1):
                client_name = row['client_name']
                meetings = row['recorded_meetings']
                subjects = row['sample_subjects']
                print(f"      {i}. {client_name}: {meetings} meetings")
                if subjects:
                    print(f"         Subjects: {', '.join(subjects)}")
        else:
            print("   Result: No client meeting data found")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Query 5: Employee meeting breakdown (any employee with meetings)
    print("\n5. Employee meeting breakdown (top employee):")
    query5 = """
    MATCH (e:Employee)-[:OWNER_OF]->(c:CalendarEvent)<-[:LINKED_TO]-(r:Recording)
    WITH e, c, r
    WITH e, 
         count(r) as total_recorded_meetings,
         sum(CASE WHEN size(c.externalParticipants) = 0 THEN 1 ELSE 0 END) as internal_meetings,
         sum(CASE WHEN size(c.externalParticipants) > 0 THEN 1 ELSE 0 END) as external_meetings
    WHERE total_recorded_meetings > 0
    RETURN e.name, total_recorded_meetings, internal_meetings, external_meetings
    ORDER BY total_recorded_meetings DESC LIMIT 1
    """
    
    try:
        result5 = client.execute_query(query5)
        if result5:
            name = result5[0]['e.name']
            total = result5[0]['total_recorded_meetings']
            internal = result5[0]['internal_meetings']
            external = result5[0]['external_meetings']
            print(f"   Result: {name} had {total} recorded meetings: {internal} internal, {external} external")
        else:
            print("   Result: No employee meeting data found")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n=== All Queries Complete ===")

if __name__ == "__main__":
    test_working_queries()