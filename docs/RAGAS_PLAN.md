# RAGAS Integration & RAG Improvement Plan

**Project**: TSKB-RAG Chatbot System  
**Date**: 2025-11-17  
**Status**: Active  
**Priority**: High  

---

## Current RAGAS Results (Baseline)

**Evaluation Date**: 2025-11-17  
**Overall Performance**: 🔴 Critical Issues Identified

| Metric | Score | Status | Target |
|--------|-------|--------|--------|
| Faithfulness | 0.667 | 🔴 Needs Work | >0.8 |
| Answer Relevancy | 0.059 | 🔴 Critical | >0.8 |
| Context Precision | 0.333 | 🔴 Needs Work | >0.7 |
| Context Recall | 0.000 | 🔴 Critical | >0.7 |
| Answer Correctness | 0.030 | 🔴 Critical | >0.8 |

---

## Phase 1: Critical Issues Resolution (Week 1-2)

### 1.1 Fix Answer Relevancy (Score: 0.059 → Target: >0.8)

**Root Cause**: Generated answers don't match user questions

**Actions**:
- [ ] Analyze query-answer mismatches in RAGAS results
- [ ] Review LLM prompt engineering in `bedrock_client.py`
- [ ] Implement answer validation against user intent
- [ ] Add query classification to route questions properly

**Files to Modify**:
- `app/core/bedrock_client.py`
- `app/core/query_generator.py`

### 1.2 Fix Context Recall (Score: 0.000 → Target: >0.7)

**Root Cause**: Retrieved contexts missing essential information

**Actions**:
- [ ] Audit Cypher query generation accuracy
- [ ] Verify schema descriptions match actual data
- [ ] Implement context completeness validation
- [ ] Add fallback retrieval strategies

**Files to Modify**:
- `app/core/schema_descriptions.py`
- `app/core/query_validator.py`

### 1.3 Fix Answer Correctness (Score: 0.030 → Target: >0.8)

**Root Cause**: Factual inaccuracies in generated responses

**Actions**:
- [ ] Implement fact-checking against retrieved data
- [ ] Add confidence scoring for answers
- [ ] Create answer validation pipeline
- [ ] Implement citation mechanisms

**Files to Modify**:
- `app/api/routes.py`
- `app/core/bedrock_client.py`

---

## Phase 2: System Enhancement (Week 3-4)

### 2.1 Improve Context Precision (Score: 0.333 → Target: >0.7)

**Actions**:
- [ ] Implement semantic filtering of retrieved contexts
- [ ] Add relevance scoring for Cypher results
- [ ] Optimize query generation prompts
- [ ] Implement context ranking algorithms

### 2.2 Enhance Faithfulness (Score: 0.667 → Target: >0.8)

**Actions**:
- [ ] Strengthen context-answer alignment
- [ ] Implement grounding verification
- [ ] Add hallucination detection
- [ ] Create context-aware response generation

---

## Phase 3: Continuous Monitoring (Ongoing)

### 3.1 Automated RAGAS Evaluation

**Setup**:
- [ ] Daily RAGAS evaluation pipeline
- [ ] Performance trend monitoring
- [ ] Automated alerts for score drops
- [ ] Integration with CI/CD pipeline

**Implementation**:
```bash
# Daily evaluation cron job
0 2 * * * cd /path/to/project && python Tests/ragas_evaluation_bedrock.py
```

### 3.2 Evaluation Infrastructure

**Local DGX Setup** (Cost-free evaluation):
- [ ] Fix DGX connectivity issues
- [ ] Setup Ollama model management
- [ ] Implement automated model updates
- [ ] Create evaluation scheduling

**AWS Bedrock Fallback**:
- [ ] Cost monitoring for Bedrock usage
- [ ] Optimize evaluation frequency
- [ ] Implement smart sampling strategies

---

## Implementation Strategy

### Week 1: Critical Fixes
- **Day 1-2**: Answer Relevancy fixes
- **Day 3-4**: Context Recall improvements  
- **Day 5-7**: Answer Correctness validation

### Week 2: Validation & Testing
- **Day 1-3**: Implement fixes and test
- **Day 4-5**: Run comprehensive RAGAS evaluation
- **Day 6-7**: Performance validation and tuning

### Week 3-4: Enhancement & Monitoring
- **Week 3**: Context Precision and Faithfulness improvements
- **Week 4**: Automated monitoring setup

---

## Success Metrics

### Target Scores (End of Phase 2)
- **Faithfulness**: >0.8 (Current: 0.667)
- **Answer Relevancy**: >0.8 (Current: 0.059)
- **Context Precision**: >0.7 (Current: 0.333)
- **Context Recall**: >0.7 (Current: 0.000)
- **Answer Correctness**: >0.8 (Current: 0.030)

### Performance Indicators
- Query success rate: >95%
- Average response time: <3 seconds
- User satisfaction: >4.0/5.0
- Factual accuracy: >90%

---

## Tools & Resources

### RAGAS Evaluation Scripts
- `Tests/ragas_evaluation_bedrock.py` - AWS Bedrock evaluation
- `Tests/ragas_evaluation_ollama.py` - Local DGX evaluation
- `Tests/dgx_model_manager.py` - DGX model management

### Monitoring & Analysis
- `Tests/ragas_*_results_*.json` - Detailed evaluation results
- `Tests/ragas_*_analysis_*.json` - Performance analysis
- Daily evaluation reports and trend analysis

### Development Environment
- Local DGX: `172.16.10.250` (Ollama + GPU acceleration)
- AWS Bedrock: Fallback for evaluation when DGX unavailable
- Automated testing pipeline integration

---

## Risk Mitigation

### Technical Risks
- **DGX Connectivity**: AWS Bedrock fallback implemented
- **API Costs**: Local DGX prioritized for frequent evaluation
- **Performance Regression**: Automated monitoring with alerts

### Process Risks
- **Scope Creep**: Phased approach with clear milestones
- **Resource Allocation**: Dedicated evaluation infrastructure
- **Quality Assurance**: Continuous RAGAS monitoring

---

## Documentation Updates

### Required Updates
- [ ] Update `docs/ADR.md` with RAGAS integration decisions
- [ ] Update `docs/CHANGELOG.md` with improvement milestones
- [ ] Update `docs/SchemaSync.md` with context improvements
- [ ] Create `docs/RAGAS_RESULTS.md` for ongoing tracking

### Maintenance
- Weekly RAGAS result reviews
- Monthly performance trend analysis
- Quarterly evaluation methodology updates

---

## Next Actions

### Immediate (This Week)
1. **Analyze detailed RAGAS results** from `Tests/ragas_bedrock_results_20251117_110318.json`
2. **Identify specific failure patterns** in answer generation
3. **Prioritize fixes** based on impact and effort
4. **Setup DGX connectivity** for cost-free evaluation

### Short Term (Next 2 Weeks)
1. **Implement critical fixes** for Answer Relevancy and Context Recall
2. **Run daily RAGAS evaluations** to track improvement
3. **Document lessons learned** and update processes
4. **Establish baseline performance** for future comparisons

---

**Plan Owner**: TeraSky AI Team  
**Last Updated**: 2025-11-17  
**Next Review**: 2025-11-24  
**Status**: In Progress - Phase 1 Critical Issues Resolution