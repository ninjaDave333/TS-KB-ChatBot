"""
Structured tracing for RAG pipeline execution.
Captures comprehensive execution data for analysis and optimization.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, Optional
import json
from pathlib import Path
import uuid
import logging

logger = logging.getLogger(__name__)

TRACE_FILE = Path("/app/data/traces.jsonl")

@dataclass
class RagTrace:
    """Comprehensive trace of RAG pipeline execution."""
    trace_id: str
    timestamp: str
    intent: Optional[str]
    use_ai: bool
    routing_path: Optional[str]
    
    retrieval_config: Dict[str, Any]
    cypher_query: Optional[str]
    cypher_params: Dict[str, Any]
    neo4j_result_summary: Dict[str, Any]
    
    prompt_system: Optional[str]
    prompt_user: Optional[str]
    llm_model_role: Optional[str]   # "primary", "judge", etc.
    llm_model_id: Optional[str]
    
    final_answer: Optional[str]

def new_trace(intent: Optional[str], use_ai: bool, routing_path: Optional[str]) -> RagTrace:
    """Create a new RAG trace with default values."""
    return RagTrace(
        trace_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow().isoformat(),
        intent=intent,
        use_ai=use_ai,
        routing_path=routing_path,
        retrieval_config={},
        cypher_query=None,
        cypher_params={},
        neo4j_result_summary={},
        prompt_system=None,
        prompt_user=None,
        llm_model_role=None,
        llm_model_id=None,
        final_answer=None,
    )

def write_trace(trace: RagTrace) -> None:
    """Write trace to JSONL file. Fails gracefully to not break production."""
    try:
        TRACE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with TRACE_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(trace)) + "\n")
    except Exception as e:
        logger.warning(f"Failed to write trace {trace.trace_id}: {e}")

def safe_write_trace(trace: RagTrace) -> None:
    """Safely write trace with error handling for production use."""
    try:
        write_trace(trace)
    except Exception as e:
        logger.warning(f"Tracing failed for {trace.trace_id}: {e}")
        # Continue normal operation - tracing must not break the app