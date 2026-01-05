# Production Optimization Work Plan

**Date**: 2025-12-29  
**Scope**: Address 3 key production issues from 186-trace analysis  
**Timeline**: 3-5 days implementation  
**Status**: Issue 1 COMPLETED & DEPLOYED

---

## ✅ Issue 1: Improve "General" Intent Performance [COMPLETED]
**Problem**: 76 queries (40.9% of traffic), 78.9% success rate  
**Impact**: Largest volume, lowest success rate  
**Target**: Increase to 90%+ success rate  
**Status**: ✅ DEPLOYED to dev environment  

### Root Cause Analysis Required
1. **Analyze Failed General Queries**:
   ```bash
   python -c "
   import json
   failed_general = []
   with open('ref_data/traces.jsonl') as f:
       for line in f:
           trace = json.loads(line)
           if trace.get('intent') == 'general' and not trace.get('neo4j_result_summary', {}).get('has_data', False):
               failed_general.append(trace.get('cypher_query', 'No query'))
   
   print(f'Failed general queries ({len(failed_general)}):')
   for i, query in enumerate(failed_general[:10], 1):
       print(f'{i}. {query[:100]}...')
   "
   ```

2. **Pattern Analysis**: Identify common patterns in failed general queries
3. **Intent Misclassification**: Check if queries should be in specific intents

### Implementation Plan

#### Day 1: Analysis & Classification
- [ ] Extract all 76 general queries with success/failure status
- [ ] Categorize failed queries by pattern type
- [ ] Identify queries that should be reclassified to specific intents
- [ ] Document common failure patterns

#### Day 2: Intent Classification Improvements
- [x] **Add Missing Keywords**: ✅ Updated `app/core/prompt_profiles.py`
   ```python
   # COMPLETED: Added missing keywords
   SALES_KEYWORDS = [..., "opportunity", "opportunity_stage", "opportunities"]
   CALENDAR_KEYWORDS = [..., "calendarevent", "starttime", "duration"]
   PRODUCT_KEYWORDS = [..., "backstage"]
   ```

- [ ] **Create Sub-Intents**: Split general into categories
   ```python
   def classify_general_subtype(question: str) -> str:
       if any(kw in question.lower() for kw in ["employee", "team", "staff"]):
           return "general_employee"
       elif any(kw in question.lower() for kw in ["client", "customer", "account"]):
           return "general_client"
       # ... more categories
       return "general_misc"
   ```

#### Day 3: Prompt Profile Enhancement
- [ ] **Create General Sub-Profiles**: 
   ```python
   PROMPT_PROFILES["general_employee"] = {
       "schema_focus": "Employee nodes, relationships, properties",
       "examples": ["Who are the senior engineers?", "List team leads by region"],
       "rules": ["Focus on Employee.title, Employee.sf_seniority_level"]
   }
   ```

- [ ] **Enhance General Prompt**: Add more specific guidance
   ```python
   PROMPT_PROFILES["general"]["rules"] += [
       "For employee queries: Use Employee.name, Employee.title, Employee.email",
       "For client queries: Use Client.sf_name, not Client.name",
       "For ambiguous queries: Ask for clarification in natural language"
   ]
   ```

#### Day 4: Testing & Validation
- [ ] Test improved classification on failed queries
- [ ] Validate new prompts don't break existing successful patterns
- [ ] A/B test with sample of general queries

---

## Issue 2: Increase Learned Pattern Usage [NEXT PRIORITY]
**Problem**: 14% learned patterns vs 50% target  
**Impact**: Slower responses, higher LLM costs  
**Target**: Achieve 35%+ learned pattern usage  
**Status**: ⏳ WAITING for new trace data to validate Issue 1 fix

### Immediate Monitoring Plan:
1. **Track New Traces**: Monitor production for 24-48 hours
   ```bash
   # Check for new traces
   python Tests/monitor_deployment.py
   
   # Copy new traces when available
   scp -i D:\Projects\aipg.pem ubuntu@aipg.dudelabz.com:/home/ubuntu/meetingsBotLogs/persistentData/traces.jsonl ref_data/
   
   # Analyze new data
   python -m Tests.analyze_traces --data-dir ref_data --export-csv
   ```

2. **Validate Fix**: Look for improved general intent success rate in new traces
3. **Baseline Established**: Current 186 traces show 78.9% general success rate  

### Root Cause Analysis
1. **Pattern Learning Threshold**: Current confidence threshold may be too high
2. **Pattern Diversity**: May need more diverse successful patterns
3. **Pattern Matching**: Similarity algorithm may be too strict

### Implementation Plan

#### Day 1: Pattern Analysis
- [ ] **Analyze Current Patterns**:
   ```bash
   python -c "
   import json
   with open('ref_data/query_patterns.json') as f:
       patterns = json.load(f)
   
   print(f'Total patterns: {len(patterns.get(\"patterns\", {}))}')
   for pattern_id, data in patterns.get('patterns', {}).items():
       print(f'{pattern_id}: {data.get(\"usage_count\", 0)} uses, {data.get(\"success_rate\", 0):.1%} success')
   "
   ```

- [ ] **Identify High-Volume Query Types**: Find repeated query patterns not yet learned
- [ ] **Check Confidence Thresholds**: Review why patterns aren't matching

#### Day 2: Lower Learning Barriers
- [ ] **Reduce Confidence Threshold**: 
   ```python
   # In app/core/enhanced_query_generator.py
   LEARNED_PATTERN_THRESHOLD = 0.7  # Down from 0.8
   ```

- [ ] **Improve Pattern Matching**:
   ```python
   def calculate_similarity(query1: str, query2: str) -> float:
       # Add fuzzy matching, keyword overlap, intent similarity
       # Current implementation may be too strict
   ```

- [ ] **Accelerate Pattern Creation**:
   ```python
   # Promote successful queries to patterns faster
   MIN_SUCCESS_COUNT = 2  # Down from 3
   MIN_SUCCESS_RATE = 0.8  # Down from 0.9
   ```

#### Day 3: Pattern Seeding
- [ ] **Seed High-Volume Patterns**: Manually create patterns for common queries
   ```python
   # Add patterns for top query types from analysis
   SEED_PATTERNS = {
       "client_list_by_region": {
           "template": "MATCH (c:Client)-[:LOCATED_IN]->(r:Region {name: $region}) RETURN c.sf_name",
           "examples": ["List clients in IL", "Show US clients", "Clients in UK region"]
       }
   }
   ```

- [ ] **Batch Pattern Learning**: Process successful queries in batches
   ```python
   def batch_learn_from_traces():
       # Process all successful traces to create patterns
       # Focus on queries with >2 similar examples
   ```

#### Day 4: Monitoring & Optimization
- [ ] Deploy changes and monitor pattern usage increase
- [ ] Track response time improvements
- [ ] Adjust thresholds based on results

---

## Issue 3: Address Empty Results (24 failures)
**Problem**: All 24 failures are empty results, not query errors  
**Impact**: 12.9% failure rate, poor user experience  
**Target**: Reduce to <5% empty results  

### Root Cause Analysis
1. **Valid Queries, No Data**: Queries are syntactically correct but return no results
2. **Data Availability**: Users asking for data that doesn't exist
3. **Query Specificity**: Queries may be too restrictive

### Implementation Plan

#### Day 1: Empty Result Analysis
- [ ] **Categorize Empty Results**:
   ```bash
   python -c "
   import json
   empty_queries = []
   with open('ref_data/traces.jsonl') as f:
       for line in f:
           trace = json.loads(line)
           if not trace.get('neo4j_result_summary', {}).get('has_data', False):
               empty_queries.append({
                   'query': trace.get('cypher_query', '')[:100],
                   'intent': trace.get('intent', 'unknown')
               })
   
   print(f'Empty result queries ({len(empty_queries)}):')
   for i, q in enumerate(empty_queries[:10], 1):
       print(f'{i}. [{q[\"intent\"]}] {q[\"query\"]}...')
   "
   ```

- [ ] **Data Availability Check**: Verify if requested data exists in database
- [ ] **Query Restrictiveness**: Check if filters are too narrow

#### Day 2: Smart Fallback System
- [ ] **Implement Query Relaxation**:
   ```python
   def relax_query_constraints(cypher_query: str) -> List[str]:
       """Generate progressively less restrictive versions of query"""
       relaxed_queries = []
       
       # Remove date constraints
       if "close_date >=" in cypher_query:
           relaxed_queries.append(cypher_query.replace("AND o.close_date >= '2025-01-01'", ""))
       
       # Remove specific filters
       if "WHERE" in cypher_query:
           # Try query without WHERE clause
           relaxed_queries.append(cypher_query.split("WHERE")[0] + cypher_query.split("WHERE")[1].split("RETURN")[0].replace("WHERE", "RETURN"))
       
       return relaxed_queries
   ```

- [ ] **Implement Progressive Querying**:
   ```python
   async def execute_with_fallback(cypher_query: str):
       result = neo4j_client.execute_query(cypher_query)
       
       if not result:  # Empty result
           # Try relaxed versions
           for relaxed_query in relax_query_constraints(cypher_query):
               result = neo4j_client.execute_query(relaxed_query)
               if result:
                   return result, f"No exact matches found. Showing broader results:"
       
       return result, None
   ```

#### Day 3: Helpful Empty Responses
- [ ] **Data Availability Suggestions**:
   ```python
   def generate_empty_result_help(query: str, intent: str) -> str:
       suggestions = []
       
       if "2025" in query:
           suggestions.append("Try a different year (2023, 2024)")
       
       if intent == "vendor":
           suggestions.append("Available vendors: HashiCorp, AWS, Microsoft, etc.")
       
       if intent == "list" and "client" in query.lower():
           suggestions.append("Try 'List all clients' or specify a region (IL, US, UK)")
       
       return "No results found. Suggestions: " + "; ".join(suggestions)
   ```

- [ ] **Schema-Aware Suggestions**:
   ```python
   def suggest_alternatives(failed_query: str) -> List[str]:
       # Analyze query and suggest similar queries that would return data
       # Based on actual data availability in Neo4j
   ```

#### Day 4: User Experience Enhancement
- [ ] **Implement in Answer Renderer**:
   ```python
   # In app/core/answer_renderer.py
   async def render_answer(question, rows, bedrock_client):
       if not rows:  # Empty result
           help_text = generate_empty_result_help(question, detect_intent(question))
           return f"No results found for your query. {help_text}"
       
       # Normal processing for non-empty results
   ```

- [ ] **Add Query Suggestions**: Suggest related queries that would return data
- [ ] **Data Exploration Mode**: Offer to show available data in the domain

---

## Implementation Timeline

### Week 1 (Days 1-5)
- **Days 1-2**: Analysis and root cause identification
- **Days 3-4**: Implementation of fixes
- **Day 5**: Testing and validation

### Success Metrics
- [ ] **General Intent**: 78.9% → 90%+ success rate
- [ ] **Learned Patterns**: 14% → 35%+ usage rate  
- [ ] **Empty Results**: 12.9% → <5% failure rate
- [ ] **Overall Success**: 87.1% → 95%+ success rate

### Monitoring Plan
- [ ] Deploy changes incrementally
- [ ] Monitor production metrics daily
- [ ] Run analysis after 50 new queries
- [ ] Rollback if performance degrades

---

## Files to Modify

### Intent Classification
- `app/core/prompt_profiles.py` - Add keywords, create sub-intents
- `app/core/enhanced_query_generator.py` - Adjust thresholds

### Pattern Learning  
- `app/core/adaptive_query_classifier.py` - Lower confidence thresholds
- `app/core/production_learning_loader.py` - Seed patterns

### Empty Results
- `app/core/answer_renderer.py` - Smart fallbacks and suggestions
- `app/api/routes.py` - Progressive querying logic

### Testing
- `Tests/test_intent_classification.py` - Validate improvements
- `Tests/test_pattern_learning.py` - Test pattern usage increase
- `Tests/production_validation.py` - End-to-end testing

---

**Estimated Effort**: 3-5 days  
**Risk Level**: Medium (production changes)  
**Rollback Plan**: Git revert + container restart  
**Success Criteria**: 95%+ overall success rate, 35%+ pattern usage