#!/usr/bin/env python3
"""
Unit tests for multi-model configuration support.
"""

import sys
import os
import asyncio
from unittest.mock import Mock, patch, MagicMock
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import get_model_config, get_rag_config
from app.core.llm_client import LLMClient

def test_model_config_primary():
    """Test that primary model config returns expected values."""
    config = get_model_config("primary")
    
    assert config is not None
    assert config['provider'] == 'bedrock'
    assert 'model_id' in config
    assert 'max_tokens' in config
    assert 'temperature' in config
    print("✅ Primary model config test passed!")

def test_model_config_judge():
    """Test that judge model config returns expected values.""" 
    config = get_model_config("judge")
    
    assert config is not None
    assert config['provider'] == 'bedrock'
    assert 'model_id' in config
    assert 'max_tokens' in config
    assert 'temperature' in config
    print("✅ Judge model config test passed!")

def test_model_config_fallback():
    """Test that unknown role falls back to primary."""
    primary_config = get_model_config("primary")
    unknown_config = get_model_config("unknown_role")
    
    assert unknown_config == primary_config
    print("✅ Model config fallback test passed!")

def test_rag_config_models_section():
    """Test that RAG config contains models section."""
    config = get_rag_config()
    
    assert 'models' in config
    assert 'primary' in config['models']
    assert 'judge' in config['models']
    print("✅ RAG config models section test passed!")

async def test_llm_client_primary_role():
    """Test LLMClient with primary role."""
    with patch('boto3.client') as mock_boto3:
        mock_bedrock = Mock()
        mock_boto3.return_value = mock_bedrock
        
        # Setup mock response
        mock_response = {'body': Mock()}
        mock_result = {'content': [{'text': 'MATCH (n) RETURN n LIMIT 5'}]}
        mock_response['body'].read.return_value = json.dumps(mock_result).encode()
        mock_bedrock.invoke_model.return_value = mock_response
        
        client = LLMClient()
        result = await client.generate("test prompt", role="primary")
        
        assert result == "MATCH (n) RETURN n LIMIT 5"
        
        # Verify correct model was used
        call_args = mock_bedrock.invoke_model.call_args
        body = json.loads(call_args[1]['body'])
        model_id = call_args[1]['modelId']
        
        # Should use primary model configuration
        primary_config = get_model_config("primary")
        assert model_id == primary_config['model_id']
        
        print("✅ LLMClient primary role test passed!")

async def test_llm_client_judge_role():
    """Test LLMClient with judge role."""
    with patch('boto3.client') as mock_boto3:
        mock_bedrock = Mock()
        mock_boto3.return_value = mock_bedrock
        
        # Setup mock response
        mock_response = {'body': Mock()}
        mock_result = {'content': [{'text': '{"score": 9, "reasoning": "Good answer"}'}]}
        mock_response['body'].read.return_value = json.dumps(mock_result).encode()
        mock_bedrock.invoke_model.return_value = mock_response
        
        client = LLMClient()
        result = await client.generate("evaluate this", role="judge")
        
        assert "score" in result
        
        # Verify correct model was used
        call_args = mock_bedrock.invoke_model.call_args
        model_id = call_args[1]['modelId']
        
        # Should use judge model configuration
        judge_config = get_model_config("judge")
        assert model_id == judge_config['model_id']
        
        print("✅ LLMClient judge role test passed!")

async def test_llm_client_complete_with_role():
    """Test LLMClient complete method with role parameter."""
    with patch('boto3.client') as mock_boto3:
        mock_bedrock = Mock()
        mock_boto3.return_value = mock_bedrock
        
        # Setup mock response
        mock_response = {'body': Mock()}
        mock_result = {'content': [{'text': 'MATCH (c:Client) RETURN count(c)'}]}
        mock_response['body'].read.return_value = json.dumps(mock_result).encode()
        mock_bedrock.invoke_model.return_value = mock_response
        
        client = LLMClient()
        result = await client.complete("system prompt", "user prompt", role="primary")
        
        assert result == "MATCH (c:Client) RETURN count(c)"
        
        # Verify system prompt was included
        call_args = mock_bedrock.invoke_model.call_args
        body = json.loads(call_args[1]['body'])
        assert body['system'] == "system prompt"
        
        print("✅ LLMClient complete with role test passed!")

def run_sync_tests():
    """Run synchronous tests."""
    test_model_config_primary()
    test_model_config_judge()
    test_model_config_fallback()
    test_rag_config_models_section()

async def run_async_tests():
    """Run asynchronous tests."""
    await test_llm_client_primary_role()
    await test_llm_client_judge_role()
    await test_llm_client_complete_with_role()

if __name__ == "__main__":
    print("Testing multi-model configuration...")
    run_sync_tests()
    asyncio.run(run_async_tests())
    print("✅ All multi-model configuration tests passed!")