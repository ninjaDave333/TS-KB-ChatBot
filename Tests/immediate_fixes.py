#!/usr/bin/env python3
"""
Immediate fixes for production issues identified from trace analysis
"""

# 1. Add input validation for invalid queries
def validate_user_input(question: str) -> bool:
    """Reject obviously invalid inputs"""
    invalid_patterns = [
        'crap', '!', 'test', 'hello', 'hi', 'what', 'how are you'
    ]
    
    if len(question.strip()) < 5:
        return False
        
    if any(pattern in question.lower() for pattern in invalid_patterns):
        return False
        
    return True

# 2. Enhanced intent classification keywords
ENHANCED_KEYWORDS = {
    'calendar_v1': [
        'calendarevent', 'starttime', 'duration', 'owner', 'meeting', 'recording'
    ],
    'product_v1': [
        'backstage', 'product', 'vendor', 'installed', 'region'
    ],
    'sales_v1': [
        'opportunity', 'opportunity_stage', 'opportunities', 'pipeline', 'closed won'
    ]
}

# 3. Query relaxation for low data returns
def relax_date_constraints(cypher: str) -> str:
    """Remove restrictive date filters for broader results"""
    
    # Remove specific year constraints
    if "2025" in cypher:
        cypher = cypher.replace("AND o.close_date >= '2025-01-01'", "")
        cypher = cypher.replace("WHERE o.close_date >= '2025-01-01'", "WHERE 1=1")
    
    # Remove specific stage constraints for broader results
    if "opportunity_stage = 'Closed Won'" in cypher:
        cypher = cypher.replace("opportunity_stage = 'Closed Won'", "opportunity_stage IN ['Closed Won', 'Pipeline', 'Proposal']")
    
    return cypher

# 4. Better error messages for empty results
def generate_helpful_message(intent: str, question: str) -> str:
    """Generate helpful messages for empty results"""
    
    if "2025" in question:
        return "No data found for 2025. Try 2023 or 2024 instead."
    
    if intent == "vendor" and "backstage" in question.lower():
        return "No 'backstage' products found. Try 'HashiCorp', 'AWS', or 'Microsoft'."
    
    if intent == "general" and "calendarevent" in question.lower():
        return "Try asking about 'meetings' or 'recordings' instead of 'calendarevent'."
    
    return "No results found. Try broadening your search criteria."

print("Immediate fixes identified:")
print("1. Input validation for invalid queries")
print("2. Enhanced intent classification keywords") 
print("3. Query relaxation for low data returns")
print("4. Better error messages for empty results")