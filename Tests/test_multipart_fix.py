#!/usr/bin/env python3
"""
Test the improved multi-part query detection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.answer_generator import AnswerGenerator

def test_multipart_detection():
    """Test multi-part query detection"""
    generator = AnswerGenerator()
    
    test_queries = [
        "how many non terasky products do we have ?",
        "how many non terasky products that has a successful deal during 2025 do we have ?",
        "how many non terasky products that has a successful deal during 2025 do we have ? list the names of the top 3",
        "list the names of the top 3 best sellers of 2025",
        "list the name of the top best seller of 2025"
    ]
    
    for query in test_queries:
        is_multi = generator._is_multi_part_query(query)
        print(f"Query: {query}")
        print(f"Is multi-part: {is_multi}")
        print("-" * 50)

if __name__ == "__main__":
    test_multipart_detection()