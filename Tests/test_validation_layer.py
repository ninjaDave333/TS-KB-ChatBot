#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.query_validator import CypherValidator

def test_validation_layer():
    validator = CypherValidator()
    
    print("=== Testing Query Validation Layer ===")
    
    # Test cases with common issues
    test_cases = [
        {
            "name": "Trailing comma",
            "query": "MATCH (c:Client) RETURN count(c) as total,",
            "expected_fix": True
        },
        {
            "name": "Variable mismatch",
            "query": "WITH collect(c) as clients RETURN total, samples",
            "expected_fix": True
        },
        {
            "name": "Wrong date field",
            "query": "MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product) RETURN o.close_date",
            "expected_fix": True
        },
        {
            "name": "LOCATED_IN pattern",
            "query": "MATCH (c:Client)-[:LOCATED_IN]->(r:Region) WHERE r.name = 'IL' RETURN c.sf_name",
            "expected_fix": True
        },
        {
            "name": "APOC function",
            "query": "RETURN apoc.coll.randomItems([1,2,3], 2)",
            "expected_fix": False
        },
        {
            "name": "Valid query",
            "query": "MATCH (c:Client) WHERE c.region = 'IL' RETURN c.sf_name",
            "expected_fix": True
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test['name']} ---")
        print(f"Original: {test['query']}")
        
        is_valid, fixed_query, issues = validator.validate_and_fix(test['query'])
        
        print(f"Valid: {is_valid}")
        print(f"Fixed: {fixed_query}")
        print(f"Issues: {issues}")
        
        if is_valid == test['expected_fix']:
            print("✅ Test passed")
        else:
            print("❌ Test failed")

if __name__ == "__main__":
    test_validation_layer()