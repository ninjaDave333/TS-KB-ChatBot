#!/usr/bin/env python3
"""
Analyze user feedback tags in traces to identify improvement opportunities
"""

import json
from collections import Counter, defaultdict

def analyze_feedback_tags():
    """Find queries tagged as 'almost' or 'not helpful'"""
    
    with open('ref_data/traces.jsonl', 'r') as f:
        traces = [json.loads(line) for line in f if line.strip()]
    
    feedback_analysis = {
        'almost': [],
        'not_helpful': [],
        'helpful': [],
        'no_feedback': []
    }
    
    intent_feedback = defaultdict(lambda: {'almost': 0, 'not_helpful': 0, 'helpful': 0})
    
    for trace in traces:
        feedback = trace.get('user_feedback', {})
        rating = feedback.get('rating', 'no_feedback')
        intent = trace.get('intent', 'unknown')
        
        query_info = {
            'trace_id': trace.get('trace_id'),
            'intent': intent,
            'question': trace.get('question', '')[:100],
            'cypher': trace.get('cypher_query', '')[:100],
            'has_data': trace.get('neo4j_result_summary', {}).get('has_data', False),
            'record_count': trace.get('neo4j_result_summary', {}).get('record_count', 0)
        }
        
        if rating == 'almost':
            feedback_analysis['almost'].append(query_info)
            intent_feedback[intent]['almost'] += 1
        elif rating == 'not_helpful':
            feedback_analysis['not_helpful'].append(query_info)
            intent_feedback[intent]['not_helpful'] += 1
        elif rating == 'helpful':
            feedback_analysis['helpful'].append(query_info)
            intent_feedback[intent]['helpful'] += 1
        else:
            feedback_analysis['no_feedback'].append(query_info)
    
    return feedback_analysis, dict(intent_feedback)

def print_analysis():
    feedback_data, intent_breakdown = analyze_feedback_tags()
    
    print("USER FEEDBACK ANALYSIS")
    print("=" * 50)
    
    for category, queries in feedback_data.items():
        if category == 'no_feedback':
            continue
            
        print(f"\n{category.upper()} ({len(queries)} queries)")
        print("-" * 30)
        
        if not queries:
            print("   No queries found")
            continue
            
        for i, q in enumerate(queries[:5], 1):
            status = "OK" if q['has_data'] else "FAIL"
            print(f"{i}. {status} [{q['intent']}] {q['question']}")
            if q['cypher']:
                print(f"   Cypher: {q['cypher']}...")
            print(f"   Records: {q['record_count']}")
            print()
    
    print("\nFEEDBACK BY INTENT")
    print("-" * 30)
    for intent, counts in intent_breakdown.items():
        total_feedback = counts['almost'] + counts['not_helpful'] + counts['helpful']
        if total_feedback > 0:
            print(f"{intent}: {counts['helpful']} helpful, {counts['almost']} almost, {counts['not_helpful']} not helpful")

if __name__ == "__main__":
    print_analysis()