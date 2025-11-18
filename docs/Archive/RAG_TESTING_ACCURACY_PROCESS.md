# RAG Testing & Accuracy Improvement Process

**Project**: Automated RAG Query Accuracy Enhancement  
**Version**: 1.0.0  
**Date**: 2025-11-12  
**Purpose**: Systematic process to identify, debug, and fix AI query generation issues

---

## Overview

This document outlines the systematic process we developed to identify and fix AI query generation issues in the TSKB-RAG system. This process can be automated and repeated for continuous improvement.

---

## Phase 1: Issue Detection & Analysis

### Step 1.1: Query Failure Detection
**Trigger**: API returns syntax errors or empty results
**Tools**: Error monitoring, query logs

**Process**:
1. Capture failed query and error message
2. Log user intent vs generated Cypher
3. Categorize error type (syntax, semantic, data)

**Example**:
```
Error: "Invalid input '': expected an expression"
Query: "list clients in israel"
Generated: "MATCH (c:Client)-[:LOCATED_IN]->(r:Region) WHERE r.name = 'IL' AND c.active = true"
Issue: Assumed LOCATED_IN relationship doesn't exist
```

### Step 1.2: Data Structure Investigation
**Purpose**: Understand actual vs assumed data structure

**Debug Script Template**:
```python
def debug_data_structure(entity_type, search_term):
    # 1. Check if entity exists
    # 2. Examine actual properties
    # 3. Verify relationship patterns
    # 4. Document findings
```

**Key Investigations**:
- Property names (sf_name vs name)
- Relationship existence (LOCATED_IN vs direct properties)
- Data types (boolean vs string status fields)
- Available values (region codes, status values)

---

## Phase 2: Root Cause Analysis

### Step 2.1: Schema Description Audit
**Purpose**: Compare schema descriptions vs actual data

**Checklist**:
- [ ] Node property names match actual data
- [ ] Relationship patterns exist in database
- [ ] Common values are accurate
- [ ] Query examples work correctly

### Step 2.2: AI Generation Issues
**Common Issues**:
1. **Token Truncation**: max_tokens too low causing incomplete queries
2. **APOC Usage**: AI using unavailable functions
3. **Syntax Errors**: Trailing commas, incomplete statements
4. **Wrong Assumptions**: Non-existent relationships/properties

---

## Phase 3: Systematic Fixes

### Step 3.1: Schema Description Updates
**Process**:
1. Document actual data structure
2. Update schema descriptions with correct patterns
3. Add explicit "DO NOT" rules for common mistakes
4. Include working query examples

**Template**:
```python
"critical_notes": {
    "field_names": "ALWAYS use Client.sf_name, NEVER Client.name",
    "relationships": "Clients use direct region property, NO LOCATED_IN",
    "syntax": "NEVER end RETURN with trailing commas"
}
```

### Step 3.2: AI Client Configuration
**Common Fixes**:
- Increase max_tokens (200 → 500+)
- Add syntax validation rules
- Include complete query examples
- Add error recovery prompts

### Step 3.3: Query Validation Layer
**Implementation**:
```python
def validate_cypher(query):
    # 1. Syntax check
    # 2. Entity existence check  
    # 3. Relationship validation
    # 4. Auto-repair common issues
```

---

## Phase 4: Testing & Validation

### Step 4.1: Create Test Cases
**For each fix, create**:
1. Direct query test (known working Cypher)
2. AI generation test (natural language → Cypher)
3. Edge case tests (variations of the query)

**Test Script Template**:
```python
def test_query_fix(natural_query, expected_pattern):
    # 1. Generate Cypher via AI
    # 2. Execute query
    # 3. Validate results
    # 4. Check for expected patterns
```

### Step 4.2: Regression Testing
**Golden Dataset**: Maintain set of known good query-result pairs
```python
GOLDEN_TESTS = [
    {
        "query": "clients in israel",
        "expected_cypher_contains": "c.region = 'IL'",
        "min_results": 50,
        "must_contain": ["Tufin", "Edgybees"]
    }
]
```

---

## Phase 5: Documentation & Deployment

### Step 5.1: Update Documentation
**Required Updates**:
- [ ] CHANGELOG.md with fix details
- [ ] ADR.md with decision rationale
- [ ] SchemaSync.md with corrected patterns
- [ ] Test results and validation

### Step 5.2: Deploy & Monitor
**Process**:
1. Deploy schema description updates
2. Monitor query success rates
3. Track new error patterns
4. Schedule regular accuracy audits

---

## Automation Framework

### Automated Testing Pipeline
```yaml
schedule: "0 */6 * * *"  # Every 6 hours
steps:
  1. Run golden test suite
  2. Analyze failure patterns
  3. Generate debug reports
  4. Alert on accuracy drops
  5. Auto-create improvement tickets
```

### Self-Healing Components
1. **Query Repair**: Auto-fix common syntax issues
2. **Fallback Chain**: AI → Rules → Templates → Error
3. **Schema Sync**: Auto-refresh on relationship failures
4. **Token Adjustment**: Auto-increase on truncation detection

---

## Success Metrics

### Accuracy Targets
- **Query Success Rate**: >95%
- **Syntax Error Rate**: <2%
- **Empty Result Rate**: <5%
- **Response Time**: <3 seconds

### Quality Indicators
- Reduced manual debugging sessions
- Fewer user-reported issues
- Improved natural language understanding
- Higher user satisfaction scores

---

## Process Checklist

### For Each New Issue:
- [ ] Capture error details and user query
- [ ] Create debug script to investigate data structure
- [ ] Identify root cause (schema, AI config, or data)
- [ ] Implement targeted fix
- [ ] Create test cases for the fix
- [ ] Update documentation
- [ ] Deploy and monitor results
- [ ] Add to golden test suite

### Monthly Review:
- [ ] Analyze error patterns and trends
- [ ] Review schema description accuracy
- [ ] Update AI prompts based on failures
- [ ] Optimize token limits and model settings
- [ ] Expand golden test coverage

---

## Tools & Scripts

### Debug Scripts Location
- `Tests/debug_*.py` - Investigation scripts
- `Tests/test_*_fixed.py` - Validation scripts

### Key Files to Monitor
- `app/core/schema_descriptions.py` - Schema accuracy
- `app/core/bedrock_client.py` - AI configuration
- `docs/CHANGELOG.md` - Change tracking
- `docs/ADR.md` - Decision documentation

---

**Maintained By**: TeraSky AI Team  
**Last Updated**: 2025-11-12  
**Next Review**: 2025-12-12