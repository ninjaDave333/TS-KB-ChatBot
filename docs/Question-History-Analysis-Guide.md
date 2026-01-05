# Question History Analysis Guide

## Overview

The Question History Analysis tool provides comprehensive insights into your RAG system's performance by analyzing multiple data sources and generating actionable improvement suggestions.

## Quick Start

### Basic Analysis
```bash
python -m Tests.analyze_question_history
```

### Detailed Analysis
```bash
python -m Tests.analyze_question_history --detailed
```

### Export to CSV
```bash
python -m Tests.analyze_question_history --export-csv
```

## Data Sources

The tool analyzes the following data files from your `data/` directory:

1. **eval_results.jsonl** - Judge model evaluation scores
2. **query_patterns.json** - Learned patterns and failure analysis  
3. **self_improvement_results.json** - Intent classification performance
4. **production_insights.json** - User behavior patterns

## Analysis Sections

### 1. Evaluation Scores Analysis
- Overall performance metrics across all intents
- Intent-specific performance breakdown
- Score distribution (overall_score, factual_correctness, grounded_in_context, helpfulness)

### 2. Learned Patterns Analysis
- Total patterns learned and their success rates
- Most frequently used patterns
- Pattern failure analysis with error types

### 3. Intent Classification Analysis
- Success rate by intent type
- Error pattern distribution
- Failed query analysis with improvement suggestions

### 4. User Behavior Analysis
- Query volume by type
- User refinement patterns
- Data quality issues affecting user experience

### 5. Improvement Suggestions
Automated suggestions based on data patterns:
- 🎯 Intent improvements for low-scoring categories
- 🔧 Pattern fixes for high-failure cases
- 📝 Keyword additions for failed classifications
- 🧹 Data quality issue resolution

## Sample Output

```
============================================================
📊 QUESTION HISTORY ANALYSIS REPORT
============================================================

🎯 EVALUATION SCORES ANALYSIS
----------------------------------------
Total Evaluations: 15
Intents Covered: CLIENT_HISTORY, PRODUCT_INFO
overall_score: 7.2/10 (range: 6.0-9.1)
factual_correctness: 8.1/10 (range: 7.0-9.3)

🧠 LEARNED PATTERNS ANALYSIS
----------------------------------------
Total Patterns: 14
Total Failures: 4
Avg Success Rate: 0.957
Total Usage: 25

🎪 INTENT CLASSIFICATION ANALYSIS
----------------------------------------
Total Queries: 20
Success Rate: 85%
Failed Queries: 3

Intent Distribution:
  strict_v1: 4✅ 0❌ (100.0% success)
  sales_v1: 3✅ 0❌ (100.0% success)
  calendar_v1: 5✅ 0❌ (100.0% success)
  product_v1: 5✅ 0❌ (100.0% success)
  unknown: 0✅ 3❌ (0.0% success)

💡 IMPROVEMENT SUGGESTIONS
----------------------------------------
1. 🎯 Improve CLIENT_HISTORY intent: avg score 6.7/10 - review prompt profile and examples
2. 📝 Add keywords for 3 failed queries - see actionable_keywords section
3. 🔧 Fix top failure pattern: 2 failures in {"complexity": 3, "entities": ["client"]}
```

## CSV Export Format

The CSV export includes all data points for external analysis:

| Column | Description |
|--------|-------------|
| source | Data source (evaluation, learned_pattern, failure) |
| intent | Intent type or pattern category |
| trace_id | Unique identifier for the record |
| overall_score | Judge model overall score (0-10) |
| factual_correctness | Factual accuracy score (0-10) |
| grounded_in_context | Context grounding score (0-10) |
| helpfulness | Helpfulness score (0-10) |
| primary_issue | Main issue identified |
| success_rate | Pattern success rate (0-1) |
| usage_count | Number of times pattern was used |
| error_type | Type of error encountered |

## Integration with Self-Improvement

This tool complements the existing self-learning system:

1. **Run Analysis**: Use this tool to identify improvement opportunities
2. **Apply Changes**: Update prompts, keywords, or schema based on suggestions
3. **Monitor Impact**: Re-run analysis to measure improvement effectiveness
4. **Iterate**: Continuous improvement cycle based on data insights

## Troubleshooting

### No Data Available
If you see "No [data type] available" messages:
- Ensure the corresponding JSON files exist in your `data/` directory
- Check that the files contain valid JSON data
- Verify the system has been running and collecting data

### Missing Metrics
Some metrics may be missing if:
- Data files are incomplete or corrupted
- The system hasn't collected enough data yet
- File permissions prevent reading

### Performance Issues
For large datasets:
- Use `--detailed` sparingly for initial analysis
- Consider filtering data files to recent entries
- Export to CSV for analysis in external tools

## Best Practices

1. **Regular Analysis**: Run weekly to identify trends
2. **Before/After Comparison**: Analyze before and after making changes
3. **Export for Trends**: Keep CSV exports to track improvements over time
4. **Focus on Actionable Items**: Prioritize suggestions with highest impact
5. **Validate Changes**: Re-run analysis after implementing suggestions

## Command Reference

```bash
# Basic analysis
python -m Tests.analyze_question_history

# Detailed analysis with all metrics
python -m Tests.analyze_question_history --detailed

# Export results to CSV
python -m Tests.analyze_question_history --export-csv

# Custom data directory
python -m Tests.analyze_question_history --data-dir /path/to/data

# Combine options
python -m Tests.analyze_question_history --detailed --export-csv
```