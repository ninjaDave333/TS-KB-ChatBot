#!/usr/bin/env python3
"""
Phase 3 verification test - confirms multi-model configuration works without calling models.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import get_model_config, get_rag_config
from app.core.llm_client import LLMClient

def test_phase3_config_verification():
    """Verify Phase 3 multi-model configuration is working correctly."""
    print("Phase 3 Verification: Multi-Model Configuration")
    print("=" * 50)
    
    # Test 1: Configuration loading
    print("1. Testing configuration loading...")
    config = get_rag_config()
    assert 'models' in config, "Config missing models section"
    assert 'primary' in config['models'], "Config missing primary model"
    assert 'judge' in config['models'], "Config missing judge model"
    print("   ✅ Configuration structure correct")
    
    # Test 2: Model config retrieval
    print("2. Testing model config retrieval...")
    primary_config = get_model_config("primary")
    judge_config = get_model_config("judge")
    
    print(f"   Primary model: {primary_config['model_id']}")
    print(f"   Judge model: {judge_config['model_id']}")
    
    # Verify they are different models
    assert primary_config['model_id'] != judge_config['model_id'], "Primary and judge should use different models"
    print("   ✅ Primary and judge models are different")
    
    # Test 3: Model parameters
    print("3. Testing model parameters...")
    assert primary_config['max_tokens'] == 4000, "Primary model max_tokens incorrect"
    assert judge_config['max_tokens'] == 2000, "Judge model max_tokens incorrect"
    assert primary_config['temperature'] == 0.3, "Primary model temperature incorrect"
    assert judge_config['temperature'] == 0.0, "Judge model temperature incorrect"
    print("   ✅ Model parameters correct")
    
    # Test 4: Fallback behavior
    print("4. Testing fallback behavior...")
    unknown_config = get_model_config("unknown_role")
    assert unknown_config == primary_config, "Unknown role should fallback to primary"
    print("   ✅ Fallback to primary works")
    
    # Test 5: LLMClient initialization
    print("5. Testing LLMClient initialization...")
    try:
        llm_client = LLMClient()
        print("   ✅ LLMClient initializes successfully")
    except Exception as e:
        print(f"   ⚠️  LLMClient initialization failed (expected if no AWS access): {e}")
    
    # Test 6: Judge client import
    print("6. Testing judge client import...")
    try:
        from app.core.judge_client import judge_answer
        print("   ✅ Judge client imports successfully")
    except Exception as e:
        print(f"   ❌ Judge client import failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ Phase 3 Multi-Model Configuration VERIFIED")
    print("\nKey Achievements:")
    print(f"  • Primary model: {primary_config['model_id']}")
    print(f"  • Judge model: {judge_config['model_id']}")
    print("  • Role-based model selection working")
    print("  • Configuration-driven model management")
    print("  • Judge model foundation ready")
    
    return True

if __name__ == "__main__":
    success = test_phase3_config_verification()
    if success:
        print("\n🎉 Phase 3 implementation verified successfully!")
        print("Ready for Phase 4: Judge model evaluation and quality assessment")
    else:
        print("\n❌ Phase 3 verification failed")
        sys.exit(1)