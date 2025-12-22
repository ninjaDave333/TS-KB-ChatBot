"""
Intent-based prompt profiles for optimized Cypher generation.
Ported from self-learning RAG system.
"""
from typing import Dict, Tuple

# Schema and rules summaries
SCHEMA_SUMMARY = """
You are an expert Cypher query generator for a Neo4j knowledge graph.

CRITICAL: There is NO :Deal node. Deals are OPPORTUNITY relationships between Client and Product.

Node labels:
- Employee(azure_id, name, email, ms_id, ... )
- Client(sf_id, sf_name, region, ... )
- Product(name, vendor, sf_family, sf_type, sf_business_unit, ... )
  *** IMPORTANT: Product property is 'vendor' NOT 'vendor_name' ***
- Vendor(name)
- Region(name: "IL", "US", "UK")
- Skill(name)
- BU(name)
- Recording(title, name, createdDateTime, meetingOwner, ... )
- CalendarEvent(title, name, owner, startTime, endTime, externalParticipants, internalParticipants, ... )

Important relationships:
- (Client)-[:MANAGED_BY]->(Employee)
- (Employee|Client)-[:LOCATED_IN]->(Region)
- (Employee|Product)-[:BELONGS_TO]->(BU)
- (Vendor)-[:MAKES]->(Product)
- (Client)-[:OPPORTUNITY]->(Product)  ← DEALS ARE HERE (not a :Deal node!)
- (Client)-[:HAS_INSTALLED]->(Product)
- (Product)-[:REQUIRES_SKILL]->(Skill)
- (Employee)-[:HAS_SKILL]->(Skill)
- (Recording)-[:LINKED_TO]->(CalendarEvent)

OPPORTUNITY relationship properties: total_price, close_date, opportunity_name, opportunity_stage ("Closed Won", "Closed Lost", "Pipeline").
"""

RULES_SUMMARY = """
Rules:
- ALWAYS generate Cypher that is READ-ONLY.
- Do NOT use CREATE, MERGE, DELETE, DETACH, or SET.
- For "top active clients in YEAR":
  - Use Closed Won opportunities:
    MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
    WHERE o.opportunity_stage = "Closed Won"
      AND o.close_date >= "YEAR-01-01"
      AND o.close_date < "YEAR+1-01-01"
    WITH c, count(o) AS deal_count
    ORDER BY deal_count DESC
    RETURN c.sf_name AS client_name, deal_count
"""

FEW_SHOT_EXAMPLES = """
EXAMPLES:

1. Top 5 clients by deal count in 2024:
   MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
   WHERE o.opportunity_stage = 'Closed Won'
     AND o.close_date >= '2024-01-01' AND o.close_date < '2025-01-01'
   WITH c.sf_name AS client, count(o) AS deal_count
   ORDER BY deal_count DESC
   LIMIT 5
   RETURN client, deal_count

2. Top 3 products with most successful deals in 2023:
   MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
   WHERE o.opportunity_stage = 'Closed Won'
     AND o.close_date >= '2023-01-01' AND o.close_date < '2024-01-01'
   WITH p.name AS product, count(o) AS deal_count
   ORDER BY deal_count DESC
   LIMIT 3
   RETURN product, deal_count
"""

# Intent-specific prompt profiles
PROMPT_PROFILES: Dict[str, Dict[str, str]] = {
    "strict_v1": {
        "system": (
            SCHEMA_SUMMARY + "\n" + RULES_SUMMARY + "\n" + FEW_SHOT_EXAMPLES +
            "\nYou MUST answer ONLY with a Cypher query, no explanation, no markdown, no backticks."
        ),
        "user_template": "Convert this natural language question into a Cypher query:\n\n{question}\n",
    },
    "sales_v1": {
        "system": (
            SCHEMA_SUMMARY + "\n" + RULES_SUMMARY +
            "\nFOCUS: This is a sales/deal analytics query. Emphasize:" +
            "\n- OPPORTUNITY relationship between Client and Product: (c:Client)-[o:OPPORTUNITY]->(p:Product)" +
            "\n- opportunity_stage = 'Closed Won' for successful deals" +
            "\n- close_date for filtering by year/period" +
            "\n- Aggregations: count(o) for deal count, sum(toFloat(o.total_price)) for revenue" +
            "\n- Product vendor property is 'vendor' (NOT vendor_name): use p.vendor" +
            "\n- For filtering by vendor: WHERE toLower(p.vendor) CONTAINS 'hashicorp' or NOT toLower(p.vendor) CONTAINS 'terasky'" +
            "\n" + FEW_SHOT_EXAMPLES +
            "\nYou MUST answer ONLY with a Cypher query, no explanation, no markdown, no backticks."
        ),
        "user_template": "Convert this natural language sales/deal question into a Cypher query:\n\n{question}\n",
    },
    "calendar_v1": {
        "system": (
            SCHEMA_SUMMARY + "\n" + RULES_SUMMARY +
            "\nFOCUS: This is a calendar/meeting query. Emphasize:" +
            "\n- CalendarEvent node properties: owner, startTime, endTime, title, externalParticipants, internalParticipants" +
            "\n- For employee meeting activity: MATCH (ce:CalendarEvent) then count by ce.owner" +
            "\n- Use toLower() and CONTAINS for case-insensitive matching" +
            "\n- For date ranges: WHERE ce.startTime >= datetime('2025-01-01')" +
            "\n- AVOID complex list comprehensions with WHERE clauses - use simple MATCH patterns" +
            "\n- Example: MATCH (ce:CalendarEvent) WHERE toLower(ce.owner) CONTAINS '@' WITH ce.owner AS employee, count(ce) AS meeting_count" +
            "\n" + FEW_SHOT_EXAMPLES +
            "\nYou MUST answer ONLY with a Cypher query, no explanation, no markdown, no backticks."
        ),
        "user_template": "Convert this natural language calendar/meeting question into a Cypher query:\n\n{question}\n",
    },
    "product_v1": {
        "system": (
            SCHEMA_SUMMARY + "\n" + RULES_SUMMARY +
            "\nFOCUS: This is a product/vendor analytics query. Emphasize:" +
            "\n- Product node with properties: name, vendor (NOT vendor_name), sf_family, sf_type" +
            "\n- Use 'p.vendor' to filter/match vendors, e.g., toLower(p.vendor) CONTAINS 'terasky'" +
            "\n- For non-terasky products: WHERE NOT toLower(p.vendor) CONTAINS 'terasky'" +
            "\n- Do NOT use (Vendor)-[:MAKES]->(Product) unless explicitly asked for vendor details" +
            "\n- For vendor aggregations: GROUP BY p.vendor (via WITH p.vendor AS vendor, ...)" +
            "\n- Use CONTAINS for keyword matching on product/vendor names" +
            "\n" + FEW_SHOT_EXAMPLES +
            "\nYou MUST answer ONLY with a Cypher query, no explanation, no markdown, no backticks."
        ),
        "user_template": "Convert this natural language product question into a Cypher query:\n\n{question}\n",
    },
}


def classify_question_intent(question: str) -> str:
    """
    Classify question intent using keyword matching.
    Returns: 'sales_v1', 'calendar_v1', 'product_v1', or 'strict_v1' (default)
    """
    q_lower = question.lower()
    
    # Calendar / Meeting keywords
    calendar_keywords = [
        "meeting", "recording", "calendar", "event", "call", "invite", "invited",
        "owner of", "participant", "attendee", "transcript", "subject", "agenda"
    ]
    
    # Sales / Deal keywords
    sales_keywords = [
        "deal", "opportunity", "revenue", "sold", "sales", "pipeline", "closed won",
        "closed lost", "client", "customer", "purchase", "deal count", "top selling",
        "best performing", "successful deals", "win rate"
    ]
    
    # Product / Vendor keywords
    product_keywords = [
        "product", "vendor", "solution", "feature", "installed", "family",
        "license", "asset", "version", "deployment", "tool"
    ]
    
    # Count keyword matches
    calendar_score = sum(1 for kw in calendar_keywords if kw in q_lower)
    sales_score = sum(1 for kw in sales_keywords if kw in q_lower)
    product_score = sum(1 for kw in product_keywords if kw in q_lower)
    
    # Return the highest scoring intent
    if calendar_score > 0 and calendar_score >= sales_score and calendar_score >= product_score:
        return "calendar_v1"
    elif sales_score > 0 and sales_score >= product_score:
        return "sales_v1"
    elif product_score > 0:
        return "product_v1"
    else:
        return "strict_v1"


def get_prompt_for_intent(intent: str, question: str) -> Tuple[str, str]:
    """
    Get system and user prompts for specific intent.
    Returns: (system_prompt, user_prompt)
    """
    profile = PROMPT_PROFILES.get(intent, PROMPT_PROFILES["strict_v1"])
    system_prompt = profile["system"]
    user_prompt = profile["user_template"].format(question=question)
    return system_prompt, user_prompt
