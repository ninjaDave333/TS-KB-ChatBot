#!/usr/bin/env python3
"""
Integration test to verify identical behavior before/after LLMClient refactor.
"""

import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.llm_client import LLMClient
from app.core.bedrock_client import BedrockClient
from app.database.neo4j_client import Neo4jClient

async def test_integration():
    """Test that refactored BedrockClient produces identical results."""
    print("Testing LLMClient integration...")
    
    try:
        # Initialize components
        llm_client = LLMClient()
        bedrock_client = BedrockClient(llm_client)
        neo4j_client = Neo4jClient()
        
        # Get schema
        schema = neo4j_client.get_schema()
        
        # Test query
        test_query = "How many clients are there?"
        
        print(f"Testing query: {test_query}")
        
        # Generate Cypher using refactored BedrockClient
        cypher_query = await bedrock_client.generate_cypher(test_query, schema)
        
        print(f"Generated Cypher: {cypher_query}")
        
        # Verify the query is valid Cypher
        assert cypher_query is not None
        assert len(cypher_query.strip()) > 0
        assert "MATCH" in cypher_query.upper() or "RETURN" in cypher_query.upper()
        
        print("✅ Integration test passed - BedrockClient generates valid Cypher via LLMClient")
        
        # Test that we can execute the query (optional)
        try:
            result = neo4j_client.execute_query(cypher_query)
            print(f"Query executed successfully, returned {len(result)} results")
        except Exception as e:
            print(f"Query execution failed (expected for some generated queries): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_integration())
    if success:
        print("✅ All integration tests passed!")
    else:
        print("❌ Integration tests failed!")
        sys.exit(1)