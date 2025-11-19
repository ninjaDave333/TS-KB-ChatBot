#!/usr/bin/env python3
"""
Unit tests for LLMClient abstraction.
"""

import sys
import os
import asyncio
from unittest.mock import Mock, patch, MagicMock
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.llm_client import LLMClient

def run_tests():
    """Run all tests."""
    print("Testing LLMClient abstraction...")
    
    # Test initialization
    with patch('boto3.client') as mock_boto3:
        mock_bedrock = Mock()
        mock_boto3.return_value = mock_bedrock
        
        client = LLMClient()
        assert client.bedrock_client == mock_bedrock
        assert client.model_name is not None
        print("✅ LLMClient initialization test passed!")
    
    # Test custom model
    with patch('boto3.client') as mock_boto3:
        mock_bedrock = Mock()
        mock_boto3.return_value = mock_bedrock
        custom_model = "custom-model-id"
        
        client = LLMClient(model_name=custom_model)
        assert client.model_name == custom_model
        print("✅ LLMClient custom model initialization test passed!")
    
    # Test initialization failure
    with patch('boto3.client', side_effect=Exception("AWS Error")):
        client = LLMClient()
        assert client.bedrock_client is None
        assert client.model_name is None
        print("✅ LLMClient initialization failure test passed!")

async def run_async_tests():
    """Run async method tests."""
    # Test generate method
    with patch('boto3.client') as mock_boto3:
        mock_bedrock = Mock()
        mock_boto3.return_value = mock_bedrock
        
        # Setup mock response
        mock_response = {'body': Mock()}
        mock_result = {'content': [{'text': 'MATCH (n) RETURN n LIMIT 5'}]}
        mock_response['body'].read.return_value = json.dumps(mock_result).encode()
        mock_bedrock.invoke_model.return_value = mock_response
        
        client = LLMClient()
        result = await client.generate("test prompt")
        
        assert result == "MATCH (n) RETURN n LIMIT 5"
        print("✅ LLMClient.generate() test passed!")
    
    # Test complete method
    with patch('boto3.client') as mock_boto3:
        mock_bedrock = Mock()
        mock_boto3.return_value = mock_bedrock
        
        # Setup mock response
        mock_response = {'body': Mock()}
        mock_result = {'content': [{'text': 'MATCH (n) RETURN n LIMIT 5'}]}
        mock_response['body'].read.return_value = json.dumps(mock_result).encode()
        mock_bedrock.invoke_model.return_value = mock_response
        
        client = LLMClient()
        result = await client.complete("system prompt", "user prompt")
        
        assert result == "MATCH (n) RETURN n LIMIT 5"
        print("✅ LLMClient.complete() test passed!")
    
    # Test error handling
    with patch('boto3.client') as mock_boto3:
        mock_bedrock = Mock()
        mock_boto3.return_value = mock_bedrock
        mock_bedrock.invoke_model.side_effect = Exception("API Error")
        
        client = LLMClient()
        
        try:
            await client.generate("test prompt")
            assert False, "Should have raised exception"
        except Exception as e:
            assert "API Error" in str(e)
            print("✅ LLMClient error handling test passed!")

if __name__ == "__main__":
    run_tests()
    asyncio.run(run_async_tests())
    print("✅ All LLMClient tests passed!")