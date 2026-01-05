#!/usr/bin/env python3
"""
Analyze failed general queries from production traces
"""

import json

def analyze_failed_general():
    failed_general = []
    with open('ref_data/traces.jsonl') as f:
        for line in f:
            trace = json.loads(line)
            if trace.get('intent') == 'general' and not trace.get('neo4j_result_summary', {}).get('has_data', False):
                failed_general.append(trace.get('cypher_query', 'No query'))
    
    print(f'Failed general queries ({len(failed_general)}):')
    for i, query in enumerate(failed_general[:10], 1):
        print(f'{i}. {query[:100]}...')

if __name__ == "__main__":
    analyze_failed_general()