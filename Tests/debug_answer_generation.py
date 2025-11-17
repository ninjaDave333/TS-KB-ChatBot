#!/usr/bin/env python3
"""
Debug answer generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.answer_generator import AnswerGenerator

def debug_answer_generation():
    """Debug the answer generation for client ranking"""
    
    generator = AnswerGenerator()
    
    # Test data from the actual query
    test_data = [
        {'client': 'PayKey', 'recorded_meetings': 88}, 
        {'client': 'FireFly (ex Infralight)', 'recorded_meetings': 88}, 
        {'client': 'Ametos', 'recorded_meetings': 88}
    ]
    
    query = "Top 3 clients most recorded meetings"
    
    # Test the query type detection
    query_type = generator._detect_query_type(query)
    print(f"Detected query type: {query_type}")
    
    # Test the answer generation
    answer = generator.generate_answer(query, "", test_data)
    print(f"Generated answer: {answer}")
    
    # Test the specific method
    if query_type == "client_meeting_ranking":
        answer = generator._generate_meeting_analytics_answer(query, test_data, query_type)
        print(f"Direct method answer: {answer}")

if __name__ == "__main__":
    debug_answer_generation()