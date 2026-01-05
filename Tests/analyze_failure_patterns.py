#!/usr/bin/env python3
"""
Analysis of Failed General Queries - Root Cause & Solutions
"""

# FAILED GENERAL QUERIES ANALYSIS
# ================================

FAILED_QUERIES = [
    "I cannot generate a Cypher query from \"crap !\" as it doesn't contain any specific data requirements",
    "MATCH (ce:CalendarEvent {id: '123'}) RETURN ce.owner",
    "MATCH (c:Client)-[:HAS_INSTALLED]->(p:Product) WHERE c.region = 'East'",
    "MATCH (r:Recording)-[:LINKED_TO]->(ce:CalendarEvent) MATCH (e:Employee)-[:LOCATED_IN]->(reg:Region",
    "MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product) WHERE o.opportunity_stage = 'Closed Won' AND o.close_d",
    "MATCH (r:Recording) WHERE r.duration IS NOT NULL",
    "MATCH (ce:CalendarEvent) WHERE ce.startTime >= datetime('2025-01-01')",
    "MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product) WHERE o.opportunity_stage IN ['Closed Won', 'Closed Lo",
    "MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product) WHERE toLower(p.name) CONTAINS 'backstage'",
    "MATCH (r:Recording) WHERE r.subject_type = 'Other'"
]

def analyze_failure_patterns():
    print("FAILED GENERAL QUERIES - ROOT CAUSE ANALYSIS")
    print("=" * 60)
    
    # Pattern 1: Invalid/nonsense queries
    invalid_queries = [q for q in FAILED_QUERIES if "cannot generate" in q or "crap" in q]
    print(f"\nPATTERN 1: Invalid/Nonsense Queries ({len(invalid_queries)})")
    print("   Root Cause: User input validation needed")
    print("   Solution: Add input validation, suggest valid query types")
    
    # Pattern 2: Wrong field names/values
    wrong_fields = [q for q in FAILED_QUERIES if any(field in q for field in ["id: '123'", "region = 'East'", "subject_type", "duration"])]
    print(f"\nPATTERN 2: Wrong Field Names/Values ({len(wrong_fields)})")
    print("   Root Cause: Using non-existent fields or values")
    print("   Issues found:")
    print("   - CalendarEvent.id (should use different identifier)")
    print("   - c.region = 'East' (valid regions: IL, US, UK)")
    print("   - r.duration, r.subject_type (fields don't exist)")
    print("   Solution: Better schema validation, field mapping")
    
    # Pattern 3: Misclassified queries (should be specific intents)
    misclassified = [q for q in FAILED_QUERIES if any(keyword in q for keyword in ["OPPORTUNITY", "Recording", "CalendarEvent"])]
    print(f"\nPATTERN 3: Misclassified Queries ({len(misclassified)})")
    print("   Root Cause: Should be classified as specific intents")
    print("   - OPPORTUNITY queries -> sales_v1 intent")
    print("   - Recording queries -> external_meeting_analytics intent") 
    print("   - CalendarEvent queries -> employee_activity_ranking intent")
    print("   Solution: Add missing keywords to intent classifier")
    
    # Pattern 4: Date/time queries
    date_queries = [q for q in FAILED_QUERIES if "datetime" in q or "2025" in q]
    print(f"\nPATTERN 4: Date/Time Queries ({len(date_queries)})")
    print("   Root Cause: Incorrect datetime syntax or date ranges")
    print("   Solution: Standardize date handling in prompts")

def generate_solutions():
    print("\n\nIMMEDIATE SOLUTIONS")
    print("=" * 60)
    
    print("\n1. ADD MISSING KEYWORDS TO INTENT CLASSIFIER")
    print("   File: app/core/prompt_profiles.py")
    print("   Add to classify_question_intent():")
    print("   - SALES_KEYWORDS += ['opportunity_stage', 'closed won', 'backstage']")
    print("   - CALENDAR_KEYWORDS += ['calendarevent', 'starttime', 'meeting title']")
    print("   - RECORDING_KEYWORDS += ['recording', 'duration', 'subject_type']")
    
    print("\n2. ADD INPUT VALIDATION")
    print("   File: app/core/bedrock_client.py")
    print("   Before generate_cypher():")
    print("   - Check for nonsense input (length < 3, only punctuation)")
    print("   - Suggest valid query types for invalid input")
    
    print("\n3. IMPROVE SCHEMA VALIDATION")
    print("   File: app/core/cypher_validator.py")
    print("   Add field validation:")
    print("   - Replace 'region = East' with 'region IN [IL, US, UK]'")
    print("   - Remove non-existent fields (duration, subject_type)")
    print("   - Fix CalendarEvent queries to use proper identifiers")
    
    print("\n4. ENHANCE GENERAL PROMPT")
    print("   File: app/core/prompt_profiles.py")
    print("   Add to general prompt:")
    print("   - Valid regions: IL, US, UK (not East, West, North, South)")
    print("   - CalendarEvent properties: title, startTime, endTime, owner")
    print("   - Recording properties: title, name, status, createdDateTime")

if __name__ == "__main__":
    analyze_failure_patterns()
    generate_solutions()