#!/usr/bin/env python3
"""
Find immediate improvement opportunities from current trace data
"""

import json
from collections import Counter, defaultdict

def analyze_improvement_opportunities():
    """Find patterns in current data that can be improved immediately"""
    
    with open('ref_data/traces.jsonl', 'r') as f:
        traces = [json.loads(line) for line in f if line.strip()]
    
    # 1. Failed queries by intent
    failed_by_intent = defaultdict(list)
    
    # 2. Low data return queries (successful but minimal results)
    low_data_queries = []
    
    # 3. Repeated query patterns
    query_patterns = Counter()
    
    for trace in traces:
        intent = trace.get('intent', 'unknown')
        has_data = trace.get('neo4j_result_summary', {}).get('has_data', False)
        record_count = trace.get('neo4j_result_summary', {}).get('record_count', 0)
        question = trace.get('question', '')
        cypher = trace.get('cypher_query', '')
        
        # Failed queries
        if not has_data:
            failed_by_intent[intent].append({
                'question': question[:80],
                'cypher': cypher[:80] if cypher else 'No query'
            })
        
        # Low data return (1-3 records)
        elif 1 <= record_count <= 3:
            low_data_queries.append({
                'intent': intent,
                'question': question[:80],
                'records': record_count
            })
        
        # Pattern extraction for repeated queries
        if question:
            # Simple pattern matching
            q_lower = question.lower()
            if 'list' in q_lower and 'client' in q_lower:
                query_patterns['list_clients'] += 1
            elif 'count' in q_lower:
                query_patterns['count_queries'] += 1
            elif 'meeting' in q_lower or 'recording' in q_lower:
                query_patterns['meeting_queries'] += 1
            elif 'product' in q_lower or 'vendor' in q_lower:
                query_patterns['product_queries'] += 1
            else:
                query_patterns['other'] += 1
    
    return failed_by_intent, low_data_queries, query_patterns

def print_opportunities():
    failed_queries, low_data, patterns = analyze_improvement_opportunities()
    
    print("IMMEDIATE IMPROVEMENT OPPORTUNITIES")
    print("=" * 50)
    
    # 1. Failed queries by intent
    print("\n1. FAILED QUERIES BY INTENT")
    print("-" * 30)
    for intent, failures in failed_queries.items():
        if failures:
            print(f"\n{intent.upper()} ({len(failures)} failures):")
            for i, f in enumerate(failures[:3], 1):
                print(f"  {i}. {f['question']}")
                if f['cypher'] != 'No query':
                    print(f"     Query: {f['cypher']}...")
    
    # 2. Low data return queries
    print(f"\n2. LOW DATA RETURN QUERIES ({len(low_data)} queries)")
    print("-" * 30)
    intent_low_data = defaultdict(int)
    for q in low_data:
        intent_low_data[q['intent']] += 1
    
    for intent, count in intent_low_data.items():
        print(f"{intent}: {count} queries with 1-3 records")
    
    # 3. Query patterns for learned patterns
    print(f"\n3. REPEATED QUERY PATTERNS")
    print("-" * 30)
    for pattern, count in patterns.most_common():
        if count > 5:  # Patterns with >5 occurrences
            print(f"{pattern}: {count} queries (candidate for learned pattern)")
    
    # 4. Specific recommendations
    print(f"\n4. ACTIONABLE RECOMMENDATIONS")
    print("-" * 30)
    
    # General intent issues
    general_failures = len(failed_queries.get('general', []))
    if general_failures > 5:
        print(f"- Fix general intent classification ({general_failures} failures)")
    
    # Pattern learning opportunities
    high_volume_patterns = [p for p, c in patterns.items() if c > 10]
    if high_volume_patterns:
        print(f"- Create learned patterns for: {', '.join(high_volume_patterns)}")
    
    # Low data queries
    if len(low_data) > 10:
        print(f"- Investigate {len(low_data)} queries returning minimal data")

if __name__ == "__main__":
    print_opportunities()