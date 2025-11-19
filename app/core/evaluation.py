"""
Judge model evaluation for RAG pipeline quality assessment.
Provides structured scoring and error classification.
"""

from dataclasses import dataclass, asdict
from typing import Optional
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

EVAL_FILE = Path("/app/data/eval_results.jsonl")

@dataclass
class EvalResult:
    """Structured evaluation result from judge model."""
    trace_id: str
    overall_score: float
    factual_correctness: float
    grounded_in_context: float
    helpfulness: float
    error_type: str  # "retrieval" | "reasoning" | "missing_knowledge" | "none"
    raw_judge_response: Optional[str] = None

def write_eval(eval_result: EvalResult) -> None:
    """Write evaluation result to JSONL file. Fails gracefully."""
    try:
        EVAL_FILE.parent.mkdir(parents=True, exist_ok=True)
        with EVAL_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(eval_result)) + "\n")
    except Exception as e:
        logger.warning(f"Failed to write eval result {eval_result.trace_id}: {e}")

def safe_write_eval(eval_result: EvalResult) -> None:
    """Safely write evaluation result with error handling."""
    try:
        write_eval(eval_result)
    except Exception as e:
        logger.warning(f"Evaluation writing failed for {eval_result.trace_id}: {e}")
        # Continue normal operation - evaluation must not break the app