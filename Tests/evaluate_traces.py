#!/usr/bin/env python3
"""
CLI script for evaluating traces using judge model.
Reads traces from traces.jsonl and writes evaluations to eval_results.jsonl.
"""

import json
import asyncio
import argparse
from pathlib import Path
from typing import List
from app.core.tracing import RagTrace, TRACE_FILE
from app.core.evaluation import write_eval, EVAL_FILE
from app.core.judge_client import evaluate_trace
from app.core.llm_client import LLMClient

def load_traces(limit: int = None) -> List[RagTrace]:
    """Load traces from traces.jsonl file."""
    traces = []
    
    if not TRACE_FILE.exists():
        print(f"No trace file found at {TRACE_FILE}")
        return traces
    
    with TRACE_FILE.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if limit and i >= limit:
                break
                
            try:
                data = json.loads(line.strip())
                # Convert dict back to RagTrace
                trace = RagTrace(**data)
                traces.append(trace)
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Error loading trace on line {i+1}: {e}")
                continue
    
    print(f"Loaded {len(traces)} traces")
    return traces

def load_existing_evaluations() -> set:
    """Load existing evaluation trace IDs to avoid re-evaluation."""
    evaluated_ids = set()
    
    if not EVAL_FILE.exists():
        return evaluated_ids
    
    with EVAL_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                evaluated_ids.add(data["trace_id"])
            except (json.JSONDecodeError, KeyError):
                continue
    
    print(f"Found {len(evaluated_ids)} existing evaluations")
    return evaluated_ids

async def evaluate_traces_batch(traces: List[RagTrace], skip_existing: bool = True):
    """Evaluate a batch of traces using judge model."""
    if not traces:
        print("No traces to evaluate")
        return
    
    # Load existing evaluations if skipping
    existing_evals = load_existing_evaluations() if skip_existing else set()
    
    # Filter out already evaluated traces
    traces_to_eval = [t for t in traces if t.trace_id not in existing_evals]
    
    if skip_existing and len(traces_to_eval) < len(traces):
        skipped = len(traces) - len(traces_to_eval)
        print(f"Skipping {skipped} already evaluated traces")
    
    if not traces_to_eval:
        print("All traces already evaluated")
        return
    
    print(f"Evaluating {len(traces_to_eval)} traces...")
    
    # Initialize LLM client for judge model
    llm_client = LLMClient()
    
    successful_evals = 0
    failed_evals = 0
    
    for i, trace in enumerate(traces_to_eval, 1):
        print(f"Evaluating trace {i}/{len(traces_to_eval)}: {trace.trace_id[:8]}...")
        
        try:
            # Evaluate trace
            eval_result = await evaluate_trace(llm_client, trace)
            
            if eval_result:
                # Write evaluation result
                write_eval(eval_result)
                successful_evals += 1
                print(f"  ✓ Score: {eval_result.overall_score:.1f}/10")
            else:
                failed_evals += 1
                print(f"  ✗ Evaluation failed")
                
        except Exception as e:
            failed_evals += 1
            print(f"  ✗ Error: {e}")
    
    print(f"\nEvaluation complete:")
    print(f"  Successful: {successful_evals}")
    print(f"  Failed: {failed_evals}")
    print(f"  Results written to: {EVAL_FILE}")

def print_evaluation_summary():
    """Print summary of evaluation results."""
    if not EVAL_FILE.exists():
        print("No evaluation results found")
        return
    
    scores = []
    error_types = {}
    
    with EVAL_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                scores.append(data["overall_score"])
                error_type = data.get("error_type", "unknown")
                error_types[error_type] = error_types.get(error_type, 0) + 1
            except (json.JSONDecodeError, KeyError):
                continue
    
    if not scores:
        print("No valid evaluation results found")
        return
    
    print(f"\nEvaluation Summary ({len(scores)} evaluations):")
    print(f"  Average Score: {sum(scores)/len(scores):.2f}/10")
    print(f"  Min Score: {min(scores):.1f}/10")
    print(f"  Max Score: {max(scores):.1f}/10")
    
    print(f"\nError Types:")
    for error_type, count in sorted(error_types.items()):
        percentage = (count / len(scores)) * 100
        print(f"  {error_type}: {count} ({percentage:.1f}%)")

async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Evaluate RAG traces using judge model")
    parser.add_argument("--limit", "-l", type=int, help="Limit number of traces to evaluate")
    parser.add_argument("--force", "-f", action="store_true", help="Re-evaluate existing traces")
    parser.add_argument("--summary", "-s", action="store_true", help="Show evaluation summary only")
    
    args = parser.parse_args()
    
    if args.summary:
        print_evaluation_summary()
        return
    
    # Load and evaluate traces
    traces = load_traces(limit=args.limit)
    
    if traces:
        await evaluate_traces_batch(traces, skip_existing=not args.force)
    
    # Show summary
    print_evaluation_summary()

if __name__ == "__main__":
    asyncio.run(main())