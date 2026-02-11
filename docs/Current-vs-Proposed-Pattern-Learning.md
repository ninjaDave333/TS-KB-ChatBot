# Current vs. Proposed: Pattern Learning Enhancement

## Current Process (What We're Refining)

### 1. **Current Query Flow**
```
User Question → Intent Classification → Prompt Profile Selection → LLM Generation → Cypher Execution
```

**Example Current Flow:**
```
Question: "Who are the top 3 clients with most deals in 2025?"
↓
Intent: "sales_v1" (keyword matching: "top", "deals")
↓
Prompt Profile: sales_v1 system prompt + few-shot examples
↓
LLM: Generates Cypher from scratch every time
↓
Result: ~3-5 seconds, costs API tokens
```

### 2. **Current Intent Classification (keyword-based)**
```python
def classify_question_intent(question: str) -> str:
    q_lower = question.lower()
    
    # High-priority product keywords
    if any(kw in q_lower for kw in ["hashicorp", "terraform", "vault"]):
        return "product_v1"
    
    # Calendar keywords  
    if any(kw in q_lower for kw in ["meeting", "recording", "calendar"]):
        return "calendar_v1"
    
    # Sales keywords
    if any(kw in q_lower for kw in ["deal", "revenue", "opportunity"]):
        return "sales_v1"
    
    return "strict_v1"  # Default
```

### 3. **Current Prompt Profiles**
```python
PROMPT_PROFILES = {
    "sales_v1": {
        "system": SCHEMA_SUMMARY + RULES_SUMMARY + FEW_SHOT_EXAMPLES,
        "user_template": "Convert this sales question: {question}"
    }
}
```

**Issues with Current Approach:**
- ❌ **Every query goes to LLM** (expensive, slow)
- ❌ **No learning from successful patterns**
- ❌ **Static few-shot examples** (not from production data)
- ❌ **12.3% learned pattern usage** (low efficiency)

---

## Proposed Enhancement: Pattern Learning System

### 1. **Enhanced Query Flow**
```
User Question → Intent Classification → Pattern Matching → [Learned Pattern OR LLM Generation]
```

**Example Enhanced Flow:**
```
Question: "Who are the top 3 clients with most deals in 2025?"
↓
Intent: "sales_v1" 
↓
Pattern Check: Match found! (pattern_sales_top_ranking_3)
↓
Instant Response: Use cached Cypher + parameters
↓
Result: ~0.2 seconds, no API cost
```

### 2. **Pattern Learning from Production Data**

**Source Data:** `production_metrics.json` (141 real queries)
```json
{
  "query": "list top 3 biggest deals of 2025, show client name, deal date and deal profit",
  "intent": "sales_v1", 
  "success": true,
  "cypher": "MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)...",
  "answer": "Here are the 3 largest deals..."
}
```

**Pattern Extraction:**
```python
# Group successful queries by exact Cypher match
cypher_groups = defaultdict(list)
for query in successful_queries:
    cypher_groups[query['cypher']].append(query)

# Create patterns for Cypher used 2+ times
for cypher, group in cypher_groups.items():
    if len(group) >= 2:
        pattern = create_learned_pattern(group)
```

### 3. **Learned Pattern Structure**
```json
{
  "id": "pattern_sales_top_ranking_3",
  "intent": "sales_v1",
  "pattern_type": "top_ranking",
  "cypher_template": "MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product) WHERE o.opportunity_stage = 'Closed Won' AND o.close_date >= '{year}-01-01' AND o.close_date < '{next_year}-01-01' WITH c.sf_name AS client, o.close_date AS date, toFloat(o.total_price) AS profit ORDER BY profit DESC LIMIT 3 RETURN client, date, profit",
  "trigger_keywords": ["top", "biggest", "deals", "client", "profit"],
  "example_questions": [
    "list top 3 biggest deals of 2025",
    "show me the 3 largest deals by profit", 
    "top 3 most profitable deals"
  ],
  "usage_count": 4,
  "confidence": 0.8,
  "sample_answer": "Here are the 3 largest deals by profit..."
}
```

### 4. **Enhanced Query Processing**
```python
def process_query_enhanced(question: str):
    # Step 1: Intent classification (same as before)
    intent = classify_question_intent(question)
    
    # Step 2: NEW - Check for learned patterns
    pattern = find_matching_pattern(question, intent)
    
    if pattern:
        # Use learned pattern (fast path)
        cypher = apply_pattern_template(pattern, question)
        return execute_cypher(cypher), "learned_pattern"
    else:
        # Fall back to LLM generation (slow path)
        return generate_with_llm(question, intent), "ai_generated"
```

### 5. **Pattern Matching Algorithm**
```python
def find_matching_pattern(question, intent):
    patterns = get_patterns_for_intent(intent)
    
    for pattern in patterns:
        # Check keyword overlap
        question_words = set(question.lower().split())
        pattern_keywords = set(pattern['trigger_keywords'])
        
        overlap = len(question_words & pattern_keywords)
        threshold = len(pattern_keywords) * 0.6  # 60% keyword match
        
        if overlap >= threshold:
            return pattern
    
    return None  # No pattern match, use LLM
```

---

## Expected Impact

### **Performance Improvements**
| Metric | Current | With Patterns | Improvement |
|--------|---------|---------------|-------------|
| **Response Time** | 3-5 seconds | 0.2-0.5 seconds | **90% faster** |
| **API Costs** | $0.02 per query | $0.00 per pattern | **100% savings** |
| **Pattern Usage** | 12.3% | 35-50% | **3x increase** |
| **Success Rate** | 85.4% | 90%+ | **Higher accuracy** |

### **Business Value**
- **Cost Savings**: ~$500/month in LLM API costs
- **User Experience**: Sub-second responses for common queries  
- **Reliability**: Proven Cypher from production data
- **Scalability**: System learns and improves automatically

### **Implementation Strategy**

**Phase 1: Pattern Extraction (This Session)**
- ✅ Analyze 141 production queries
- ✅ Extract 5-10 high-value patterns
- ✅ Human approval for each pattern

**Phase 2: Integration (Next)**
- Modify query processing to check patterns first
- Add pattern matching logic
- Deploy and monitor performance

**Phase 3: Continuous Learning (Future)**
- Auto-extract new patterns from successful queries
- A/B test pattern vs. LLM performance
- Expand to more intent types

---

## Human-in-the-Loop Approval Process

**Why Human Approval?**
- Ensure pattern quality and accuracy
- Validate business logic correctness  
- Prevent bad patterns from affecting users
- Build confidence in the system

**What You'll Review:**
1. **Pattern Intent**: Does it match the right category?
2. **Cypher Quality**: Is the generated query correct?
3. **Keyword Relevance**: Do trigger words make sense?
4. **Business Value**: Will this pattern help users?

**Example Review:**
```
PATTERN #1: pattern_sales_top_ranking_3
Intent: sales_v1
Usage: 4 times (high confidence)
Keywords: top, biggest, deals, client, profit

Example Questions:
1. "list top 3 biggest deals of 2025"
2. "show me the 3 largest deals by profit"
3. "top 3 most profitable deals"

Cypher: MATCH (c:Client)-[o:OPPORTUNITY]->...

Approve? (y/n/s): y ✓
```

This approach ensures we only deploy high-quality, human-validated patterns that will genuinely improve the user experience.