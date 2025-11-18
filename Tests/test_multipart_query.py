#!/usr/bin/env python3
"""
Test Multi-part Query Handling
Tests the enhanced answer generation for multi-part queries
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.answer_generator import AnswerGenerator

def test_multipart_failed_opportunities():
    """Test the specific multi-part query from the user"""
    generator = AnswerGenerator()
    
    # Test the exact query from the user
    query = "how many failed opportunities were during 2025? and what is the most popular failed product?"
    
    # Test with single count result (like the actual response)
    data_single = [{"total": 511}]
    result_single = generator.generate_answer(query, "", data_single)
    print(f"Query: {query}")
    print(f"Single count result: {result_single}")
    print()
    
    # Test with multiple product results
    data_multiple = [
        {"product_name": "HashiCorp Vault", "failure_count": 45},
        {"product_name": "AWS EC2", "failure_count": 38},
        {"product_name": "Microsoft Azure", "failure_count": 32}
    ]
    result_multiple = generator.generate_answer(query, "", data_multiple)
    print(f"Multiple product results: {result_multiple}")
    print()
    
    # Test the multi-part detection and generation directly
    is_multipart = generator._is_multi_part_query(query.lower())
    print(f"Is multi-part query: {is_multipart}")
    if is_multipart:
        multipart_result = generator._generate_multi_part_answer(query, data_single)
        print(f"Direct multi-part result: {multipart_result}")
    print()

def test_multipart_detection():
    """Test multi-part query detection"""
    generator = AnswerGenerator()
    
    test_queries = [
        "how many failed opportunities were during 2025? and what is the most popular failed product?",
        "show me clients and their top products",
        "count deals and display best manager",
        "how many clients?",
        "list employees"
    ]
    
    print("Multi-part Query Detection:")
    for query in test_queries:
        is_multipart = generator._is_multi_part_query(query.lower())
        print(f"'{query}' -> Multi-part: {is_multipart}")
    print()

if __name__ == "__main__":
    print("=== Multi-part Query Handling Test ===\n")
    
    test_multipart_failed_opportunities()
    test_multipart_detection()
    
    print("=== Test Complete ===")