#!/usr/bin/env python3
"""
Test the multi-part query detection for the specific failing case
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.answer_generator import AnswerGenerator

def test_specific_query():
    """Test the specific query that should be multi-part"""
    generator = AnswerGenerator()
    
    query = "how many non terasky products that has a succesfullt deal during 2025 do we have ? list the names of the top 3"
    
    is_multi = generator._is_multi_part_query(query)
    print(f"Query: {query}")
    print(f"Is multi-part: {is_multi}")
    
    # Test the components
    query_lower = query.lower()
    has_conjunction = any(conj in query_lower for conj in [" and ", " & ", "also", "plus", "additionally"])
    has_additional_request = any(req in query_lower for req in ["most popular", "top ", "highest", "best", "worst", "list", "show", "names"])
    has_question_then_request = "?" in query and any(req in query_lower.split("?")[-1] for req in ["list", "show", "names", "top"])
    
    print(f"Has conjunction: {has_conjunction}")
    print(f"Has additional request: {has_additional_request}")
    print(f"Has question then request: {has_question_then_request}")
    print(f"After question mark: '{query_lower.split('?')[-1]}'")

if __name__ == "__main__":
    test_specific_query()