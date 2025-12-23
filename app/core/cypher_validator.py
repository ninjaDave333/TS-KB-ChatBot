"""
Enhanced Cypher query validator with self-correction retry logic.
Ported from self-learning RAG system.
"""
import re
from typing import Tuple, List

# Forbidden schema patterns (invented nodes/relationships)
FORBIDDEN_SCHEMA_PATTERNS = [
    r":Deal\b",             # invented Deal node
    r":CLOSED_DEAL\b",      # invented rel
    r"\bd\.year\b",         # bogus Deal.year
    r"\bd\.amount\b",
    r"\bd\.profit\b",
    r"\bd\.client\b",
]


def clean_cypher(text: str) -> str:
    """
    Normalize LLM output into bare Cypher.
    Removes markdown fences, labels, explanations, and validates syntax.
    """
    if not text:
        return ""

    text = text.strip()
    
    # Remove outer quotes
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]
    if text.startswith("'") and text.endswith("'"):
        text = text[1:-1]
    
    # Remove single backticks
    if text.startswith('`') and text.endswith('`') and not text.startswith('```'):
        text = text[1:-1]

    # Remove markdown fences
    fence_pattern = re.compile(r"^```(?:cypher|sql)?\s*([\s\S]*?)```$", re.IGNORECASE | re.MULTILINE)
    m = fence_pattern.search(text)
    if m:
        text = m.group(1).strip()
    
    # Look for fences anywhere in text
    fence_pattern2 = re.compile(r"```(?:cypher|sql)?\s*([\s\S]*?)```", re.IGNORECASE | re.MULTILINE)
    m2 = fence_pattern2.search(text)
    if m2:
        text = m2.group(1).strip()

    # Check for SQL keywords and reject
    if re.search(r"\b(SELECT|FROM|GROUP\s+BY|HAVING|JOIN)\b", text, re.IGNORECASE):
        raise ValueError("LLM returned SQL instead of Cypher")

    # Remove leading prefixes
    prefix_pattern = re.compile(r"^(cypher|query|sql)\s*:\s*", re.IGNORECASE)
    text = prefix_pattern.sub("", text).strip()

    # Extract Cypher lines
    lines = text.splitlines()
    cypher_start_re = re.compile(
        r"^\s*(MATCH|OPTIONAL\s+MATCH|RETURN|WITH|UNWIND|CALL)\b", re.IGNORECASE
    )
    
    cypher_lines = []
    found_start = False
    
    for line in lines:
        line = line.strip()
        
        # Remove trailing semicolons
        if line.endswith(';'):
            line = line[:-1].strip()
        
        if not line:
            if found_start:
                cypher_lines.append("")
            continue
            
        if cypher_start_re.match(line):
            found_start = True
            cypher_lines.append(line)
        elif found_start:
            # Stop if we hit explanatory text
            if line.lower().startswith(("please", "this query", "the query", "explanation", "note:", "here", "certainly", "assuming")):
                break
            # Stop if line looks like prose
            if re.search(r"\b(assuming|example|might|would|could|should|property|stored|differently|adjust|accordingly)\b", line, re.IGNORECASE):
                break
            cypher_lines.append(line)
        elif "MATCH" in line.upper() or "RETURN" in line.upper():
            found_start = True
            cypher_lines.append(line)
    
    if cypher_lines:
        result = "\n".join(cypher_lines).strip()
        if result.endswith(';'):
            result = result[:-1].strip()
        return result
    
    return text.strip()


def validate_cypher_syntax(cypher: str) -> Tuple[bool, str]:
    """
    Validate Cypher syntax for common issues.
    Returns: (is_valid: bool, error_message: str)
    """
    if not cypher or not cypher.strip():
        return False, "Empty Cypher query"
    
    upper_cyp = cypher.upper()
    
    # Check for APOC functions
    if "APOC." in upper_cyp:
        return False, "APOC functions not available - use native Cypher only"
    
    # Check for SQL-ONLY keywords
    sql_only_keywords = ["SELECT", "FROM", "GROUP BY", "HAVING", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN"]
    for kw in sql_only_keywords:
        if re.search(rf"\b{kw}\b", upper_cyp):
            return False, f"SQL keyword detected: {kw}"
    
    # Check for multiple queries
    if cypher.count(';') > 1:
        return False, "Multiple queries detected (semicolon-separated)"
    
    # Check for balanced brackets
    if cypher.count('(') != cypher.count(')'):
        return False, "Unbalanced parentheses"
    if cypher.count('[') != cypher.count(']'):
        return False, "Unbalanced brackets"
    if cypher.count('{') != cypher.count('}'):
        return False, "Unbalanced braces"
    
    # Check for required keywords
    required_keywords = ["MATCH", "RETURN", "OPTIONAL MATCH", "CALL", "UNWIND"]
    has_required = any(kw in upper_cyp for kw in required_keywords)
    if not has_required:
        return False, "Missing required keyword (MATCH, RETURN, etc.)"
    
    return True, ""


def reject_if_forbidden_schema(cypher: str) -> None:
    """
    Check for forbidden schema patterns and raise ValueError if found.
    """
    for pat in FORBIDDEN_SCHEMA_PATTERNS:
        if re.search(pat, cypher):
            raise ValueError(f"Generated Cypher contains invalid schema pattern: {pat}")

    if not cypher:
        raise ValueError("Model returned empty Cypher.")
        
    first_word = cypher.strip().split()[0].upper()
    allowed_starts = {"MATCH", "OPTIONAL", "RETURN", "WITH", "UNWIND", "CALL"}
    if first_word not in allowed_starts:
        raise ValueError(
            f"Generated Cypher must start with MATCH/OPTIONAL/RETURN/WITH/UNWIND/CALL, got: {first_word}"
        )

    # Disallow write keywords
    forbidden = [" CREATE ", " MERGE ", " DELETE ", " DETACH ", " SET "]
    upper_cyp = f" {cypher.upper()} "
    for bad in forbidden:
        if bad in upper_cyp:
            raise ValueError(f"Generated Cypher contains forbidden write clause: {bad.strip()}")
    
    # Check for CalendarEvent queries using .name instead of .title
    if "CalendarEvent" in cypher or "ce." in cypher:
        if re.search(r"\bce\.name\b", cypher) or re.search(r"\bm\.name\b", cypher):
            raise ValueError("Use ce.title for meeting names, NOT ce.name (which contains UUID)")
        # Check for unaliased ce.owner in WITH clause
        if re.search(r"WITH ce\.owner,", cypher):
            raise ValueError("Expression ce.owner in WITH must be aliased: use 'WITH ce.owner AS owner'")
        # Check for invalid collect with ORDER BY inside
        if re.search(r"collect\([^)]+ORDER BY", cypher, re.IGNORECASE):
            raise ValueError("Cannot use ORDER BY inside collect(). Use ORDER BY before WITH, then collect()")


def suggest_correction(cypher: str, error_reason: str) -> str:
    """
    Suggest a correction strategy for common Cypher errors.
    """
    suggestions = {
        "SQL keyword detected": "Use Cypher MATCH/WHERE/WITH/RETURN instead of SQL SELECT/FROM/GROUP BY.",
        "Multiple queries detected": "Return ONE query only. Do not use semicolons to chain queries.",
        "Unbalanced parentheses": "Check that all MATCH patterns have matching ( and ) brackets.",
        "Unbalanced brackets": "Check that all relationships [ ] and property access { } have matching brackets.",
        "Missing required keyword": "Every Cypher query must start with MATCH, OPTIONAL MATCH, RETURN, WITH, UNWIND, or CALL.",
    }
    
    for key, suggestion in suggestions.items():
        if key in error_reason:
            return suggestion
    
    return "Generated Cypher appears invalid. Ensure it follows Neo4j Cypher syntax."


def validate_and_clean(raw_cypher: str) -> Tuple[str, List[str]]:
    """
    Clean and validate Cypher query.
    Returns: (cleaned_cypher, validation_errors)
    """
    errors = []
    
    try:
        cypher = clean_cypher(raw_cypher)
    except ValueError as e:
        errors.append(str(e))
        return "", errors
    
    # Validate syntax
    is_valid, error_msg = validate_cypher_syntax(cypher)
    if not is_valid:
        errors.append(error_msg)
        return cypher, errors
    
    # Check forbidden patterns
    try:
        reject_if_forbidden_schema(cypher)
    except ValueError as e:
        errors.append(str(e))
        return cypher, errors
    
    return cypher, errors
