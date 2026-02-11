#!/usr/bin/env python3
"""
Examine trace structure to understand available fields
"""

import json
from pathlib import Path

def examine_trace_structure():
    traces_file = Path('ref_data/traces.jsonl')
    
    with open(traces_file, 'r', encoding='utf-8') as f:
        traces = [json.loads(line) for line in f if line.strip()]
    
    print("Sample trace structure:")
    if traces:
        sample = traces[0]
        print("Available fields:")
        for key, value in sample.items():
            if isinstance(value, str) and len(value) > 100:
                print(f"  {key}: {type(value).__name__} (length: {len(value)})")
            else:
                print(f"  {key}: {value}")
        
        print(f"\nSample cypher_query:")
        print(f"  {sample.get('cypher_query', 'Not found')}")
        
        print(f"\nSample routing_path:")
        print(f"  {sample.get('routing_path', 'Not found')}")

if __name__ == "__main__":
    examine_trace_structure()