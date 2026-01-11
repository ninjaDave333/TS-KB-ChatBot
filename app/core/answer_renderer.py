"""
Answer Renderer for TSKB RAG System
Generates human-friendly explanations from query results using LLM
Ported from self-learning RAG system
"""
import json
from typing import Any, Dict, List


def serialize_for_json(obj: Any) -> Any:
    """
    Recursively convert non-JSON-serializable objects to strings.
    Handles dicts, lists, and primitive types gracefully.
    """
    if isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_for_json(item) for item in obj]
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    else:
        # Convert any other type (DateTime, Decimal, etc.) to string
        return str(obj)


async def render_answer(
    question: str,
    rows: List[Dict[str, Any]],
    bedrock_client,
) -> str:
    """
    Turn query results into a human-friendly explanation using the LLM.
    
    - Keeps all Cypher generation / DB logic separate (we only rewrite the *result*).
    - Does NOT invent numbers: the model is instructed to stay grounded in rows.
    - Handles non-JSON-serializable types by converting to strings.
    - Provides helpful suggestions for empty results.
    """
    
    if not rows:
        # Generate helpful suggestions for empty results
        helpful_message = generate_empty_result_help(question)
        return f"There are no matching results for that question. {helpful_message}"
    
    # Limit rows to keep prompts reasonable
    max_rows_for_prompt = 50
    truncated_rows = rows[:max_rows_for_prompt]
    
    # Serialize all rows to handle DateTime and other non-JSON types
    serialized_rows = serialize_for_json(truncated_rows)
    rows_json = json.dumps(serialized_rows, ensure_ascii=False, indent=2)
    
    system_prompt = (
        "You are a helpful business analytics assistant.\n"
        "\n"
        "GOAL\n"
        "- Given a user's question and result rows from a Neo4j analytics query,\n"
        "  write a clear, concise, human-friendly explanation.\n"
        "- Do NOT invent new numeric values or entities. Only describe what is present\n"
        "  in the rows and what logically follows from them.\n"
        "- CRITICAL: When rows contain lists or arrays (like latest_meetings), you MUST\n"
        "  display the actual values from those lists, not generic descriptions.\n"
        "\n"
        "STYLE\n"
        "- Answer in natural language, not JSON or tables.\n"
        "- Prefer short paragraphs or bullet points.\n"
        "- If there are top-N results, mention them in plain language.\n"
        "- If there are amounts or counts, reference them, but do not fabricate any.\n"
        "- If there are many rows, summarize the main patterns instead of listing all.\n"
        "- Use markdown formatting for better readability (bold, lists, etc.).\n"
        "- When displaying meeting titles or list items, show the ACTUAL values from the data.\n"
    )
    
    user_prompt = (
        f"User question:\n{question}\n\n"
        f"Result rows (JSON, up to {max_rows_for_prompt} rows shown):\n{rows_json}\n\n"
        "Write a short human-friendly explanation of the answer. "
        "If there are multiple rows, summarize the key insights."
    )
    
    # Use LLM to generate natural language explanation
    text = await bedrock_client.generate_text(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.2,  # focused, not too creative
    )
    
    text = (text or "").strip()
    if not text:
        return "I ran the query but could not generate a natural-language explanation."
    
    return text


def generate_empty_result_help(question: str) -> str:
    """Generate helpful suggestions for empty results"""
    q_lower = question.lower()
    suggestions = []
    
    if "2025" in question or "2026" in question:
        suggestions.append("Try a different year (2023 or 2024)")
    
    if "prompt security" in q_lower:
        suggestions.append("Try 'security', 'HashiCorp Vault', or 'Aqua Security' instead")
    
    if "backstage" in q_lower:
        suggestions.append("Try 'HashiCorp', 'AWS', or 'Microsoft' instead")
    
    if "calendarevent" in q_lower:
        suggestions.append("Try asking about 'meetings' or 'recordings' instead")
    
    if "client" in q_lower and "region" in q_lower:
        suggestions.append("Try 'IL', 'US', or 'UK' for regions")
    
    if "opportunity_stage" in q_lower:
        suggestions.append("Try 'Closed Won', 'Pipeline', or 'Proposal' for stages")
    
    # Generic product search suggestions
    if any(word in q_lower for word in ["product", "solution", "deals"]) and len(suggestions) == 0:
        suggestions.append("Try broader terms like 'security', 'cloud', or 'infrastructure'")
    
    if suggestions:
        return "Suggestions: " + "; ".join(suggestions) + "."
    
    return "Try broadening your search criteria or using different keywords."
