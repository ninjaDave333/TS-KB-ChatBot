"""
Test script to validate self-learning RAG integration.
Tests intent classification, prompt selection, and validation.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.prompt_profiles import classify_question_intent, get_prompt_for_intent
from app.core.cypher_validator import validate_and_clean

# Test queries
TEST_QUERIES = [
    "Top 5 clients with most deals in 2024",
    "List all meetings David Gidony is owner of in the past 2 months",
    "5 top selling security products during 2023-2025",
    "How many clients purchased HashiCorp products in 2025?",
]

def test_intent_classification():
    """Test intent classification for various queries."""
    print("\n" + "="*80)
    print("TEST 1: Intent Classification")
    print("="*80)
    
    for query in TEST_QUERIES:
        intent = classify_question_intent(query)
        print(f"\nQuery: {query}")
        print(f"Intent: {intent}")

def test_prompt_generation():
    """Test prompt generation for each intent."""
    print("\n" + "="*80)
    print("TEST 2: Prompt Generation")
    print("="*80)
    
    for query in TEST_QUERIES:
        intent = classify_question_intent(query)
        system_prompt, user_prompt = get_prompt_for_intent(intent, query)
        
        print(f"\nQuery: {query}")
        print(f"Intent: {intent}")
        print(f"System Prompt Length: {len(system_prompt)} chars")
        print(f"User Prompt: {user_prompt[:100]}...")

def test_validation():
    """Test Cypher validation."""
    print("\n" + "="*80)
    print("TEST 3: Cypher Validation")
    print("="*80)
    
    # Valid Cypher
    valid_cypher = """
    MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
    WHERE o.opportunity_stage = 'Closed Won'
      AND o.close_date >= '2024-01-01' AND o.close_date < '2025-01-01'
    WITH c.sf_name AS client, count(o) AS deal_count
    ORDER BY deal_count DESC
    LIMIT 5
    RETURN client, deal_count
    """
    
    print("\nTest 1: Valid Cypher")
    cleaned, errors = validate_and_clean(valid_cypher)
    print(f"Errors: {errors if errors else 'None'}")
    print(f"Cleaned: {cleaned[:100]}...")
    
    # Invalid Cypher (SQL)
    invalid_sql = "SELECT * FROM clients WHERE year = 2024"
    
    print("\nTest 2: Invalid SQL")
    cleaned, errors = validate_and_clean(invalid_sql)
    print(f"Errors: {errors}")
    
    # Cypher with markdown
    markdown_cypher = """
    ```cypher
    MATCH (c:Client) RETURN count(c) as total
    ```
    """
    
    print("\nTest 3: Cypher with markdown")
    cleaned, errors = validate_and_clean(markdown_cypher)
    print(f"Errors: {errors if errors else 'None'}")
    print(f"Cleaned: {cleaned}")

def test_best_config():
    """Test best config loading."""
    print("\n" + "="*80)
    print("TEST 4: Best Config Loading")
    print("="*80)
    
    import json
    config_path = Path("data/best_config.json")
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"\nBest Config Found:")
        print(f"  Temperature: {config.get('temperature')}")
        print(f"  Profile: {config.get('prompt_profile')}")
    else:
        print("\n❌ Best config not found at data/best_config.json")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("SELF-LEARNING RAG INTEGRATION TEST")
    print("="*80)
    
    try:
        test_intent_classification()
        test_prompt_generation()
        test_validation()
        test_best_config()
        
        print("\n" + "="*80)
        print("[SUCCESS] ALL TESTS COMPLETED")
        print("="*80)
        
    except Exception as e:
        print(f"\n[FAILED] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
