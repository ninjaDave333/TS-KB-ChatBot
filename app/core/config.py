import yaml
import os
from functools import lru_cache
from typing import Dict, Any

@lru_cache(maxsize=1)
def get_rag_config() -> Dict[str, Any]:
    """
    Load RAG configuration from YAML file with caching.
    Returns default values if config file is not found or invalid.
    """
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'rag_config.yaml')
    
    # Default configuration
    default_config = {
        'routing': {
            'learned_pattern_threshold': 0.8,
            'fallback_order': ['ai', 'enhanced', 'traditional']
        },
        'models': {
            'primary': {
                'provider': 'bedrock',
                'model_id': 'us.anthropic.claude-sonnet-4-20250514-v1:0',
                'max_tokens': 4000,
                'temperature': 0.3
            },
            'judge': {
                'provider': 'bedrock',
                'model_id': 'us.anthropic.claude-sonnet-4-20250514-v1:0',
                'max_tokens': 2000,
                'temperature': 0.0
            }
        }
    }
    
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            return config if config else default_config
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"Warning: Could not load RAG config from {config_path}: {e}")
        print("Using default configuration")
        return default_config

def get_model_config(role: str = "primary") -> Dict[str, Any]:
    """
    Get model configuration for a specific role.
    Falls back to primary model if role not found.
    """
    config = get_rag_config()
    
    # Default model configurations
    default_models = {
        'primary': {
            'provider': 'bedrock',
            'model_id': 'us.anthropic.claude-sonnet-4-20250514-v1:0',
            'max_tokens': 4000,
            'temperature': 0.3
        },
        'judge': {
            'provider': 'bedrock',
            'model_id': 'us.anthropic.claude-sonnet-4-20250514-v1:0',
            'max_tokens': 2000,
            'temperature': 0.0
        }
    }
    
    models = config.get('models', default_models)
    return models.get(role, models.get('primary', default_models['primary']))