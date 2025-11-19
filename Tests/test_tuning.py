"""
Tests for Config Auto-Tuning System

Comprehensive unit tests for tuning engine, suggestion generation,
and configuration application with safety guardrails.
"""

import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from app.monitoring.tuning import (
    IntentStats,
    TuningSuggestion,
    load_intent_stats,
    suggest_retrieval_tuning,
    apply_suggestions_to_config
)


class TestIntentStats:
    """Test IntentStats data model."""
    
    def test_intent_stats_creation(self):
        """Test IntentStats dataclass creation."""
        stats = IntentStats(
            intent="TEST_INTENT",
            eval_count=25,
            avg_overall_score=7.5,
            avg_factual_correctness=8.0,
            avg_grounded_in_context=7.2,
            avg_helpfulness=7.8,
            error_type_distribution={"retrieval": 0.2, "none": 0.8}
        )
        
        assert stats.intent == "TEST_INTENT"
        assert stats.eval_count == 25
        assert stats.avg_overall_score == 7.5
        assert stats.error_type_distribution["retrieval"] == 0.2


class TestTuningSuggestion:
    """Test TuningSuggestion data model."""
    
    def test_tuning_suggestion_creation(self):
        """Test TuningSuggestion dataclass creation."""
        suggestion = TuningSuggestion(
            intent="CLIENT_HISTORY",
            current_limit=10,
            suggested_limit=15,
            reason="High retrieval errors detected"
        )
        
        assert suggestion.intent == "CLIENT_HISTORY"
        assert suggestion.current_limit == 10
        assert suggestion.suggested_limit == 15
        assert "High retrieval errors" in suggestion.reason


class TestLoadIntentStats:
    """Test loading and computing intent statistics from eval results."""
    
    def test_load_intent_stats_success(self):
        """Test successful loading of intent stats from eval results."""
        # Create sample eval results
        eval_data = [
            {
                "intent": "CLIENT_HISTORY",
                "scores": {
                    "overall_score": 6.0,
                    "factual_correctness": 7.0,
                    "grounded_in_context": 5.0,
                    "helpfulness": 6.0
                },
                "primary_issue": "retrieval"
            },
            {
                "intent": "CLIENT_HISTORY", 
                "scores": {
                    "overall_score": 8.0,
                    "factual_correctness": 8.0,
                    "grounded_in_context": 8.0,
                    "helpfulness": 8.0
                },
                "primary_issue": "none"
            },
            {
                "intent": "PRODUCT_INFO",
                "scores": {
                    "overall_score": 9.0,
                    "factual_correctness": 9.0,
                    "grounded_in_context": 9.0,
                    "helpfulness": 9.0
                },
                "primary_issue": "none"
            }
        ]
        
        # Write to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            for item in eval_data:
                f.write(json.dumps(item) + '\n')
            temp_path = Path(f.name)
        
        try:
            # Load stats
            stats = load_intent_stats(temp_path)
            
            # Verify CLIENT_HISTORY stats
            assert "CLIENT_HISTORY" in stats
            client_stats = stats["CLIENT_HISTORY"]
            assert client_stats.eval_count == 2
            assert client_stats.avg_overall_score == 7.0  # (6.0 + 8.0) / 2
            assert client_stats.avg_factual_correctness == 7.5  # (7.0 + 8.0) / 2
            assert client_stats.error_type_distribution["retrieval"] == 0.5  # 1/2
            assert client_stats.error_type_distribution["none"] == 0.5  # 1/2
            
            # Verify PRODUCT_INFO stats
            assert "PRODUCT_INFO" in stats
            product_stats = stats["PRODUCT_INFO"]
            assert product_stats.eval_count == 1
            assert product_stats.avg_overall_score == 9.0
            assert product_stats.error_type_distribution["none"] == 1.0
            
        finally:
            temp_path.unlink()
    
    def test_load_intent_stats_missing_file(self):
        """Test handling of missing eval results file."""
        nonexistent_path = Path("nonexistent_file.jsonl")
        stats = load_intent_stats(nonexistent_path)
        assert stats == {}
    
    def test_load_intent_stats_empty_file(self):
        """Test handling of empty eval results file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            stats = load_intent_stats(temp_path)
            assert stats == {}
        finally:
            temp_path.unlink()
    
    def test_load_intent_stats_malformed_json(self):
        """Test handling of malformed JSON in eval results."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            f.write('{"valid": "json"}\n')
            f.write('invalid json line\n')
            f.write('{"another": "valid"}\n')
            temp_path = Path(f.name)
        
        try:
            stats = load_intent_stats(temp_path)
            # Should return empty dict due to JSON parsing error
            assert stats == {}
        finally:
            temp_path.unlink()


class TestSuggestRetrievalTuning:
    """Test retrieval limit tuning suggestion generation."""
    
    def test_suggest_increase_limit_high_errors(self):
        """Test suggestion to increase limit when retrieval errors are high."""
        config = {
            "intents": {
                "CLIENT_HISTORY": {
                    "retrieval": {"limit": 10}
                }
            }
        }
        
        intent_stats = {
            "CLIENT_HISTORY": IntentStats(
                intent="CLIENT_HISTORY",
                eval_count=15,
                avg_overall_score=6.5,  # Low score
                avg_factual_correctness=7.0,
                avg_grounded_in_context=6.0,
                avg_helpfulness=6.5,
                error_type_distribution={"retrieval": 0.4, "none": 0.6}  # High retrieval errors
            )
        }
        
        suggestions = suggest_retrieval_tuning(config, intent_stats, min_eval_count=10)
        
        assert len(suggestions) == 1
        suggestion = suggestions[0]
        assert suggestion.intent == "CLIENT_HISTORY"
        assert suggestion.current_limit == 10
        assert suggestion.suggested_limit == 15  # 10 + 5 (default step)
        assert "High retrieval error ratio" in suggestion.reason
    
    def test_suggest_decrease_limit_low_errors(self):
        """Test suggestion to decrease limit when performance is excellent."""
        config = {
            "intents": {
                "PRODUCT_INFO": {
                    "retrieval": {"limit": 20}
                }
            }
        }
        
        intent_stats = {
            "PRODUCT_INFO": IntentStats(
                intent="PRODUCT_INFO",
                eval_count=20,
                avg_overall_score=9.0,  # High score
                avg_factual_correctness=9.2,
                avg_grounded_in_context=8.8,
                avg_helpfulness=9.1,
                error_type_distribution={"retrieval": 0.05, "none": 0.95}  # Very low retrieval errors
            )
        }
        
        suggestions = suggest_retrieval_tuning(config, intent_stats, min_eval_count=10)
        
        assert len(suggestions) == 1
        suggestion = suggestions[0]
        assert suggestion.intent == "PRODUCT_INFO"
        assert suggestion.current_limit == 20
        assert suggestion.suggested_limit == 15  # 20 - 5 (default step)
        assert "Low retrieval error ratio" in suggestion.reason
    
    def test_no_suggestion_insufficient_data(self):
        """Test no suggestion when evaluation count is insufficient."""
        config = {"intents": {"TEST_INTENT": {"retrieval": {"limit": 10}}}}
        
        intent_stats = {
            "TEST_INTENT": IntentStats(
                intent="TEST_INTENT",
                eval_count=5,  # Below min_eval_count
                avg_overall_score=6.0,
                avg_factual_correctness=6.0,
                avg_grounded_in_context=6.0,
                avg_helpfulness=6.0,
                error_type_distribution={"retrieval": 0.4}
            )
        }
        
        suggestions = suggest_retrieval_tuning(config, intent_stats, min_eval_count=10)
        assert len(suggestions) == 0
    
    def test_no_suggestion_moderate_performance(self):
        """Test no suggestion when performance is moderate (no clear action needed)."""
        config = {"intents": {"TEST_INTENT": {"retrieval": {"limit": 15}}}}
        
        intent_stats = {
            "TEST_INTENT": IntentStats(
                intent="TEST_INTENT",
                eval_count=20,
                avg_overall_score=8.0,  # Moderate score
                avg_factual_correctness=8.0,
                avg_grounded_in_context=8.0,
                avg_helpfulness=8.0,
                error_type_distribution={"retrieval": 0.2, "none": 0.8}  # Moderate errors
            )
        }
        
        suggestions = suggest_retrieval_tuning(config, intent_stats, min_eval_count=10)
        assert len(suggestions) == 0
    
    def test_respect_max_limit(self):
        """Test that suggestions respect maximum limit constraint."""
        config = {"intents": {"TEST_INTENT": {"retrieval": {"limit": 48}}}}
        
        intent_stats = {
            "TEST_INTENT": IntentStats(
                intent="TEST_INTENT",
                eval_count=15,
                avg_overall_score=6.0,
                avg_factual_correctness=6.0,
                avg_grounded_in_context=6.0,
                avg_helpfulness=6.0,
                error_type_distribution={"retrieval": 0.5}
            )
        }
        
        suggestions = suggest_retrieval_tuning(
            config, intent_stats, min_eval_count=10, max_limit=50, step=5
        )
        
        assert len(suggestions) == 1
        assert suggestions[0].suggested_limit == 50  # Capped at max_limit
    
    def test_custom_parameters(self):
        """Test tuning with custom parameters."""
        config = {"intents": {"TEST_INTENT": {"retrieval": {"limit": 10}}}}
        
        intent_stats = {
            "TEST_INTENT": IntentStats(
                intent="TEST_INTENT",
                eval_count=25,
                avg_overall_score=6.0,
                avg_factual_correctness=6.0,
                avg_grounded_in_context=6.0,
                avg_helpfulness=6.0,
                error_type_distribution={"retrieval": 0.4}
            )
        }
        
        suggestions = suggest_retrieval_tuning(
            config, intent_stats, 
            min_eval_count=20, 
            max_limit=30, 
            step=3
        )
        
        assert len(suggestions) == 1
        assert suggestions[0].suggested_limit == 13  # 10 + 3 (custom step)


class TestApplySuggestionsToConfig:
    """Test applying suggestions to configuration dictionary."""
    
    def test_apply_suggestions_success(self):
        """Test successful application of suggestions to config."""
        config = {
            "intents": {
                "CLIENT_HISTORY": {
                    "retrieval": {"limit": 10}
                },
                "PRODUCT_INFO": {
                    "retrieval": {"limit": 20}
                }
            }
        }
        
        suggestions = [
            TuningSuggestion("CLIENT_HISTORY", 10, 15, "Increase for better recall"),
            TuningSuggestion("PRODUCT_INFO", 20, 15, "Decrease for efficiency")
        ]
        
        updated_config = apply_suggestions_to_config(config, suggestions)
        
        # Verify changes applied
        assert updated_config["intents"]["CLIENT_HISTORY"]["retrieval"]["limit"] == 15
        assert updated_config["intents"]["PRODUCT_INFO"]["retrieval"]["limit"] == 15
        
        # Verify original config unchanged
        assert config["intents"]["CLIENT_HISTORY"]["retrieval"]["limit"] == 10
        assert config["intents"]["PRODUCT_INFO"]["retrieval"]["limit"] == 20
    
    def test_apply_suggestions_new_intent(self):
        """Test applying suggestions for intent not in original config."""
        config = {"intents": {}}
        
        suggestions = [
            TuningSuggestion("NEW_INTENT", 10, 15, "New intent optimization")
        ]
        
        updated_config = apply_suggestions_to_config(config, suggestions)
        
        assert "NEW_INTENT" in updated_config["intents"]
        assert updated_config["intents"]["NEW_INTENT"]["retrieval"]["limit"] == 15
    
    def test_apply_suggestions_empty_config(self):
        """Test applying suggestions to empty config."""
        config = {}
        
        suggestions = [
            TuningSuggestion("TEST_INTENT", 10, 15, "Test suggestion")
        ]
        
        updated_config = apply_suggestions_to_config(config, suggestions)
        
        assert "intents" in updated_config
        assert "TEST_INTENT" in updated_config["intents"]
        assert updated_config["intents"]["TEST_INTENT"]["retrieval"]["limit"] == 15
    
    def test_apply_no_suggestions(self):
        """Test applying empty suggestions list."""
        config = {"intents": {"TEST": {"retrieval": {"limit": 10}}}}
        
        updated_config = apply_suggestions_to_config(config, [])
        
        # Config should be unchanged
        assert updated_config == config
        assert updated_config is not config  # But should be a copy


if __name__ == "__main__":
    pytest.main([__file__, "-v"])