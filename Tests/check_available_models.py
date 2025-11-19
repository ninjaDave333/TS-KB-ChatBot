#!/usr/bin/env python3
"""
Check available AWS Bedrock models in the current account.
"""

import boto3
import json
from botocore.exceptions import ClientError

def check_available_models():
    """Check which Bedrock models are available."""
    try:
        bedrock_client = boto3.client('bedrock', region_name='us-east-1')
        
        print("Checking available Bedrock models...")
        
        # List foundation models
        response = bedrock_client.list_foundation_models()
        
        available_models = []
        anthropic_models = []
        
        for model in response['modelSummaries']:
            model_id = model['modelId']
            model_name = model['modelName']
            provider = model['providerName']
            
            available_models.append({
                'id': model_id,
                'name': model_name,
                'provider': provider
            })
            
            if 'anthropic' in provider.lower():
                anthropic_models.append({
                    'id': model_id,
                    'name': model_name
                })
        
        print(f"\nFound {len(available_models)} available models")
        
        print(f"\nAnthropic Models ({len(anthropic_models)} available):")
        for model in anthropic_models:
            print(f"  - {model['id']}")
            print(f"    Name: {model['name']}")
        
        # Test current primary model
        current_primary = "us.anthropic.claude-sonnet-4-20250514-v1:0"
        primary_available = any(m['id'] == current_primary for m in available_models)
        print(f"\nCurrent primary model ({current_primary}): {'Available' if primary_available else 'Not Available'}")
        
        # Test current judge model
        current_judge = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
        judge_available = any(m['id'] == current_judge for m in available_models)
        print(f"Current judge model ({current_judge}): {'Available' if judge_available else 'Not Available'}")
        
        # Suggest alternative judge models
        print(f"\nSuggested judge models (faster/cheaper alternatives):")
        for model in anthropic_models:
            if 'haiku' in model['name'].lower() or 'claude-3' in model['id']:
                print(f"  - {model['id']}")
        
        return anthropic_models
        
    except ClientError as e:
        print(f"Error checking models: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

if __name__ == "__main__":
    models = check_available_models()
    
    if models:
        print(f"\nCopy one of the available model IDs above to update the judge model in config/rag_config.yaml")
    else:
        print(f"\nNo models found. Check your AWS credentials and Bedrock access.")