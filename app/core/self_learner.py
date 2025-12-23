"""
Self-learning module - analyzes failures and suggests prompt improvements.
Runs manually to learn from production errors.
"""
import json
from typing import List, Dict, Any
from collections import defaultdict, Counter
from pathlib import Path
from .metrics_collector import metrics_collector

def analyze_failures() -> Dict[str, Any]:
    """Analyze recent failures and extract patterns."""
    metrics = metrics_collector.get_metrics()
    all_queries = metrics['recent_queries']
    failures = [q for q in all_queries if not q['success']]
    
    # Group by error type
    error_patterns = defaultdict(list)
    for failure in failures:
        error_patterns[failure['error']].append({
            'query': failure['query'],
            'intent': failure['intent'],
            'timestamp': failure['timestamp']
        })
    
    # Analyze validation retries
    retry_queries = [q for q in all_queries if q['validation_attempts'] > 1]
    
    return {
        'total_queries': len(all_queries),
        'total_failures': len(failures),
        'failure_rate': round(len(failures) / len(all_queries) * 100, 1) if all_queries else 0,
        'error_breakdown': {k: len(v) for k, v in error_patterns.items()},
        'error_details': dict(error_patterns),
        'retry_count': len(retry_queries),
        'retry_queries': retry_queries
    }

def analyze_user_feedback() -> Dict[str, Any]:
    """Analyze user feedback patterns."""
    feedback_file = Path('/app/logs/persistentData/user_feedback.jsonl')
    if not feedback_file.exists():
        return {'error': 'No feedback data found'}
    
    feedback_data = []
    with open(feedback_file, 'r') as f:
        for line in f:
            feedback_data.append(json.loads(line))
    
    # Group by rating type
    helpful = [f for f in feedback_data if f['rating'] == 'helpful']
    almost = [f for f in feedback_data if f['rating'] == 'almost']
    not_helpful = [f for f in feedback_data if f['rating'] == 'not_helpful']
    
    # Group almost/not_helpful by intent for analysis
    almost_by_intent = defaultdict(list)
    not_helpful_by_intent = defaultdict(list)
    
    for f in almost:
        almost_by_intent[f.get('intent', 'unknown')].append(f['query'])
    for f in not_helpful:
        not_helpful_by_intent[f.get('intent', 'unknown')].append(f['query'])
    
    total = len(feedback_data)
    satisfaction_rate = round((len(helpful) / total * 100), 1) if total else 0
    partial_rate = round((len(almost) / total * 100), 1) if total else 0
    
    return {
        'total_feedback': total,
        'helpful_count': len(helpful),
        'almost_count': len(almost),
        'not_helpful_count': len(not_helpful),
        'satisfaction_rate': satisfaction_rate,
        'partial_success_rate': partial_rate,
        'almost_by_intent': {k: len(v) for k, v in almost_by_intent.items()},
        'not_helpful_by_intent': {k: len(v) for k, v in not_helpful_by_intent.items()},
        'almost_queries': dict(almost_by_intent),
        'not_helpful_queries': dict(not_helpful_by_intent)
    }

def analyze_intent_accuracy() -> Dict[str, Any]:
    """Analyze intent classification patterns."""
    metrics = metrics_collector.get_metrics()
    intent_dist = metrics['intent_distribution']
    
    # Check for unknown intent (misclassification indicator)
    unknown_count = intent_dist.get('unknown', 0)
    total = sum(intent_dist.values())
    
    return {
        'intent_distribution': intent_dist,
        'unknown_rate': round(unknown_count / total * 100, 1) if total else 0,
        'most_common': max(intent_dist.items(), key=lambda x: x[1])[0] if intent_dist else None
    }

def suggest_improvements() -> Dict[str, List[str]]:
    """Generate actionable suggestions based on analysis."""
    failures = analyze_failures()
    feedback = analyze_user_feedback()
    intent = analyze_intent_accuracy()
    
    suggestions = {
        'prompt_rules': [],
        'intent_keywords': [],
        'schema_hints': [],
        'few_shot_examples': []
    }
    
    # Suggest based on error patterns
    if failures['error_breakdown'].get('CypherSyntaxError', 0) > 2:
        suggestions['prompt_rules'].append(
            "High syntax errors detected. Review RULES_SUMMARY for common patterns."
        )
    
    if failures['error_breakdown'].get('CypherTypeError', 0) > 2:
        suggestions['prompt_rules'].append(
            "Type errors detected. Add explicit type casting examples (toFloat, date())."
        )
    
    # Suggest based on retries
    if failures['retry_count'] > 5:
        suggestions['prompt_rules'].append(
            f"{failures['retry_count']} queries needed retries. Review validation rules."
        )
    
    # Suggest based on intent accuracy
    if intent['unknown_rate'] > 10:
        suggestions['intent_keywords'].append(
            f"Unknown intent rate: {intent['unknown_rate']}%. Add keywords to classifier."
        )
    
    # Suggest based on negative feedback
    if feedback.get('almost_count', 0) > 3:
        suggestions['few_shot_examples'].append(
            f"{feedback['almost_count']} 'almost' ratings. Queries partially correct - review for missing details."
        )
    
    if feedback.get('not_helpful_count', 0) > 3:
        suggestions['prompt_rules'].append(
            f"{feedback['not_helpful_count']} 'not helpful' ratings. Review failed queries and add examples."
        )
    
    return suggestions

def generate_report() -> Dict[str, Any]:
    """Generate comprehensive self-learning analysis report."""
    return {
        'timestamp': metrics_collector.get_metrics()['last_updated'],
        'failure_analysis': analyze_failures(),
        'feedback_analysis': analyze_user_feedback(),
        'intent_analysis': analyze_intent_accuracy(),
        'suggestions': suggest_improvements()
    }

def save_report(output_file: str = '/app/data/self_learning_report.json'):
    """Generate and save analysis report."""
    report = generate_report()
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    return output_file
