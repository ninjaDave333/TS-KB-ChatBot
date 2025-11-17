"""
Validate Teams Recording schema against actual Neo4j database.
"""

from app.database.neo4j_client import Neo4jClient

def validate_recording_schema():
    """Validate the Teams Recording schema in Neo4j."""
    
    client = Neo4jClient()
    
    print("=== Teams Recording Schema Validation ===\n")
    
    # 1. Check node types
    print("1. Checking Node Types:")
    node_query = """
    CALL db.labels() YIELD label
    WHERE label IN ['Recording', 'CalendarEvent', 'ScanMetadata']
    RETURN label
    ORDER BY label
    """
    
    labels = client.execute_query(node_query)
    found_labels = [row['label'] for row in labels]
    expected_labels = ['Recording', 'CalendarEvent', 'ScanMetadata']
    
    for label in expected_labels:
        status = "✓" if label in found_labels else "✗"
        print(f"  {status} {label}")
    
    if not found_labels:
        print("  No Teams Recording nodes found in database")
        return
    
    # 2. Check node counts
    print("\n2. Node Counts:")
    for label in found_labels:
        count_query = f"MATCH (n:{label}) RETURN count(n) as count"
        result = client.execute_query(count_query)
        count = result[0]['count'] if result else 0
        print(f"  {label}: {count} nodes")
    
    # 3. Check Recording properties
    if 'Recording' in found_labels:
        print("\n3. Recording Node Properties:")
        props_query = """
        MATCH (r:Recording)
        WITH r LIMIT 1
        RETURN keys(r) as properties
        """
        result = client.execute_query(props_query)
        if result:
            props = result[0]['properties']
            expected_props = ['name', 'contentUrl', 'title', 'status', 'createdDateTime', 'sizeInBytes']
            
            for prop in expected_props:
                status = "✓" if prop in props else "✗"
                print(f"    {status} {prop}")
            
            print(f"    All properties: {props}")
    
    # 4. Check CalendarEvent properties
    if 'CalendarEvent' in found_labels:
        print("\n4. CalendarEvent Node Properties:")
        props_query = """
        MATCH (c:CalendarEvent)
        WITH c LIMIT 1
        RETURN keys(c) as properties
        """
        result = client.execute_query(props_query)
        if result:
            props = result[0]['properties']
            expected_props = ['name', 'subject', 'startTime', 'endTime', 'organizer']
            
            for prop in expected_props:
                status = "✓" if prop in props else "✗"
                print(f"    {status} {prop}")
            
            print(f"    All properties: {props}")
    
    # 5. Check relationships
    print("\n5. Relationship Types:")
    rel_query = """
    CALL db.relationshipTypes() YIELD relationshipType
    WHERE relationshipType IN ['LINKED_TO', 'OWNER_OF', 'INVITED_TO']
    RETURN relationshipType
    ORDER BY relationshipType
    """
    
    rels = client.execute_query(rel_query)
    found_rels = [row['relationshipType'] for row in rels]
    expected_rels = ['LINKED_TO', 'OWNER_OF', 'INVITED_TO']
    
    for rel in expected_rels:
        status = "✓" if rel in found_rels else "✗"
        print(f"  {status} {rel}")
    
    # 6. Check relationship patterns
    if found_rels:
        print("\n6. Relationship Patterns:")
        
        # LINKED_TO pattern
        if 'LINKED_TO' in found_rels:
            linked_query = """
            MATCH (r:Recording)-[:LINKED_TO]->(c:CalendarEvent)
            RETURN count(*) as count
            """
            result = client.execute_query(linked_query)
            count = result[0]['count'] if result else 0
            print(f"  Recording-[:LINKED_TO]->CalendarEvent: {count} relationships")
        
        # OWNER_OF pattern
        if 'OWNER_OF' in found_rels:
            owner_query = """
            MATCH (e:Employee)-[:OWNER_OF]->(c:CalendarEvent)
            RETURN count(*) as count
            """
            result = client.execute_query(owner_query)
            count = result[0]['count'] if result else 0
            print(f"  Employee-[:OWNER_OF]->CalendarEvent: {count} relationships")
        
        # INVITED_TO pattern
        if 'INVITED_TO' in found_rels:
            invited_query = """
            MATCH (e:Employee)-[:INVITED_TO]->(c:CalendarEvent)
            RETURN count(*) as count
            """
            result = client.execute_query(invited_query)
            count = result[0]['count'] if result else 0
            print(f"  Employee-[:INVITED_TO]->CalendarEvent: {count} relationships")
    
    # 7. Sample data
    print("\n7. Sample Data:")
    
    if 'Recording' in found_labels:
        sample_query = """
        MATCH (r:Recording)
        OPTIONAL MATCH (r)-[:LINKED_TO]->(c:CalendarEvent)
        RETURN r.name as recording, r.status as status, c.subject as meeting
        LIMIT 3
        """
        results = client.execute_query(sample_query)
        print("  Sample Recordings:")
        for row in results:
            print(f"    - {row['recording']} ({row['status']}) -> {row['meeting']}")
    
    # 8. Employee integration check
    print("\n8. Employee Integration:")
    employee_check = """
    MATCH (e:Employee)-[:OWNER_OF|INVITED_TO]->(c:CalendarEvent)
    RETURN count(DISTINCT e) as employees_with_meetings
    """
    result = client.execute_query(employee_check)
    if result:
        count = result[0]['employees_with_meetings']
        print(f"  Employees linked to meetings: {count}")
    
    print("\n=== Validation Complete ===")

if __name__ == "__main__":
    validate_recording_schema()