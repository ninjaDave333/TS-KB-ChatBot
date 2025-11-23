#!/usr/bin/env python3
"""
Test the fixed answer generation logic
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.answer_generator import AnswerGenerator

def test_count_queries():
    """Test count query detection and answer generation"""
    generator = AnswerGenerator()
    
    # Test simple count query
    query1 = "how many non terasky products do we have ?"
    data1 = [{"non_terasky_products": 429}]
    
    is_count = generator._is_count_query(query1, data1)
    is_multi = generator._is_multi_part_query(query1)
    
    print(f"Query: {query1}")
    print(f"Is count query: {is_count}")
    print(f"Is multi-part: {is_multi}")
    
    answer = generator.generate_answer(query1, "", data1)
    print(f"Answer: {answer}")
    print("-" * 50)
    
    # Test count query with additional criteria
    query2 = "how many non terasky products that has a successful deal during 2025 do we have ?"
    data2 = [{"non_terasky_products_count": 95}]
    
    is_count2 = generator._is_count_query(query2, data2)
    is_multi2 = generator._is_multi_part_query(query2)
    
    print(f"Query: {query2}")
    print(f"Is count query: {is_count2}")
    print(f"Is multi-part: {is_multi2}")
    
    answer2 = generator.generate_answer(query2, "", data2)
    print(f"Answer: {answer2}")
    print("-" * 50)
    
    # Test actual multi-part query
    query3 = "how many non terasky products that has a successful deal during 2025 do we have ? list the names of the top 3"
    data3 = [{"product_name": "Product A", "count": 10}, {"product_name": "Product B", "count": 8}]
    
    is_count3 = generator._is_count_query(query3, data3)
    is_multi3 = generator._is_multi_part_query(query3)
    
    print(f"Query: {query3}")
    print(f"Is count query: {is_count3}")
    print(f"Is multi-part: {is_multi3}")
    
    answer3 = generator.generate_answer(query3, "", data3)
    print(f"Answer: {answer3}")
    print("-" * 50)

if __name__ == "__main__":
    test_count_queries()