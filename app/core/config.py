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