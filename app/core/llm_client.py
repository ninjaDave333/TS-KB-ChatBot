import boto3
import json
import os
from typing import Dict, Any, Optional

class LLMClient:
    """Centralized LLM abstraction for all model interactions."""
    
    def __init__(self, model_name: Optional[str] = None):
        """Initialize LLM client with specified model."""
        try:
            self.bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
            self.model_name = model_name or os.getenv('AWS_BEDROCK_MODEL_ID', 'us.anthropic.claude-3-5-haiku-20241022-v1:0')
            print(f"LLMClient initialized with model: {self.model_name}")
        except Exception as e:
            print(f"LLMClient initialization failed: {e}")
            self.bedrock_client = None
            self.model_name = None
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from a single prompt."""
        if not self.bedrock_client:
            raise Exception("LLMClient not initialized")
        
        max_tokens = kwargs.get('max_tokens', 4096)
        
        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_name,
                body=json.dumps(body)
            )
            
            result = json.loads(response['body'].read())
            return result['content'][0]['text'].strip()
            
        except Exception as e:
            print(f"LLMClient API error: {e}")
            raise e
    
    async def complete(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """Generate response with system and user prompts."""
        if not self.bedrock_client:
            raise Exception("LLMClient not initialized")
        
        max_tokens = kwargs.get('max_tokens', 4096)
        
        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_name,
                body=json.dumps(body)
            )
            
            result = json.loads(response['body'].read())
            return result['content'][0]['text'].strip()
            
        except Exception as e:
            print(f"LLMClient API error: {e}")
            raise e