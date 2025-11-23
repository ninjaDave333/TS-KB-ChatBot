#!/usr/bin/env python3
"""
Test flexible context extraction
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.answer_generator import AnswerGenerator

def test_flexible_context():
    """Test flexible context extraction for various queries"""
    generator = AnswerGenerator()
    
    test_cases = [
        "how many hashicorp products that has a successful deal during 2025 do we have ? list the names of the top 3",
        "how many microsoft products that has a successful deal during 2025 do we have ? list the names of the top 3", 
        "how many aws products that has a successful deal during 2025 do we have ? list the names of the top 3",
        "how many non terasky products that has a successful deal during 2025 do we have ? list the names of the top 3",
        "how many clients do we have ? list the top 3"
    ]
    
    data = [{
        "total_products": 5,
        "top_3_products": ["Product A", "Product B", "Product C"]
    }]
    
    for query in test_cases:
        answer = generator.generate_answer(query, "", data)
        print(f"Query: {query}")
        print(f"Answer: {answer}")
        print("-" * 50)

if __name__ == "__main__":
    test_flexible_context()