#!/usr/bin/env python3
"""
Test the enhanced schema descriptions with WIX query
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.bedrock_client import BedrockClient
from app.core.schema_descriptions import SCHEMA_DESCRIPTIONS

def test_enhanced_schema():
    print("=== Testing Enhanced Schema Descriptions ===")
    
    # Mock schema (what would come from Neo4j)
    mock_schema = {
        'node_types': ['Client', 'Employee', 'Product', 'Vendor', 'Region'],
        'relationship_types': ['OPPORTUNITY', 'MANAGED_BY', 'MAKES', 'LOCATED_IN']
    }
    
    # Test queries
    test_queries = [
        "find OPPORTUNITY with close won related to client WIX",
        "show me all products WIX purchased",
        "who manages WIX account",
        "what products did WIX install"
    ]
    
    bedrock_client = BedrockClient()
    
    for query in test_queries:
        print(f"\n--- Query: {query} ---")
        try:
            cypher = bedrock_client.generate_cypher(query, mock_schema)
            print(f"Generated Cypher: {cypher}")
        except Exception as e:
            print(f"Error: {e}")
    
    # Show schema descriptions sample
    print("\n=== Schema Descriptions Sample ===")
    client_desc = SCHEMA_DESCRIPTIONS['nodes']['Client']
    print(f"Client purpose: {client_desc['purpose']}")
    print(f"Client name field: {client_desc['name_field']}")
    print(f"Critical properties: {list(client_desc['key_properties'].keys())}")
    
    opp_desc = SCHEMA_DESCRIPTIONS['relationships']['OPPORTUNITY']
    print(f"Opportunity pattern: {opp_desc['pattern']}")
    print(f"Common stages: {opp_desc['common_stages']}")

if __name__ == "__main__":
    test_enhanced_schema()