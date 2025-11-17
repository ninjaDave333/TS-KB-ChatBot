#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.answer_generator import AnswerGenerator

def test_israeli_answer():
    """Test improved Israeli clients answer generation"""
    
    generator = AnswerGenerator()
    
    # Test data from actual API response
    user_query = "List 5 clients in Israel with their account managers"
    data = [
        {"client": "Colmobil", "account_manager": "Amnon Sinai"},
        {"client": "Nova Measuring Instruments", "account_manager": "Amnon Sinai"},
        {"client": "Teva Pharmaceutical Industries", "account_manager": "Amnon Sinai"},
        {"client": "Israel Aerospace Industries", "account_manager": "Eran Spitz"},
        {"client": "EMC (spain)", "account_manager": "Gera Lifshits"}
    ]
    
    # Generate answer
    answer = generator.generate_answer(user_query, "", data)
    
    print("=== Israeli Clients Answer Test ===")
    print(f"Query: {user_query}")
    print(f"Generated Answer: {answer}")
    print()
    
    # Check if answer contains client names and managers
    expected_elements = ["Israeli clients", "Colmobil", "Amnon Sinai", "managed by"]
    
    success = all(element in answer for element in expected_elements)
    
    if success:
        print("✅ Test PASSED - Answer contains client names and managers")
    else:
        print("❌ Test FAILED - Answer missing key information")
        missing = [elem for elem in expected_elements if elem not in answer]
        print(f"Missing elements: {missing}")
    
    return success

if __name__ == "__main__":
    success = test_israeli_answer()
    
    if success:
        print("\n🎉 Israeli clients answer generation FIXED!")
        print("Next: Restart API server and run RAGAS test")
    else:
        print("\n⚠️ Israeli clients answer generation needs more work")