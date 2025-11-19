#!/usr/bin/env python3
"""
Test script to verify RAG configuration loading and routing behavior.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import get_rag_config

def test_config_loading():
    """Test that RAG configuration loads correctly."""
    print("Testing RAG configuration loading...")
    
    config = get_rag_config()
    print(f"Loaded config: {config}")
    
    # Verify expected structure
    assert 'routing' in config, "Missing 'routing' section in config"
    assert 'learned_pattern_threshold' in config['routing'], "Missing learned_pattern_threshold"
    assert 'fallback_order' in config['routing'], "Missing fallback_order"
    
    # Verify expected values
    threshold = config['routing']['learned_pattern_threshold']
    fallback_order = config['routing']['fallback_order']
    
    print(f"Learned pattern threshold: {threshold}")
    print(f"Fallback order: {fallback_order}")
    
    assert isinstance(threshold, (int, float)), "Threshold should be numeric"
    assert isinstance(fallback_order, list), "Fallback order should be a list"
    assert len(fallback_order) >= 2, "Should have at least 2 fallback methods"
    
    print("✅ Configuration loading test passed!")
    return config

if __name__ == "__main__":
    test_config_loading()