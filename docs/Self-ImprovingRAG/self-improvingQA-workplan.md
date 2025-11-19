# Self-Improving RAG Quality & Accuracy Work Plan

**Date**: 2025-11-19  
**Status**: ACTIVE DEVELOPMENT  
**Goal**: Systematic improvement of RAG quality and accuracy using comprehensive evaluation infrastructure

## 🎯 Project Overview

The TSKB-RAG system has completed all 6 foundational Self-Improving RAG phases, establishing a robust infrastructure for data-driven quality improvements. This work plan focuses on leveraging this foundation to systematically enhance query understanding, retrieval accuracy, and response quality.

## 📊 Current State Analysis

### ✅ Completed Infrastructure (Phases 1-6)

**Phase 1-3: Foundation**
- ✅ Config-driven routing with YAML configuration (`config/rag_config.yaml`)
- ✅ LLM abstraction with multi-model support (`app/core/llm_client.py`)
- ✅ Judge model integration for quality assessment (`app/core/judge_client.py`)

**Phase 4-5: Evaluation & Monitoring**
- ✅ Structured tracing pipeline → `/app/data/traces.jsonl`
- ✅ Judge model evaluation → `/app/data/eval_results.jsonl`
- ✅ Automated evaluation daemon (`app/monitoring/eval_runner.py`)
- ✅ CLI tools for batch evaluation and metrics (`Tests/evaluate_traces.py`)

**Phase 6: Auto-Tuning**
- ✅ Config auto-tuning based on evaluation results (`app/monitoring/tuning_runner.py`)
- ✅ Intent-specific retrieval limit optimization
- ✅ Safety guardrails and automatic backups

### Recent Quality Improvements (v2.0.2)
- ✅ Enhanced multi-part query handling
- ✅ User-friendly field name mapping (raw DB fields → natural language)
- ✅ Contextual response formatting
- ✅ Natural language responses vs raw data

### Quality Metrics Infrastructure
```json
{
  "overall_score": "0-10 scale, target: >8.5",
  "factual_correctness": "0-10 scale, target: >9.0", 
  "grounded_in_context": "0-10 scale, target: >8.0",
  "helpfulness": "0-10 scale, target: >8.5",
  "error_types": {
    "retrieval": "Target: <10%",
    "reasoning": "Target: <5%", 
    "missing_knowledge": "Target: <15%",
    "none": "Target: >70%"
  }
}
```

## 🚀 Phase 7: Advanced Query Quality Enhancement

**Goal**: Leverage complete evaluation infrastructure to systematically improve query understanding and response accuracy

### 7.0 Golden Dataset & Regression Suite ⭐ CRITICAL FOUNDATION
**Priority**: HIGHEST | **Timeline**: Week 1 (Days 1-3)

**Objective**: Create human-verified golden QA set for regression detection and version comparison
- Small, high-quality, human-verified dataset for core use cases
- Detect regressions from auto-tuning and configuration changes
- Validate that improvements don't break existing functionality
- Baseline for comparing versions and configurations

**Implementation**:
```python
# Files to create:
- tests/golden_qa/qa_set.yaml (curated QA pairs)
- Tests/test_golden_regression.py (regression harness)
- app/core/golden_validator.py (validation logic)
```

**Golden QA Structure**:
```yaml
# tests/golden_qa/qa_set.yaml
golden_queries:
  - id: "client_count_basic"
    query: "How many clients do we have?"
    intent: "count_query"
    expected_entities: ["Client"]
    min_judge_score: 8.5
    critical_facts: ["total client count", "current data"]
    
  - id: "failed_opportunities_2025"
    query: "How many failed opportunities were there in 2025?"
    intent: "count_query"
    expected_entities: ["failed_opportunities", "2025"]
    min_judge_score: 9.0
    critical_facts: ["865 failed opportunities", "2025 timeframe"]
```

**Success Metrics**:
- Golden set covers all major intents (100% coverage)
- All golden queries pass regression tests
- Judge scores above defined thresholds
- Intent classification 100% accurate on golden set
- Run on every config change and nightly CI

### 7.1 Query Intent Classification Refinement
**Priority**: HIGH | **Timeline**: Week 1-2

**Objective**: Improve intent detection accuracy using evaluation feedback
- Analyze `traces.jsonl` for misclassified intents
- Implement confidence scoring for intent detection
- Add fallback intent handling for ambiguous queries
- Use judge model feedback to refine intent classification rules

**Implementation**:
```python
# Files to create/modify:
- app/core/intent_analyzer.py (enhanced intent detection)
- app/core/query_classifier.py (confidence scoring)
- Tests/test_intent_refinement.py (validation)
```

**Success Metrics**:
- Intent classification accuracy >95%
- Reduced "reasoning" error type <3%
- Improved overall_score for ambiguous queries

### 7.2 Multi-Part Query Intelligence
**Priority**: HIGH | **Timeline**: Week 2-3

**Objective**: Build on v2.0.2 improvements with evaluation-driven enhancements
- Detect complex queries: "How many X and what are the top Y"
- Implement query decomposition strategies
- Evaluate partial answer completeness via judge model
- Dynamic response assembly for multi-part queries

**Implementation**:
```python
# Files to create/modify:
- app/core/query_decomposer.py (multi-part query handling)
- app/core/response_assembler.py (comprehensive answers)
- Tests/test_multipart_queries.py (validation)
```

**Success Metrics**:
- Multi-part query completion rate >90%
- Helpfulness score >8.5 for complex queries
- Reduced incomplete response complaints

### 7.3 Context-Aware Response Generation
**Priority**: MEDIUM | **Timeline**: Week 3-4

**Objective**: Use evaluation data to improve response contextuality
- Analyze "grounded_in_context" scores by query type
- Implement dynamic context window adjustment
- Add response completeness validation
- Context relevance scoring before response generation

**Implementation**:
```python
# Files to create/modify:
- app/core/context_manager.py (dynamic context handling)
- app/core/response_validator.py (completeness checks)
- Tests/test_context_awareness.py (validation)
```

**Success Metrics**:
- Grounded_in_context score >8.5
- Context relevance accuracy >95%
- Reduced "missing_knowledge" errors <10%

## 🎯 Phase 8: Retrieval Optimization & Accuracy

**Goal**: Optimize retrieval strategies using auto-tuning insights and evaluation feedback

### 8.1 Dynamic Retrieval Strategy Selection
**Priority**: HIGH | **Timeline**: Week 4-5

**Objective**: Implement intelligent retrieval strategy selection
- Query complexity scoring algorithm
- Dynamic limit adjustment based on query type and evaluation history
- Multi-strategy retrieval with confidence weighting
- Performance-based strategy routing

**Implementation**:
```python
# Files to create/modify:
- app/core/retrieval_optimizer.py (strategy selection)
- app/core/query_complexity.py (complexity scoring)
- Tests/test_retrieval_optimization.py (validation)
```

**Success Metrics**:
- Retrieval error rate <8%
- Optimal retrieval limits per intent (auto-tuned)
- Improved factual_correctness >9.2

### 8.2 Cypher Query Quality Enhancement
**Priority**: MEDIUM | **Timeline**: Week 5-6

**Objective**: Use judge model feedback to improve Cypher generation
- Analyze "factual_correctness" patterns by Cypher type
- Implement Cypher validation and correction
- Add query optimization suggestions
- Cypher complexity vs accuracy analysis

**Implementation**:
```python
# Files to create/modify:
- app/core/cypher_optimizer.py (query optimization)
- app/core/cypher_validator.py (validation logic)
- Tests/test_cypher_quality.py (validation)
```

**Success Metrics**:
- Cypher execution success rate >98%
- Factual_correctness score >9.3
- Reduced database query errors

### 8.3 Result Relevance Scoring
**Priority**: MEDIUM | **Timeline**: Week 6-7

**Objective**: Implement relevance filtering based on evaluation data
- Score result relevance before response generation
- Filter low-relevance results dynamically
- Implement result ranking algorithms
- Relevance threshold optimization per intent

**Implementation**:
```python
# Files to create/modify:
- app/core/relevance_scorer.py (result scoring)
- app/core/result_filter.py (dynamic filtering)
- Tests/test_relevance_scoring.py (validation)
```

**Success Metrics**:
- Result relevance accuracy >92%
- Improved helpfulness score >8.7
- Reduced irrelevant information in responses

## 📈 Phase 9: Real-Time Quality Monitoring & Governance

**Goal**: Build comprehensive monitoring, alerting, and quality governance for production RAG system

### 9.1 Live Quality Dashboard + Meta-Observability
**Priority**: MEDIUM | **Timeline**: Week 7-8

**Objective**: Real-time quality metrics visualization with self-improvement monitoring
- Build on Phase 5 evaluation daemon
- Real-time quality metrics dashboard
- Alert system for quality degradation
- Performance trend analysis and reporting
- **Meta-Observability**: Monitor the health of self-improvement machinery

**Dashboard Sections**:
1. **Query Quality Metrics**: Overall scores, error rates, intent performance
2. **Self-Improvement Health**: 
   - Config changes per week
   - Pattern promotions/demotions
   - Revert events and backup usage
   - Intents with persistent low scores
   - Oscillating configs (unstable tuning)
3. **Judge Model Performance**: Throughput, error rates, calibration metrics
4. **Cost & Latency Tracking**: Token usage, response times, cost per intent

**Implementation**:
```python
# Files to create/modify:
- app/monitoring/quality_dashboard.py (comprehensive metrics)
- app/monitoring/alert_system.py (quality + meta alerts)
- app/monitoring/meta_observer.py (self-improvement health)
- static/dashboard.html (multi-section interface)
```

### 9.2 Evaluation Sampling Strategy + Judge Calibration
**Priority**: MEDIUM | **Timeline**: Week 8

**Objective**: Intelligent evaluation sampling and judge model reliability

**Stratified Sampling Strategy**:
- **Per-Intent Minimum Coverage**: Guarantee X evaluations per intent per week
- **Rare Intent Prioritization**: Extra weight for low-frequency intents
- **Change-Aware Sampling**: Prioritize recently tuned intents/configs
- **Quality-Based Sampling**: Focus on historically low-scoring query types

**Judge Model Calibration**:
- Compare judge scores vs human labels on golden dataset
- Track judge-human agreement rates over time
- Optional dual-judge consistency checks for critical flows
- Detect judge model drift and recalibration needs

**Implementation**:
```python
# Files to create:
- app/monitoring/sampling_strategy.py (intelligent sampling)
- app/core/judge_calibration.py (reliability checks)
- Tests/test_judge_calibration.py (validation)
```

### 9.3 A/B Testing Framework + Data/Schema Drift Monitoring
**Priority**: MEDIUM | **Timeline**: Week 8-9

**Objective**: Systematic testing with production safety monitoring

**A/B Testing Framework**:
- **Variant Definition**: Different prompts, retrieval limits, routing strategies
- **Assignment Strategy**: By user ID, intent, or time window
- **Success Metrics**: Judge scores, latency, cost, user feedback
- **Statistical Significance**: Automated winner detection with confidence intervals

**Data & Schema Drift Monitoring**:
- **Neo4j Schema Monitoring**: Track label/property changes over time
- **Cardinality Drift**: Monitor data distribution changes (new products, regions)
- **Schema Sanity Tests**: Core Cypher queries that must remain valid
- **Automated Alerts**: Trigger golden QA re-runs on schema changes

**Implementation**:
```python
# Files to create:
- app/monitoring/experiment_manager.py (A/B testing)
- app/monitoring/schema_monitor.py (drift detection)
- Tests/test_experiment_manager.py (validation)
- Tests/test_schema_monitor.py (validation)
```

### 9.4 Human-in-the-Loop Integration + Runtime Safety
**Priority**: LOW | **Timeline**: Week 9-10

**Objective**: Close feedback loop with safety guardrails

**Human Feedback Hooks**:
- **Answer Quality Feedback**: "Mark as wrong/great" with trace_id mapping
- **Canonical Answer Pinning**: Human-verified answers for specific queries
- **Golden Dataset Contribution**: Feed high-quality human feedback into golden set

**Runtime Safety Guardrails**:
- **Low Confidence Handling**: When factual_correctness < threshold:
  - Add confidence hedging: "I'm not fully confident..."
  - Show raw data more literally
  - Avoid speculation and extrapolation
- **Intent-Specific Safety**: Conservative behavior for high-error intents

**Implementation**:
```python
# Files to create:
- app/api/feedback_routes.py (feedback endpoints)
- app/core/feedback_store.py (feedback persistence)
- app/core/answer_safety.py (runtime guardrails)
- Tests/test_feedback_flow.py (validation)
```

## 🧠 Phase 10: Advanced Self-Learning

**Goal**: Fully automated quality enhancement and continuous improvement

### 10.1 Pattern Recognition & Learning + Pattern Library Management
**Priority**: FUTURE | **Timeline**: Week 10+

**Objective**: Identify and learn from successful patterns with intelligent lifecycle management
- Success pattern extraction from high-scoring traces
- Failure pattern analysis from low-scoring traces
- Automatic prompt optimization
- Self-improving query understanding

**Pattern Library Quality Management**:
- **Pattern Metrics Tracking**: Track per-pattern performance metrics
  ```json
  {
    "pattern_id": "vendor_count_basic",
    "eval_count": 45,
    "avg_overall_score": 8.7,
    "retrieval_error_ratio": 0.05,
    "usage_count": 156,
    "production_optimized": true
  }
  ```

- **Pattern Promotion Policy**: Promote to production only when:
  - eval_count >= 20
  - avg_overall_score >= 8.5
  - retrieval_error_ratio < 0.1

- **Pattern Demotion/Retirement**: When patterns show:
  - Persistent low scores over 50+ evaluations
  - High semantic mismatch between examples and actual usage
  - Overly broad matching (absorbing unrelated queries)

- **Pattern Cleanup & Optimization**:
  - Merge near-duplicate patterns automatically
  - Split overly broad patterns by adding temporal/entity features
  - Deduplication based on semantic similarity

**Implementation**:
```python
# Files to create:
- app/core/pattern_manager.py (lifecycle management)
- app/core/pattern_quality.py (metrics and scoring)
- Tests/test_pattern_quality.py (validation)
```

### 10.2 Dynamic Model Selection + Cost/Latency Optimization
**Priority**: FUTURE | **Timeline**: Week 11+

**Objective**: Intelligent model routing
- Query complexity → model selection mapping
- Performance-based model switching
- Cost-optimized model routing
- Multi-model ensemble approaches

### 10.3 Continuous Improvement Engine
**Priority**: FUTURE | **Timeline**: Week 12+

**Objective**: Fully automated quality enhancement
- Self-tuning based on evaluation trends
- Automatic configuration optimization
- Performance regression detection and rollback
- Adaptive learning mechanisms

## 🎯 Immediate Action Plan (Next 2 Weeks)

### Week 1: Golden Dataset & Quality Analysis
1. **Day 1-3**: Create Golden Dataset & Regression Suite (Phase 7.0)
   - Curate 20-30 high-quality QA pairs covering all intents
   - Implement regression test harness
   - Establish baseline scores for golden set
   
2. **Day 4-5**: Run comprehensive evaluation on existing traces
   ```bash
   python -m app.monitoring.eval_runner --max-traces 500
   python Tests/evaluate_traces.py --summary
   python Tests/test_golden_regression.py  # New golden set validation
   ```

2. **Day 3-4**: Analyze evaluation results for quality patterns
   - Identify top error types by intent
   - Find lowest-scoring query patterns
   - Document improvement opportunities

3. **Day 5-7**: Implement intent classification refinement
   - Create `app/core/intent_analyzer.py`
   - Add confidence scoring
   - Test with existing traces

### Week 2: Multi-Part Query Enhancement
1. **Day 8-10**: Implement query decomposition
   - Create `app/core/query_decomposer.py`
   - Handle "how many X and what Y" patterns
   - Test with complex queries

2. **Day 11-12**: Response assembly improvements
   - Create `app/core/response_assembler.py`
   - Comprehensive answer generation
   - Validate completeness

3. **Day 13-14**: Integration testing and validation
   - End-to-end testing with judge model
   - Performance impact assessment
   - Deploy improvements

## 📋 Success Criteria & KPIs

### Primary Quality Metrics
- **Overall Score**: >8.5 average (current baseline TBD)
- **Factual Correctness**: >9.0 average
- **Grounded in Context**: >8.0 average
- **Helpfulness**: >8.5 average

### Error Rate Targets
- **Retrieval Errors**: <10% (from current baseline)
- **Reasoning Errors**: <5%
- **Missing Knowledge**: <15%
- **No Errors**: >70%

### Performance & Cost Metrics (Multi-Objective Optimization)
- **Query Response Time**: <3 seconds average, <5 seconds p95
- **LLM Token Usage**: Track and optimize per intent
- **Cost per Query**: Minimize while maintaining quality thresholds
- **Intent Classification Accuracy**: >95%
- **Multi-part Query Completion**: >90%
- **User Satisfaction**: >8.0/10 (when feedback system implemented)

### Quality Governance Metrics
- **Golden Dataset Regression**: 0% failures on core use cases
- **Judge-Human Agreement**: >85% on calibration set
- **Pattern Quality**: >80% of patterns meet promotion criteria
- **Schema Drift Detection**: <24 hour alert response time
- **A/B Test Confidence**: >95% statistical significance for changes

## 🛠 Tools & Infrastructure

### Existing Tools (Ready to Use)
```bash
# Evaluation and monitoring
python -m app.monitoring.eval_runner --max-traces 100
python -m app.monitoring.tuning_runner --suggest-only
python Tests/evaluate_traces.py --summary

# Testing and validation
python Tests/test_llm_integration.py
python Tests/test_tracing.py
python Tests/test_evaluation.py
```

### New Tools (To Be Implemented)
```bash
# Golden dataset and regression testing
python Tests/test_golden_regression.py
python Tests/create_golden_dataset.py --from-traces --top-scoring

# Advanced monitoring and governance
python -m app.monitoring.sampling_strategy --stratified --intent-coverage
python -m app.monitoring.judge_calibration --compare-human-labels
python -m app.monitoring.schema_monitor --detect-drift
python -m app.monitoring.experiment_manager --create-variant

# Pattern library management
python -m app.core.pattern_manager --promote --demote --cleanup
python Tests/test_pattern_quality.py

# Human feedback and safety
python -m app.api.feedback_routes --export-canonical-answers
python Tests/test_answer_safety.py
```

### Data Sources
- `/app/data/traces.jsonl` - Complete RAG pipeline execution data
- `/app/data/eval_results.jsonl` - Judge model quality assessments
- `/app/data/eval_summary.json` - Aggregated metrics by intent
- `config/rag_config.yaml` - Current configuration parameters

### Development Environment
```bash
# Activate environment
venv\Scripts\activate

# Run development server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8002

# Access web UI for testing
http://localhost:8002/promptui
```

## 📝 Documentation Updates Required

As improvements are implemented, update:
- `docs/CHANGELOG.md` - Version history with quality improvements
- `docs/ADR.md` - Architecture decisions for new components
- `docs/SchemaSync.md` - Any schema changes or new data structures
- This work plan document - Progress tracking and lessons learned

## 🔄 Continuous Improvement Process

1. **Daily Golden Set Validation**: Ensure core functionality remains intact
2. **Weekly Comprehensive Evaluation**: Run stratified sampling on production traces
3. **Quality & Meta-Health Review**: Analyze metrics trends and self-improvement health
4. **Judge Calibration Checks**: Validate judge model reliability monthly
5. **Targeted Improvements**: Focus on lowest-performing areas with A/B testing
6. **Pattern Library Maintenance**: Promote/demote patterns based on performance
7. **Schema Drift Monitoring**: Detect and respond to data/schema changes
8. **Auto-Tuning with Safety**: Let system optimize with golden set validation
9. **Human Feedback Integration**: Incorporate user feedback into golden dataset
10. **Documentation & Audit Trail**: Maintain complete change history and learnings

---

## 🚀 Getting Started

**For new team members or clean chat sessions:**

1. **Understand the foundation**: Review Phases 1-6 documentation in `docs/Self-ImprovingRAG/`
2. **Run baseline evaluation**: Execute evaluation tools to understand current quality
3. **Identify focus area**: Choose from Phase 7-10 based on evaluation results
4. **Implement incrementally**: Small, measurable improvements with validation
5. **Leverage infrastructure**: Use existing tracing, evaluation, and auto-tuning systems

**Current Priority**: Phase 7.0 (Golden Dataset & Regression Suite) - Critical foundation that must be implemented first to ensure safe, measurable improvements.

**Next Priority**: Phase 7.1 (Intent Classification Refinement) - Build on golden dataset foundation for immediate query quality impact.

The system is production-ready with comprehensive evaluation infrastructure. Focus on data-driven improvements using the judge model feedback and auto-tuning capabilities already in place.