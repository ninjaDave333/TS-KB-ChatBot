# Tests Directory

## Production Monitoring & Analytics

### analyze_feedback.py
Analyzes user feedback (thumbs up/down) from production to track satisfaction rates and identify improvement areas.
- **Input**: `/home/ubuntu/meetingsBotLogs/persistentData/user_feedback.jsonl`
- **Output**: JSON with satisfaction rate, positive/negative counts, breakdown by intent and user
- **Usage**: `python analyze_feedback.py`

### analyze_metrics.py
Analyzes production metrics to identify patterns, errors, and performance trends.
- **Input**: `/home/ubuntu/meetingsBotLogs/persistentData/production_metrics.json`
- **Output**: Summary statistics and insights
- **Usage**: `python analyze_metrics.py`

### analyze_production_patterns.py
Deep analysis of production query patterns to identify common failures and optimization opportunities.
- **Input**: Production metrics and query history
- **Output**: Pattern analysis with recommendations

## Intent Classification Testing

### production_intent_test.py
Tests intent classification accuracy using real production queries with manual labels.
- **Accuracy**: 100% on 20 production queries
- **No LLM required**: Pure keyword-based classification
- **Usage**: Upload to DGX and run: `python3 production_intent_test.py`

### intent_test_detailed.py
Tests intent classification using Ollama-generated synthetic queries (less reliable due to generation inconsistency).
- **Requires**: Ollama running on DGX with llama3.2:3b
- **Output**: `intent_test_results.json` with detailed misclassifications

### dgx_tuner.py / dgx_tuner_verbose.py
Analyzes production metrics to suggest keyword improvements for intent classification.
- **Input**: Production metrics JSON
- **Output**: Keyword recommendations for each intent

### offline_intent_tuner.py
Offline tool for tuning intent classification keywords without production dependencies.

## Query Generation & Testing

### generate_synthetic_queries.py
Generates synthetic queries using Ollama for testing (has issues with SQL generation instead of natural language).
- **Status**: Needs prompt improvements
- **Requires**: Ollama on DGX

### generate_queries_dgx.py
DGX-specific query generation for testing.

### batch_query_test.py
Batch testing tool for running multiple queries against the API.

## Evaluation & Validation

### overnight_ragas_eval.py
RAGAS evaluation script for measuring answer quality (blocked by API authentication).
- **Status**: Requires JWT token for production API access

### overnight_validation.py
Overnight validation testing for continuous quality monitoring.

### teams_ragas_evaluation.py
Specialized RAGAS evaluation for Teams/calendar-related queries.

## Streaming & Pipeline

### streaming_pipeline.py
Streaming pipeline for simultaneous query generation and evaluation.

### offline_streaming.py
Offline version of streaming pipeline for testing without production dependencies.

## Self-Improvement

### production_self_improve.py
Production self-improvement script that learns from successful queries.

## DGX Deployment

### deploy_to_dgx.sh
Shell script for deploying code to DGX for offline testing.

### DGX_INSTRUCTIONS.md
Instructions for setting up and running tests on DGX.

## Archived/Removed
The following temporary files were removed during cleanup:
- All `test_*.py` files (one-off tests)
- All `debug_*.py` files (debugging scripts)
- All `check_*.py` files (data validation scripts)
- All `verify_*.py` files (verification scripts)
- All `validate_*.py` files (schema validation)
- All `.ps1` PowerShell scripts
- All `ragas_*.json` result files
- All `batch_test_results_*.json` files
