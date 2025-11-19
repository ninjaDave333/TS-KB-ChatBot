#!/usr/bin/env python3
"""
Evaluation daemon for continuous RAG quality monitoring.
Reads traces.jsonl, evaluates new traces with judge model, writes results and metrics.
"""

import json
import asyncio
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set, Optional
from dataclasses import asdict

from app.core.llm_client import LLMClient
from app.core.tracing import RagTrace, TRACE_FILE
from app.core.evaluation import EvalResult, EVAL_FILE, write_eval
from app.core.judge_client import evaluate_trace

logger = logging.getLogger(__name__)

SUMMARY_FILE = Path("/app/data/eval_summary.json")

class EvalRunner:
    """Evaluation daemon for continuous trace monitoring."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    def load_existing_evaluations(self) -> Set[str]:
        """Load set of already evaluated trace IDs."""
        evaluated_ids = set()
        
        if not EVAL_FILE.exists():
            return evaluated_ids
        
        try:
            with EVAL_FILE.open("r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        evaluated_ids.add(data["trace_id"])
                    except (json.JSONDecodeError, KeyError):
                        continue
        except Exception as e:
            logger.warning(f"Failed to load existing evaluations: {e}")
        
        logger.info(f"Found {len(evaluated_ids)} existing evaluations")
        return evaluated_ids
    
    def load_traces(self, max_traces: Optional[int] = None, 
                   intent_filter: Optional[str] = None,
                   since: Optional[str] = None) -> List[RagTrace]:
        """Load traces from traces.jsonl with filtering."""
        traces = []
        
        if not TRACE_FILE.exists():
            logger.info("No trace file found")
            return traces
        
        # Parse since timestamp if provided
        since_dt = None
        if since:
            try:
                since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
            except ValueError:
                logger.error(f"Invalid timestamp format: {since}")
                return traces
        
        try:
            with TRACE_FILE.open("r", encoding="utf-8") as f:
                for line in f:
                    if max_traces and len(traces) >= max_traces:
                        break
                    
                    try:
                        data = json.loads(line.strip())
                        
                        # Apply filters
                        if intent_filter and data.get("intent") != intent_filter:
                            continue
                        
                        if since_dt:
                            trace_dt = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
                            if trace_dt <= since_dt:
                                continue
                        
                        # Convert to RagTrace
                        trace = RagTrace(**data)
                        traces.append(trace)
                        
                    except (json.JSONDecodeError, TypeError) as e:
                        logger.warning(f"Failed to parse trace: {e}")
                        continue
        except Exception as e:
            logger.error(f"Failed to load traces: {e}")
        
        logger.info(f"Loaded {len(traces)} traces")
        return traces
    
    def filter_unevaluated_traces(self, traces: List[RagTrace], 
                                 evaluated_ids: Set[str]) -> List[RagTrace]:
        """Filter out already evaluated traces."""
        unevaluated = [t for t in traces if t.trace_id not in evaluated_ids]
        logger.info(f"Found {len(unevaluated)} unevaluated traces")
        return unevaluated
    
    async def evaluate_batch(self, traces: List[RagTrace]) -> List[EvalResult]:
        """Evaluate a batch of traces with error handling."""
        results = []
        
        for i, trace in enumerate(traces, 1):
            logger.info(f"Evaluating trace {i}/{len(traces)}: {trace.trace_id[:8]}")
            
            try:
                eval_result = await evaluate_trace(self.llm_client, trace)
                
                if eval_result:
                    write_eval(eval_result)
                    results.append(eval_result)
                    logger.info(f"  ✓ Score: {eval_result.overall_score:.1f}/10")
                else:
                    logger.warning(f"  ✗ Evaluation failed for {trace.trace_id}")
                    
            except Exception as e:
                logger.error(f"  ✗ Error evaluating {trace.trace_id}: {e}")
                continue
        
        logger.info(f"Successfully evaluated {len(results)}/{len(traces)} traces")
        return results
    
    def generate_metrics_summary(self) -> Dict:
        """Generate aggregated metrics from all evaluations."""
        if not EVAL_FILE.exists():
            return {"error": "No evaluation results found"}
        
        evaluations = []
        
        try:
            with EVAL_FILE.open("r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        evaluations.append(data)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"Failed to read evaluations: {e}")
            return {"error": str(e)}
        
        if not evaluations:
            return {"error": "No valid evaluations found"}
        
        # Global metrics
        total_evals = len(evaluations)
        avg_overall = sum(e["overall_score"] for e in evaluations) / total_evals
        avg_factual = sum(e["factual_correctness"] for e in evaluations) / total_evals
        avg_grounded = sum(e["grounded_in_context"] for e in evaluations) / total_evals
        avg_helpful = sum(e["helpfulness"] for e in evaluations) / total_evals
        
        # Group by intent (need to match with traces)
        by_intent = {}
        trace_intents = self._load_trace_intents()
        
        for eval_data in evaluations:
            trace_id = eval_data["trace_id"]
            intent = trace_intents.get(trace_id, "unknown")
            
            if intent not in by_intent:
                by_intent[intent] = []
            by_intent[intent].append(eval_data)
        
        # Calculate per-intent metrics
        intent_metrics = {}
        for intent, intent_evals in by_intent.items():
            count = len(intent_evals)
            
            # Error type distribution
            error_counts = {}
            for eval_data in intent_evals:
                error_type = eval_data.get("error_type", "unknown")
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
            
            error_distribution = {
                error_type: count / len(intent_evals)
                for error_type, count in error_counts.items()
            }
            
            intent_metrics[intent] = {
                "eval_count": count,
                "avg_overall_score": sum(e["overall_score"] for e in intent_evals) / count,
                "avg_factual_correctness": sum(e["factual_correctness"] for e in intent_evals) / count,
                "avg_grounded_in_context": sum(e["grounded_in_context"] for e in intent_evals) / count,
                "avg_helpfulness": sum(e["helpfulness"] for e in intent_evals) / count,
                "error_type_distribution": error_distribution
            }
        
        summary = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "global": {
                "total_evals": total_evals,
                "avg_overall_score": round(avg_overall, 2),
                "avg_factual_correctness": round(avg_factual, 2),
                "avg_grounded_in_context": round(avg_grounded, 2),
                "avg_helpfulness": round(avg_helpful, 2)
            },
            "by_intent": intent_metrics
        }
        
        return summary
    
    def _load_trace_intents(self) -> Dict[str, str]:
        """Load mapping of trace_id to intent from traces.jsonl."""
        trace_intents = {}
        
        if not TRACE_FILE.exists():
            return trace_intents
        
        try:
            with TRACE_FILE.open("r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        trace_intents[data["trace_id"]] = data.get("intent", "unknown")
                    except (json.JSONDecodeError, KeyError):
                        continue
        except Exception as e:
            logger.warning(f"Failed to load trace intents: {e}")
        
        return trace_intents
    
    def write_summary(self, summary: Dict) -> None:
        """Write metrics summary to file."""
        try:
            SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
            with SUMMARY_FILE.open("w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)
            logger.info(f"Metrics summary written to {SUMMARY_FILE}")
        except Exception as e:
            logger.error(f"Failed to write summary: {e}")
    
    async def run(self, max_traces: Optional[int] = None,
                  intent_filter: Optional[str] = None,
                  since: Optional[str] = None,
                  dry_run: bool = False) -> None:
        """Run evaluation daemon with specified parameters."""
        logger.info("Starting evaluation runner")
        
        # Load existing evaluations
        evaluated_ids = self.load_existing_evaluations()
        
        # Load and filter traces
        all_traces = self.load_traces(max_traces, intent_filter, since)
        unevaluated_traces = self.filter_unevaluated_traces(all_traces, evaluated_ids)
        
        if not unevaluated_traces:
            logger.info("No unevaluated traces found")
            # Still generate summary from existing data
            summary = self.generate_metrics_summary()
            self.write_summary(summary)
            return
        
        if dry_run:
            logger.info(f"DRY RUN: Would evaluate {len(unevaluated_traces)} traces")
            for trace in unevaluated_traces:
                logger.info(f"  - {trace.trace_id[:8]} (intent: {trace.intent})")
            return
        
        # Evaluate traces
        results = await self.evaluate_batch(unevaluated_traces)
        
        # Generate and write summary
        summary = self.generate_metrics_summary()
        self.write_summary(summary)
        
        logger.info(f"Evaluation complete: {len(results)} traces evaluated")

async def main():
    """CLI entry point for evaluation runner."""
    parser = argparse.ArgumentParser(description="RAG Evaluation Daemon")
    parser.add_argument("--max-traces", type=int, help="Maximum traces to evaluate")
    parser.add_argument("--intent-filter", help="Filter by specific intent")
    parser.add_argument("--since", help="Evaluate traces since timestamp (ISO format)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without evaluation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        # Initialize LLM client
        llm_client = LLMClient()
        
        # Run evaluation
        runner = EvalRunner(llm_client)
        await runner.run(
            max_traces=args.max_traces,
            intent_filter=args.intent_filter,
            since=args.since,
            dry_run=args.dry_run
        )
        
    except Exception as e:
        logger.error(f"Evaluation runner failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))