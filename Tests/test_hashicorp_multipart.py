#!/usr/bin/env python3
"""
Test HashiCorp multi-part answer generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.answer_generator import AnswerGenerator

def test_hashicorp_multipart():
    """Test HashiCorp multi-part answer generation"""
    generator = AnswerGenerator()
    
    query = "how many hashicorp products that has a successful deal during 2025 do we have ? list the names of the top 3"
    data = [{
        "total_products": 3,
        "top_3_products": ["HashiCorp Vault", "HashiCorp Terraform", "HashiCorp Consul"]
    }]
    
    answer = generator.generate_answer(query, "", data)
    print(f"Answer: {answer}")

if __name__ == "__main__":
    test_hashicorp_multipart()