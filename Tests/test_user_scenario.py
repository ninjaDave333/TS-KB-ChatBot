#!/usr/bin/env python3
"""
Test User Scenario - Multi-part Failed Opportunities Query
Tests the exact scenario reported by the user
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.answer_generator import AnswerGenerator

def test_user_scenario():
    """Test the exact user scenario"""
    generator = AnswerGenerator()
    
    # User's exact query
    query = "how many failed opportunities were during 2025? and what is the most popular failed product?"
    
    # Simulate the actual API response (single count result)
    data = [{"total": 511}]
    
    # Generate answer
    result = generator.generate_answer(query, "", data)
    
    print("=== User Scenario Test ===")
    print(f"Query: {query}")
    print(f"Data: {data}")
    print(f"Result: {result}")
    print()
    
    # Verify it's a multi-part query
    is_multipart = generator._is_multi_part_query(query.lower())
    print(f"Detected as multi-part: {is_multipart}")
    
    # Check if it provides information about both parts
    has_count = "511" in result
    has_product_info = any(word in result.lower() for word in ["product", "azure", "aws", "hashicorp"])
    
    print(f"Includes count information: {has_count}")
    print(f"Includes product information: {has_product_info}")
    
    if has_count and has_product_info:
        print("SUCCESS: Query answers both parts!")
    else:
        print("ISSUE: Query doesn't fully address both parts")

if __name__ == "__main__":
    test_user_scenario()