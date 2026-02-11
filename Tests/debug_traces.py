#!/usr/bin/env python3
"""
Debug script to examine trace data and understand pattern detection issues
"""

import json
from pathlib import Path
from collections import defaultdict, Counter

def debug_traces():
    traces_file = Path('ref_data/traces.jsonl')
    
    with open(traces_file, 'r', encoding='utf-8') as f:
        traces = [json.loads(line) for line in f if line.strip()]
    
    print(f"Total traces: {len(traces)}")
    
    # Check successful AI-generated queries
    successful_ai = []
    for trace in traces:
        if (trace.get('neo4j_result_summary', {}).get('has_data', False) and 
            trace.get('cypher_query') and 
            trace.get('routing_path') == 'ai_generated'):
            successful_ai.append(trace)
    
    print(f"Successful AI-generated queries: {len(successful_ai)}")
    
    # Group by intent
    by_intent = defaultdict(list)
    for trace in successful_ai:
        intent = trace.get('intent', 'unknown')
        by_intent[intent].append(trace)
    
    print("\nSuccessful queries by intent:")
    for intent, queries in by_intent.items():
        print(f"  {intent}: {len(queries)} queries")
        
        if len(queries) >= 2:
            print(f"    Sample queries:")
            for i, q in enumerate(queries[:3]):
                query_text = q.get('query', 'No query text')
                print(f"      {i+1}. \"{query_text[:60]}...\"")
            
            # Check for exact Cypher matches
            cypher_counts = Counter()
            for q in queries:
                cypher = q.get('cypher_query', '').strip()
                if cypher:
                    cypher_counts[cypher] += 1
            
            exact_matches = [(cypher, count) for cypher, count in cypher_counts.items() if count >= 2]
            if exact_matches:
                print(f"    Exact Cypher matches found: {len(exact_matches)}")
                for cypher, count in exact_matches[:2]:
                    print(f"      Used {count} times: {cypher[:80]}...")
            else:
                print(f"    No exact Cypher matches found")
        print()

if __name__ == "__main__":
    debug_traces()