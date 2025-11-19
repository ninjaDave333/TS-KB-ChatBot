"""
Config Auto-Tuning Engine

Analyzes evaluation results to generate intelligent configuration suggestions
for optimizing RAG pipeline performance, starting with retrieval limits.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class IntentStats:
    """Statistics for a specific intent based on evaluation results."""
    intent: str
    eval_count: int
    avg_overall_score: float
    avg_factual_correctness: float
    avg_grounded_in_context: float
    avg_helpfulness: float
    error_type_distribution: Dict[str, float]  # ratios 0.0–1.0


@dataclass
class TuningSuggestion:
    """Suggestion for tuning a configuration parameter."""
    intent: str
    current_limit: int
    suggested_limit: int
    reason: str


def load_intent_stats(eval_results_path: Path) -> Dict[str, IntentStats]:
    """
    Read eval_results.jsonl and return per-intent IntentStats.
    
    Args:
        eval_results_path: Path to eval_results.jsonl file
        
    Returns:
        Dictionary mapping intent names to IntentStats
    """
    if not eval_results_path.exists():
        logger.warning(f"Eval results file not found: {eval_results_path}")
        return {}
    
    intent_data = {}
    
    try:
        with open(eval_results_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                    
                eval_result = json.loads(line)
                intent = eval_result.get('intent', 'UNKNOWN')
                
                if intent not in intent_data:
                    intent_data[intent] = {
                        'scores': [],
                        'factual_scores': [],
                        'grounded_scores': [],
                        'helpful_scores': [],
                        'error_types': []
                    }
                
                # Collect scores
                scores = eval_result.get('scores', {})
                intent_data[intent]['scores'].append(scores.get('overall_score', 0))
                intent_data[intent]['factual_scores'].append(scores.get('factual_correctness', 0))
                intent_data[intent]['grounded_scores'].append(scores.get('grounded_in_context', 0))
                intent_data[intent]['helpful_scores'].append(scores.get('helpfulness', 0))
                
                # Collect error types
                error_type = eval_result.get('primary_issue', 'none')
                intent_data[intent]['error_types'].append(error_type)
    
    except Exception as e:
        logger.error(f"Error loading eval results: {e}")
        return {}
    
    # Convert to IntentStats
    stats = {}
    for intent, data in intent_data.items():
        if not data['scores']:  # Skip empty intents
            continue
            
        eval_count = len(data['scores'])
        
        # Calculate averages
        avg_overall = sum(data['scores']) / eval_count
        avg_factual = sum(data['factual_scores']) / eval_count
        avg_grounded = sum(data['grounded_scores']) / eval_count
        avg_helpful = sum(data['helpful_scores']) / eval_count
        
        # Calculate error distribution
        error_counts = {}
        for error_type in data['error_types']:
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        error_distribution = {
            error_type: count / eval_count 
            for error_type, count in error_counts.items()
        }
        
        stats[intent] = IntentStats(
            intent=intent,
            eval_count=eval_count,
            avg_overall_score=avg_overall,
            avg_factual_correctness=avg_factual,
            avg_grounded_in_context=avg_grounded,
            avg_helpfulness=avg_helpful,
            error_type_distribution=error_distribution
        )
    
    return stats


def suggest_retrieval_tuning(
    config: dict,
    intent_stats: Dict[str, IntentStats],
    min_eval_count: int = 10,
    max_limit: int = 50,
    step: int = 5
) -> List[TuningSuggestion]:
    """
    Generate tuning suggestions for retrieval limits based on intent statistics.
    
    Args:
        config: Current RAG configuration dictionary
        intent_stats: Per-intent statistics from evaluations
        min_eval_count: Minimum evaluations required for suggestions
        max_limit: Maximum allowed retrieval limit
        step: Step size for limit changes
        
    Returns:
        List of tuning suggestions
    """
    suggestions = []
    
    for intent, stats in intent_stats.items():
        # Skip if insufficient data
        if stats.eval_count < min_eval_count:
            logger.debug(f"Skipping {intent}: insufficient eval count ({stats.eval_count} < {min_eval_count})")
            continue
        
        # Get current limit from config
        try:
            current_limit = config.get('intents', {}).get(intent, {}).get('retrieval', {}).get('limit', 10)
        except (KeyError, TypeError):
            current_limit = 10  # Default fallback
        
        # Calculate retrieval error ratio
        retrieval_error_ratio = stats.error_type_distribution.get('retrieval', 0.0)
        
        # Rule 1: Increase limit if high retrieval errors and low scores
        if (retrieval_error_ratio > 0.3 and 
            stats.avg_overall_score < 7.5 and 
            current_limit < max_limit):
            
            suggested_limit = min(current_limit + step, max_limit)
            reason = (f"High retrieval error ratio ({retrieval_error_ratio:.2f}) "
                     f"and low overall score ({stats.avg_overall_score:.1f}); "
                     f"increasing limit from {current_limit} to {suggested_limit}")
            
            suggestions.append(TuningSuggestion(
                intent=intent,
                current_limit=current_limit,
                suggested_limit=suggested_limit,
                reason=reason
            ))
        
        # Rule 2: Decrease limit if low retrieval errors and high scores (optional)
        elif (retrieval_error_ratio < 0.1 and 
              stats.avg_overall_score > 8.5 and 
              current_limit > step):
            
            suggested_limit = max(current_limit - step, step)
            reason = (f"Low retrieval error ratio ({retrieval_error_ratio:.2f}) "
                     f"and high overall score ({stats.avg_overall_score:.1f}); "
                     f"decreasing limit from {current_limit} to {suggested_limit}")
            
            suggestions.append(TuningSuggestion(
                intent=intent,
                current_limit=current_limit,
                suggested_limit=suggested_limit,
                reason=reason
            ))
    
    return suggestions


def apply_suggestions_to_config(
    config: dict, 
    suggestions: List[TuningSuggestion]
) -> dict:
    """
    Apply tuning suggestions to configuration dictionary.
    
    Args:
        config: Configuration dictionary to modify
        suggestions: List of tuning suggestions to apply
        
    Returns:
        Modified configuration dictionary
    """
    # Work on a copy to avoid modifying original
    updated_config = json.loads(json.dumps(config))  # Deep copy via JSON
    
    for suggestion in suggestions:
        # Ensure nested structure exists
        if 'intents' not in updated_config:
            updated_config['intents'] = {}
        if suggestion.intent not in updated_config['intents']:
            updated_config['intents'][suggestion.intent] = {}
        if 'retrieval' not in updated_config['intents'][suggestion.intent]:
            updated_config['intents'][suggestion.intent]['retrieval'] = {}
        
        # Apply the suggestion
        updated_config['intents'][suggestion.intent]['retrieval']['limit'] = suggestion.suggested_limit
        
        logger.info(f"Applied tuning for {suggestion.intent}: "
                   f"{suggestion.current_limit} -> {suggestion.suggested_limit}")
    
    return updated_config