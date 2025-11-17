#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.answer_generator import AnswerGenerator

def test_hashicorp_answer():
    """Test HashiCorp answer generation"""
    
    generator = AnswerGenerator()
    
    # Test data from actual API response
    user_query = "How many HashiCorp products were purchased in 2025?"
    cypher_query = "MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product) WHERE toLower(p.name) CONTAINS 'hashicorp' AND o.opportunity_stage = 'Closed Won' AND o.close_date >= '2025-01-01' AND o.close_date < '2026-01-01' AND toLower(p.vendor) CONTAINS 'hashicorp' RETURN count(p) as hashicorp_products_purchased"
    data = [{"hashicorp_products_purchased": 8}]
    
    # Generate answer
    answer = generator.generate_answer(user_query, cypher_query, data)
    
    print("=== Answer Generation Test ===")
    print(f"Query: {user_query}")
    print(f"Data: {data}")
    print(f"Generated Answer: {answer}")
    print()
    
    # Expected: "In 2025, 8 HashiCorp products were purchased across various clients."
    expected_keywords = ["2025", "8", "HashiCorp", "products", "purchased"]
    
    success = all(keyword.lower() in answer.lower() for keyword in expected_keywords)
    
    if success:
        print("✅ Test PASSED - Answer contains all expected information")
    else:
        print("❌ Test FAILED - Answer missing key information")
        missing = [kw for kw in expected_keywords if kw.lower() not in answer.lower()]
        print(f"Missing keywords: {missing}")
    
    return success

def test_other_queries():
    """Test other query types"""
    
    generator = AnswerGenerator()
    
    test_cases = [
        {
            "query": "How many successful deals were conducted during 2025?",
            "data": [{"successful_deals_2025": 156}],
            "expected": ["2025", "156", "deals"]
        },
        {
            "query": "List 5 clients in Israel",
            "data": [
                {"sf_name": "Tufin", "account_manager": "Sarah Cohen"},
                {"sf_name": "Wix", "account_manager": "David Levy"}
            ],
            "expected": ["Tufin", "Wix"]
        }
    ]
    
    print("=== Additional Tests ===")
    
    for i, case in enumerate(test_cases, 1):
        answer = generator.generate_answer(case["query"], "", case["data"])
        print(f"Test {i}: {case['query']}")
        print(f"Answer: {answer}")
        
        success = all(keyword in answer for keyword in case["expected"])
        print(f"Status: {'✅ PASSED' if success else '❌ FAILED'}")
        print()

if __name__ == "__main__":
    print("Testing Answer Generation Fix for Context Recall Issue")
    print("=" * 60)
    
    # Test HashiCorp query specifically
    hashicorp_success = test_hashicorp_answer()
    
    # Test other queries
    test_other_queries()
    
    print("=" * 60)
    if hashicorp_success:
        print("🎉 HashiCorp answer generation FIXED!")
        print("Next: Restart API server and run RAGAS evaluation")
    else:
        print("⚠️  HashiCorp answer generation needs more work")