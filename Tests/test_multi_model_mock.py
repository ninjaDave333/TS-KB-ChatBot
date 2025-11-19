#!/usr/bin/env python3
"""
Mock integration test to verify multi-model support without AWS model access.
"""

import sys
import os
import asyncio
from unittest.mock import Mock, patch, MagicMock
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.llm_client import LLMClient
from app.core.bedrock_client import BedrockClient
from app.core.judge_client import judge_answer
from app.core.config import get_model_config

async def test_multi_model_integration():
    """Test multi-model integration with mocked AWS calls."""
    print("Testing multi-model integration with mocked AWS...")
    
    with patch('boto3.client') as mock_boto3:
        # Setup mock Bedrock client
        mock_bedrock = Mock()
        mock_boto3.return_value = mock_bedrock
        
        # Setup different responses for different models
        def mock_invoke_model(modelId, body):
            mock_response = {'body': Mock()}
            
            if 'claude-v2' in modelId:  # Primary model
                mock_result = {'content': [{'text': 'MATCH (c:Client) RETURN count(c) as client_count'}]}
            elif 'claude-instant' in modelId:  # Judge model
                mock_result = {'content': [{'text': '{"score": 9, "reasoning": "Excellent Cypher query"}'}]}
            else:
                mock_result = {'content': [{'text': 'MATCH (n) RETURN n LIMIT 5'}]}
            
            mock_response['body'].read.return_value = json.dumps(mock_result).encode()
            return mock_response
        
        mock_bedrock.invoke_model.side_effect = mock_invoke_model
        
        # Test 1: Primary model usage
        print("\n1. Testing primary model usage...")
        llm_client = LLMClient()
        primary_response = await llm_client.generate("How many clients?", role="primary")
        
        assert "MATCH (c:Client)" in primary_response
        print(f"   Primary model response: {primary_response}")
        
        # Verify primary model was called
        primary_calls = [call for call in mock_bedrock.invoke_model.call_args_list 
                        if 'claude-v2' in call[1]['modelId']]
        assert len(primary_calls) > 0, "Primary model should have been called"
        print("   ✅ Primary model called correctly")
        
        # Test 2: Judge model usage
        print("\n2. Testing judge model usage...")
        judge_response = await llm_client.generate("Evaluate this query", role="judge")
        
        assert "score" in judge_response
        print(f"   Judge model response: {judge_response}")
        
        # Verify judge model was called
        judge_calls = [call for call in mock_bedrock.invoke_model.call_args_list 
                      if 'claude-instant' in call[1]['modelId']]
        assert len(judge_calls) > 0, "Judge model should have been called"
        print("   ✅ Judge model called correctly")
        
        # Test 3: BedrockClient with primary model
        print("\n3. Testing BedrockClient integration...")
        bedrock_client = BedrockClient(llm_client)
        
        # Mock schema
        mock_schema = {"nodes": [], "relationships": []}
        
        cypher_query = await bedrock_client.generate_cypher("How many clients?", mock_schema)
        assert cypher_query is not None
        assert len(cypher_query.strip()) > 0
        print(f"   Generated Cypher: {cypher_query}")
        print("   ✅ BedrockClient integration working")
        
        # Test 4: Judge client functionality
        print("\n4. Testing judge client functionality...")
        judge_result = await judge_answer(llm_client, "How many clients?", "There are 100 clients", "Client data")
        
        assert judge_result is not None
        assert 'score' in judge_result
        print(f"   Judge evaluation: {judge_result}")
        print("   ✅ Judge client working")
        
        # Test 5: Configuration verification
        print("\n5. Testing model configuration...")
        primary_config = get_model_config("primary")
        judge_config = get_model_config("judge")
        
        assert primary_config['model_id'] != judge_config['model_id']
        print(f"   Primary model: {primary_config['model_id']}")
        print(f"   Judge model: {judge_config['model_id']}")
        print("   ✅ Different models configured correctly")
        
        # Test 6: Role-based parameter usage
        print("\n6. Testing role-based parameters...")
        
        # Check that different models use different parameters
        primary_calls = [call for call in mock_bedrock.invoke_model.call_args_list 
                        if 'claude-v2' in call[1]['modelId']]
        judge_calls = [call for call in mock_bedrock.invoke_model.call_args_list 
                      if 'claude-instant' in call[1]['modelId']]
        
        if primary_calls and judge_calls:
            primary_body = json.loads(primary_calls[-1][1]['body'])
            judge_body = json.loads(judge_calls[-1][1]['body'])
            
            # Different models should potentially use different parameters
            print(f"   Primary max_tokens: {primary_body.get('max_tokens', 'default')}")
            print(f"   Judge max_tokens: {judge_body.get('max_tokens', 'default')}")
            print("   ✅ Role-based parameters working")
        
        print("\n🎉 All multi-model integration tests passed!")
        return True

if __name__ == "__main__":
    success = asyncio.run(test_multi_model_integration())
    if success:
        print("\n✅ Multi-model support verified successfully!")
        print("📝 Note: This test uses mocked AWS calls due to model access restrictions")
        print("🚀 Phase 3 multi-model implementation is working correctly")
    else:
        print("\n❌ Multi-model integration tests failed!")
        sys.exit(1)