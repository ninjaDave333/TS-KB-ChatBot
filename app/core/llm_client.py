import boto3
import json
import os
from typing import Dict, Any, Optional
from .config import get_model_config

class LLMClient:
    """Centralized LLM abstraction for all model interactions."""
    
    def __init__(self):
        """Initialize LLM client with Bedrock connection."""
        try:
            self.bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
            print(f"LLMClient initialized with multi-model support")
        except Exception as e:
            print(f"LLMClient initialization failed: {e}")
            self.bedrock_client = None
    
    async def generate(self, prompt: str, role: str = "primary", **kwargs) -> str:
        """Generate response from a single prompt using specified model role."""
        if not self.bedrock_client:
            raise Exception("LLMClient not initialized")
        
        # Get model configuration for the specified role
        model_config = get_model_config(role)
        model_id = model_config['model_id']
        max_tokens = kwargs.get('max_tokens', model_config.get('max_tokens', 4096))
        temperature = kwargs.get('temperature', model_config.get('temperature', 0.3))
        
        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=model_id,
                body=json.dumps(body)
            )
            
            result = json.loads(response['body'].read())
            return result['content'][0]['text'].strip()
            
        except Exception as e:
            print(f"LLMClient API error (role: {role}, model: {model_id}): {e}")
            raise e
    
    async def complete(self, system_prompt: str, user_prompt: str, role: str = "primary", **kwargs) -> str:
        """Generate response with system and user prompts using specified model role."""
        if not self.bedrock_client:
            raise Exception("LLMClient not initialized")
        
        # Get model configuration for the specified role
        model_config = get_model_config(role)
        model_id = model_config['model_id']
        max_tokens = kwargs.get('max_tokens', model_config.get('max_tokens', 4096))
        temperature = kwargs.get('temperature', model_config.get('temperature', 0.3))
        
        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=model_id,
                body=json.dumps(body)
            )
            
            result = json.loads(response['body'].read())
            return result['content'][0]['text'].strip()
            
        except Exception as e:
            print(f"LLMClient API error (role: {role}, model: {model_id}): {e}")
            raise e