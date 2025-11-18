#!/usr/bin/env python3
"""
Test Response Consistency Improvements
Tests the enhanced answer generation for consistent, user-friendly responses
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.answer_generator import AnswerGenerator

def test_count_responses():
    """Test enhanced count response formatting"""
    generator = AnswerGenerator()
    
    # Test failed opportunities response
    query1 = "how many failed opportunities were during 2025?"
    data1 = [{"failed_opportunities": 865}]
    result1 = generator.generate_answer(query1, "", data1)
    print(f"Query: {query1}")
    print(f"Result: {result1}")
    print()
    
    # Test external meetings response
    query2 = "How many external meetings recorded?"
    data2 = [{"external_meetings_recorded": 314}]
    result2 = generator.generate_answer(query2, "", data2)
    print(f"Query: {query2}")
    print(f"Result: {result2}")
    print()
    
    # Test field name conversion
    query3 = "how many clients in total?"
    data3 = [{"client_count": 42}]
    result3 = generator.generate_answer(query3, "", data3)
    print(f"Query: {query3}")
    print(f"Result: {result3}")
    print()

def test_multi_part_queries():
    """Test multi-part query handling"""
    generator = AnswerGenerator()
    
    # Test multi-part failed opportunities query
    query = "how many failed opportunities were during 2025 and what is the most popular failed product?"
    data = [
        {"product_name": "Product A", "failure_count": 25},
        {"product_name": "Product B", "failure_count": 18},
        {"product_name": "Product C", "failure_count": 12}
    ]
    result = generator.generate_answer(query, "", data)
    print(f"Query: {query}")
    print(f"Result: {result}")
    print()

def test_field_name_conversion():
    """Test field name to friendly name conversion"""
    generator = AnswerGenerator()
    
    test_cases = [
        ("failed_opportunities", "failed opportunities"),
        ("external_meetings_recorded", "external meetings recorded"),
        ("sf_name", "name"),
        ("total_price", "total value"),
        ("meeting_count", "meetings"),
        ("unknown_field", "unknown field")
    ]
    
    print("Field Name Conversion Tests:")
    for field, expected in test_cases:
        result = generator._convert_field_to_friendly_name(field)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status} {field} -> {result} (expected: {expected})")
    print()

def test_multi_part_detection():
    """Test multi-part query detection"""
    generator = AnswerGenerator()
    
    test_queries = [
        ("how many clients?", False),
        ("how many clients and what is the top product?", True),
        ("show me the most popular items", True),
        ("list all employees", False),
        ("count deals and show top manager", True),
        ("what are the best performing products?", True)
    ]
    
    print("Multi-part Query Detection Tests:")
    for query, expected in test_queries:
        result = generator._is_multi_part_query(query.lower())
        status = "PASS" if result == expected else "FAIL"
        print(f"{status} '{query}' -> {result} (expected: {expected})")
    print()

if __name__ == "__main__":
    print("=== Response Consistency Enhancement Tests ===\n")
    
    test_count_responses()
    test_multi_part_queries()
    test_field_name_conversion()
    test_multi_part_detection()
    
    print("=== Tests Complete ===")