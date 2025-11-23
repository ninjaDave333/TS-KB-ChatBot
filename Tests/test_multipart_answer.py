#!/usr/bin/env python3
"""
Test the improved multi-part answer generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.answer_generator import AnswerGenerator

def test_multipart_answer():
    """Test multi-part answer generation with both count and list data"""
    generator = AnswerGenerator()
    
    # Test data that matches the learned pattern structure
    query = "how many non terasky products that has a successful deal during 2025 do we have ? list the names of the top 3"
    data = [{
        "total_products": 95,
        "top_3_products": ["Microsoft Azure", "AWS EC2", "Google Cloud Platform"]
    }]
    
    is_multi = generator._is_multi_part_query(query)
    print(f"Query: {query}")
    print(f"Is multi-part: {is_multi}")
    
    answer = generator.generate_answer(query, "", data)
    print(f"Answer: {answer}")
    print("-" * 50)
    
    # Test with different data structure
    data2 = [
        {"name": "Microsoft Azure", "deal_count": 25},
        {"name": "AWS EC2", "deal_count": 20},
        {"name": "Google Cloud Platform", "deal_count": 18}
    ]
    
    answer2 = generator.generate_answer(query, "", data2)
    print(f"Answer with multiple records: {answer2}")

if __name__ == "__main__":
    test_multipart_answer()