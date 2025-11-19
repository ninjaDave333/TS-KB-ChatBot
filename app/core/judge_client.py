"""Judge model client for quality assessment and evaluation."""

import json
import logging
from typing import Dict, Any, Optional
from .llm_client import LLMClient
from .tracing import RagTrace
from .evaluation import EvalResult

logger = logging.getLogger(__name__)

async def judge_answer(llm_client: LLMClient, question: str, answer: str, context: str) -> Dict[str, Any]:
    """Evaluate answer quality using judge model.
    
    Args:
        llm_client: LLMClient instance for judge model calls
        question: Original user question
        answer: Generated answer to evaluate
        context: Context used for answer generation
        
    Returns:
        Dict with evaluation results
    """
    try:
        # Build evaluation prompt
        system_prompt = """You are an expert evaluator for RAG systems. Evaluate answer quality and return ONLY valid JSON.

Return exactly this JSON format with no additional text:
{
  "overall_score": 8.5,
  "factual_correctness": 9.0,
  "grounded_in_context": 8.0,
  "helpfulness": 8.5,
  "error_type": "none"
}

Use scores 0-10 (float). Error types: retrieval, reasoning, missing_knowledge, none.
Return ONLY the JSON object, no explanations."""
        
        user_prompt = f"""Question: {question}
Answer: {answer}
Context: {context[:200] if context else 'No context'}

JSON evaluation:"""
        
        # Call judge model
        response = await llm_client.complete(system_prompt, user_prompt, role="judge")
        
        # Parse JSON response
        try:
            eval_data = json.loads(response.strip())
            return {
                "status": "success",
                "evaluation": eval_data,
                "raw_response": response
            }
        except json.JSONDecodeError as e:
            logger.warning(f"Judge model returned invalid JSON: {e}")
            return {
                "status": "json_error",
                "error": str(e),
                "raw_response": response
            }
            
    except Exception as e:
        logger.error(f"Judge evaluation failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

async def evaluate_trace(llm_client: LLMClient, trace: RagTrace) -> Optional[EvalResult]:
    """Evaluate a complete RAG trace using judge model.
    
    Args:
        llm_client: LLMClient instance
        trace: Complete RAG trace to evaluate
        
    Returns:
        EvalResult or None if evaluation fails
    """
    try:
        # Extract question from trace (could be in prompt_user or other fields)
        question = trace.prompt_user or "Unknown question"
        answer = trace.final_answer or "No answer generated"
        
        # Build context summary from trace
        context_parts = []
        if trace.cypher_query:
            context_parts.append(f"Cypher: {trace.cypher_query}")
        if trace.neo4j_result_summary:
            context_parts.append(f"Results: {trace.neo4j_result_summary}")
        context = " | ".join(context_parts)
        
        # Call judge evaluation
        judge_result = await judge_answer(llm_client, question, answer, context)
        
        if judge_result["status"] == "success":
            eval_data = judge_result["evaluation"]
            return EvalResult(
                trace_id=trace.trace_id,
                overall_score=float(eval_data.get("overall_score", 0)),
                factual_correctness=float(eval_data.get("factual_correctness", 0)),
                grounded_in_context=float(eval_data.get("grounded_in_context", 0)),
                helpfulness=float(eval_data.get("helpfulness", 0)),
                error_type=eval_data.get("error_type", "unknown"),
                raw_judge_response=judge_result["raw_response"]
            )
        else:
            logger.warning(f"Judge evaluation failed for trace {trace.trace_id}: {judge_result}")
            return None
            
    except Exception as e:
        logger.error(f"Trace evaluation failed for {trace.trace_id}: {e}")
        return None