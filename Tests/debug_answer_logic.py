#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.answer_generator import AnswerGenerator

def debug_answer_logic():
    """Debug why Israeli answer logic isn't working"""
    
    generator = AnswerGenerator()
    
    user_query = "List 5 clients in Israel with their account managers"
    data = [{"client": "Colmobil", "account_manager": "Amnon Sinai"}]
    
    query_lower = user_query.lower()
    
    print("=== Debug Answer Logic ===")
    print(f"Query: {user_query}")
    print(f"Query lower: {query_lower}")
    print(f"Data: {data}")
    print()
    
    # Test each condition
    print("Testing conditions:")
    
    # Count query test
    is_count = generator._is_count_query(query_lower, data)
    print(f"Is count query: {is_count}")
    
    # List query test  
    is_list = generator._is_list_query(query_lower)
    print(f"Is list query: {is_list}")
    
    # Vendor query test
    is_vendor = generator._is_vendor_query(query_lower)
    print(f"Is vendor query: {is_vendor}")
    
    print()
    
    # Test Israeli detection
    has_israel = "israel" in query_lower
    has_manager = "manager" in query_lower
    print(f"Has 'israel': {has_israel}")
    print(f"Has 'manager': {has_manager}")
    
    # Generate answer
    answer = generator.generate_answer(user_query, "", data)
    print(f"\nGenerated answer: {answer}")

if __name__ == "__main__":
    debug_answer_logic()