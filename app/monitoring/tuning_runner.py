"""
Config Auto-Tuning CLI Runner

Command-line interface for running config auto-tuning in suggest-only
or apply modes with comprehensive safety guardrails.
"""

import argparse
import json
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List

import yaml

from app.core.config import get_rag_config
from app.monitoring.tuning import (
    IntentStats, 
    TuningSuggestion, 
    load_intent_stats, 
    suggest_retrieval_tuning,
    apply_suggestions_to_config
)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_config_backup(config_path: Path) -> Path:
    """Create timestamped backup of configuration file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = config_path.parent / f"rag_config.backup.{timestamp}.yaml"
    
    shutil.copy2(config_path, backup_path)
    logger.info(f"Created config backup: {backup_path}")
    return backup_path


def write_suggestions_json(suggestions: List[TuningSuggestion], output_path: Path):
    """Write tuning suggestions to JSON file."""
    suggestions_data = [
        {
            "intent": s.intent,
            "current_limit": s.current_limit,
            "suggested_limit": s.suggested_limit,
            "reason": s.reason
        }
        for s in suggestions
    ]
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(suggestions_data, f, indent=2)
    
    logger.info(f"Wrote {len(suggestions)} suggestions to {output_path}")


def write_changes_log(suggestions: List[TuningSuggestion], log_path: Path):
    """Write applied changes to log file."""
    timestamp = datetime.now().isoformat()
    
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"\n=== Tuning Changes Applied: {timestamp} ===\n")
        for suggestion in suggestions:
            f.write(f"Intent: {suggestion.intent}\n")
            f.write(f"  Limit: {suggestion.current_limit} -> {suggestion.suggested_limit}\n")
            f.write(f"  Reason: {suggestion.reason}\n")
        f.write(f"Total changes: {len(suggestions)}\n\n")


def print_suggestions_summary(suggestions: List[TuningSuggestion], intent_stats: dict):
    """Print human-readable summary of suggestions."""
    if not suggestions:
        print("[OK] No tuning suggestions generated - all intents performing optimally")
        return
    
    print(f"\n[TUNING] Generated {len(suggestions)} tuning suggestions:")
    print("=" * 80)
    
    for suggestion in suggestions:
        stats = intent_stats.get(suggestion.intent)
        print(f"\n[INTENT] {suggestion.intent}")
        print(f"   Current limit: {suggestion.current_limit}")
        print(f"   Suggested limit: {suggestion.suggested_limit}")
        print(f"   Reason: {suggestion.reason}")
        
        if stats:
            print(f"   Evaluations: {stats.eval_count}")
            print(f"   Avg score: {stats.avg_overall_score:.1f}")
            retrieval_errors = stats.error_type_distribution.get('retrieval', 0.0)
            print(f"   Retrieval errors: {retrieval_errors:.1%}")
    
    print("=" * 80)


def run_suggest_mode(args) -> List[TuningSuggestion]:
    """Run tuning in suggest-only mode."""
    logger.info("Running tuning in suggest-only mode")
    
    # Load current config
    try:
        config = get_rag_config()
        logger.info("Loaded current RAG configuration")
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return []
    
    # Load evaluation stats
    eval_results_path = Path("data/eval_results.jsonl")
    intent_stats = load_intent_stats(eval_results_path)
    
    if not intent_stats:
        logger.warning("No evaluation data found - cannot generate suggestions")
        return []
    
    logger.info(f"Loaded stats for {len(intent_stats)} intents")
    
    # Generate suggestions
    suggestions = suggest_retrieval_tuning(
        config=config,
        intent_stats=intent_stats,
        min_eval_count=args.min_eval_count,
        max_limit=args.max_limit,
        step=args.step
    )
    
    # Write suggestions to JSON
    suggestions_path = Path("data/tuning_suggestions.json")
    write_suggestions_json(suggestions, suggestions_path)
    
    # Print summary
    print_suggestions_summary(suggestions, intent_stats)
    
    return suggestions


def run_apply_mode(args) -> bool:
    """Run tuning in apply mode with guardrails."""
    logger.info("Running tuning in apply mode")
    
    # First run suggest mode to get suggestions
    suggestions = run_suggest_mode(args)
    
    if not suggestions:
        logger.info("No suggestions to apply")
        return True
    
    # Apply guardrail: limit number of simultaneous changes
    max_changes = getattr(args, 'max_changes', 10)
    if len(suggestions) > max_changes:
        logger.warning(f"Limiting changes to {max_changes} (from {len(suggestions)})")
        suggestions = suggestions[:max_changes]
    
    # Load current config for modification
    try:
        config = get_rag_config()
        config_path = Path("config/rag_config.yaml")
    except Exception as e:
        logger.error(f"Failed to load config for modification: {e}")
        return False
    
    # Create backup
    try:
        backup_path = create_config_backup(config_path)
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        return False
    
    # Apply suggestions
    try:
        updated_config = apply_suggestions_to_config(config, suggestions)
        
        # Write updated config
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(updated_config, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Applied {len(suggestions)} configuration changes")
        
        # Log changes
        log_path = Path("data/tuning_changes.log")
        write_changes_log(suggestions, log_path)
        
        print(f"\n[SUCCESS] Applied {len(suggestions)} tuning changes")
        print(f"[BACKUP] Created: {backup_path}")
        print(f"[LOG] Changes logged: {log_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to apply changes: {e}")
        print(f"\n[ERROR] Failed to apply changes: {e}")
        print(f"[ROLLBACK] Configuration unchanged, backup available: {backup_path}")
        return False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="RAG Config Auto-Tuning System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate suggestions only (dry run)
  python -m app.monitoring.tuning_runner --suggest-only
  
  # Apply tuning changes with custom parameters
  python -m app.monitoring.tuning_runner --apply --min-eval-count 15 --max-limit 40
  
  # Conservative tuning with small steps
  python -m app.monitoring.tuning_runner --apply --step 3 --max-changes 5
        """
    )
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        '--suggest-only', 
        action='store_true',
        help='Generate suggestions without applying changes (dry run)'
    )
    mode_group.add_argument(
        '--apply', 
        action='store_true',
        help='Apply tuning changes with automatic backup'
    )
    
    # Tuning parameters
    parser.add_argument(
        '--min-eval-count', 
        type=int, 
        default=10,
        help='Minimum evaluations required per intent (default: 10)'
    )
    parser.add_argument(
        '--max-limit', 
        type=int, 
        default=50,
        help='Maximum retrieval limit allowed (default: 50)'
    )
    parser.add_argument(
        '--step', 
        type=int, 
        default=5,
        help='Step size for limit changes (default: 5)'
    )
    parser.add_argument(
        '--max-changes', 
        type=int, 
        default=10,
        help='Maximum number of simultaneous changes (default: 10)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.suggest_only:
            suggestions = run_suggest_mode(args)
            sys.exit(0 if suggestions is not None else 1)
        elif args.apply:
            success = run_apply_mode(args)
            sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Tuning cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()