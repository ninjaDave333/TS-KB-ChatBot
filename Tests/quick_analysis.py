#!/usr/bin/env python3
"""
Quick analysis of updated traces data
"""

import json
from collections import defaultdict, Counter
from pathlib import Path

def analyze_updated_traces():
    traces_file = Path('d:/Projects/TS-KB-ChatBot/ref_data/traces.jsonl')
    
    with open(traces_file, 'r', encoding='utf-8') as f:
        traces = [json.loads(line) for line in f if line.strip()]
    
    print(f"Total traces: {len(traces)}")
    
    # Analyze by intent
    by_intent = defaultdict(lambda: {'total': 0, 'success': 0})
    routing_methods = Counter()
    
    for trace in traces:
        intent = trace.get('intent', 'unknown')
        has_data = trace.get('neo4j_result_summary', {}).get('has_data', False)
        routing = trace.get('routing_path', 'unknown')
        
        by_intent[intent]['total'] += 1
        if has_data:
            by_intent[intent]['success'] += 1
        
        routing_methods[routing] += 1
    
    print("\nIntent Performance:")
    total_success = 0
    total_queries = 0
    for intent in sorted(by_intent.keys()):
        data = by_intent[intent]
        success_rate = (data['success'] / data['total']) * 100 if data['total'] > 0 else 0
        print(f"  {intent}: {data['total']} queries, {data['success']} successful ({success_rate:.1f}%)")
        total_success += data['success']
        total_queries += data['total']
    
    overall_success = (total_success / total_queries) * 100 if total_queries > 0 else 0
    print(f"\nOverall: {total_success}/{total_queries} successful ({overall_success:.1f}%)")
    
    print("\nRouting Methods:")
    for method, count in routing_methods.most_common():
        percentage = (count / len(traces)) * 100
        print(f"  {method}: {count} ({percentage:.1f}%)")
    
    # Check for recent improvements
    recent_traces = traces[-50:]  # Last 50 traces
    recent_success = sum(1 for t in recent_traces if t.get('neo4j_result_summary', {}).get('has_data', False))
    recent_success_rate = (recent_success / len(recent_traces)) * 100
    print(f"\nRecent Performance (last 50 queries): {recent_success}/{len(recent_traces)} ({recent_success_rate:.1f}%)")

if __name__ == "__main__":
    analyze_updated_traces()