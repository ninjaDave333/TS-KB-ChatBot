#!/usr/bin/env python3
"""
Question History Analysis Tool for Self-Improving RAG

Analyzes multiple data sources:
- eval_results.jsonl: Judge model evaluation scores
- query_patterns.json: Learned patterns and failure analysis
- self_improvement_results.json: Intent classification and error patterns
- production_insights.json: User behavior patterns

Usage:
    python -m Tests.analyze_question_history
    python -m Tests.analyze_question_history --export-csv
    python -m Tests.analyze_question_history --detailed
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict, Counter
import statistics

class QuestionHistoryAnalyzer:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.eval_results = []
        self.query_patterns = {}
        self.self_improvement = {}
        self.production_insights = {}
        
    def load_data(self):
        """Load all available data sources"""
        print("🔍 Loading question history data...")
        
        # Load evaluation results
        eval_file = self.data_dir / "eval_results.jsonl"
        if eval_file.exists():
            with open(eval_file, 'r') as f:
                self.eval_results = [json.loads(line) for line in f if line.strip()]
            print(f"   ✅ Loaded {len(self.eval_results)} evaluation results")
        
        # Load query patterns
        patterns_file = self.data_dir / "query_patterns.json"
        if patterns_file.exists():
            with open(patterns_file, 'r') as f:
                self.query_patterns = json.load(f)
            print(f"   ✅ Loaded {len(self.query_patterns.get('patterns', {}))} learned patterns")
        
        # Load self-improvement results
        self_improve_file = self.data_dir / "self_improvement_results.json"
        if self_improve_file.exists():
            with open(self_improve_file, 'r') as f:
                self.self_improvement = json.load(f)
            print(f"   ✅ Loaded self-improvement analysis")
        
        # Load production insights
        insights_file = self.data_dir / "production_insights.json"
        if insights_file.exists():
            with open(insights_file, 'r') as f:
                self.production_insights = json.load(f)
            print(f"   ✅ Loaded production insights")
    
    def analyze_evaluation_scores(self) -> Dict[str, Any]:
        """Analyze judge model evaluation scores"""
        if not self.eval_results:
            return {"message": "No evaluation data available"}
        
        # Group by intent
        by_intent = defaultdict(list)
        all_scores = []
        
        for result in self.eval_results:
            intent = result.get('intent', 'unknown')
            scores = result.get('scores', {})
            by_intent[intent].append(scores)
            all_scores.append(scores)
        
        # Calculate statistics
        analysis = {
            "total_evaluations": len(self.eval_results),
            "intents_covered": list(by_intent.keys()),
            "overall_metrics": self._calculate_score_stats(all_scores),
            "by_intent": {}
        }
        
        for intent, scores_list in by_intent.items():
            analysis["by_intent"][intent] = {
                "count": len(scores_list),
                "metrics": self._calculate_score_stats(scores_list)
            }
        
        return analysis
    
    def _calculate_score_stats(self, scores_list: List[Dict]) -> Dict[str, float]:
        """Calculate statistics for score metrics"""
        if not scores_list:
            return {}
        
        metrics = ['overall_score', 'factual_correctness', 'grounded_in_context', 'helpfulness']
        stats = {}
        
        for metric in metrics:
            values = [s.get(metric, 0) for s in scores_list if metric in s]
            if values:
                stats[metric] = {
                    "avg": round(statistics.mean(values), 2),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values)
                }
        
        return stats
    
    def analyze_learned_patterns(self) -> Dict[str, Any]:
        """Analyze learned query patterns and failures"""
        if not self.query_patterns:
            return {"message": "No learned patterns data available"}
        
        patterns = self.query_patterns.get('patterns', {})
        failures = self.query_patterns.get('failure_analysis', {})
        
        # Pattern success analysis
        successful_patterns = []
        for pattern_key, pattern_data in patterns.items():
            successful_patterns.append({
                "pattern": pattern_key,
                "success_rate": pattern_data.get('success_rate', 0),
                "usage_count": pattern_data.get('usage_count', 0),
                "avg_execution_time": pattern_data.get('avg_execution_time', 0),
                "example_queries": pattern_data.get('example_queries', [])[:2]  # First 2 examples
            })
        
        # Sort by usage count
        successful_patterns.sort(key=lambda x: x['usage_count'], reverse=True)
        
        # Failure analysis
        failure_summary = []
        for pattern_key, failure_data in failures.items():
            failure_summary.append({
                "pattern": pattern_key,
                "failure_count": failure_data.get('failure_count', 0),
                "error_types": failure_data.get('error_types', {}),
                "example_failures": failure_data.get('example_failures', [])[:1]  # First example
            })
        
        # Sort by failure count
        failure_summary.sort(key=lambda x: x['failure_count'], reverse=True)
        
        return {
            "total_patterns": len(patterns),
            "total_failures": len(failures),
            "top_patterns": successful_patterns[:10],
            "top_failures": failure_summary[:5],
            "pattern_performance": {
                "avg_success_rate": round(statistics.mean([p.get('success_rate', 0) for p in patterns.values()]), 3),
                "total_usage": sum(p.get('usage_count', 0) for p in patterns.values())
            }
        }
    
    def analyze_intent_classification(self) -> Dict[str, Any]:
        """Analyze intent classification performance"""
        if not self.self_improvement:
            return {"message": "No self-improvement data available"}
        
        summary = self.self_improvement.get('summary', {})
        successful_patterns = self.self_improvement.get('successful_patterns', {})
        failures = self.self_improvement.get('failures', {})
        improvements = self.self_improvement.get('improvements', [])
        
        # Intent distribution
        intent_distribution = {}
        for intent, data in successful_patterns.items():
            intent_distribution[intent] = {
                "successful_queries": data.get('count', 0),
                "avg_response_time": round(data.get('avg_response_time', 0), 2)
            }
        
        # Add failed queries by intent
        failed_by_intent = failures.get('by_intent', {})
        for intent, count in failed_by_intent.items():
            if intent not in intent_distribution:
                intent_distribution[intent] = {"successful_queries": 0, "avg_response_time": 0}
            intent_distribution[intent]["failed_queries"] = count
        
        # Error analysis
        error_analysis = failures.get('by_error', {})
        
        # Improvement suggestions
        suggested_keywords = self.self_improvement.get('actionable_keywords', {})
        
        return {
            "overall_performance": {
                "total_queries": summary.get('total_queries', 0),
                "success_rate": f"{summary.get('success_rate', 0)}%",
                "failed_queries": summary.get('failed', 0)
            },
            "intent_distribution": intent_distribution,
            "error_patterns": error_analysis,
            "improvement_opportunities": len(improvements),
            "suggested_keywords": suggested_keywords
        }
    
    def analyze_user_behavior(self) -> Dict[str, Any]:
        """Analyze user behavior patterns"""
        if not self.production_insights:
            return {"message": "No production insights available"}
        
        query_volume = self.production_insights.get('query_volume_by_type', {})
        performance = self.production_insights.get('average_performance', {})
        refinement_patterns = self.production_insights.get('refinement_patterns', {})
        data_quality_issues = self.production_insights.get('data_quality_issues', [])
        recommendations = self.production_insights.get('recommendations', [])
        
        return {
            "query_types": query_volume,
            "performance_by_type": performance,
            "user_refinement_patterns": refinement_patterns,
            "data_quality_issues": len(data_quality_issues),
            "top_issues": data_quality_issues[:3],
            "recommendations": recommendations
        }
    
    def generate_improvement_suggestions(self) -> List[str]:
        """Generate actionable improvement suggestions"""
        suggestions = []
        
        # From evaluation scores
        if self.eval_results:
            low_scoring_intents = []
            by_intent = defaultdict(list)
            for result in self.eval_results:
                intent = result.get('intent', 'unknown')
                overall_score = result.get('scores', {}).get('overall_score', 0)
                by_intent[intent].append(overall_score)
            
            for intent, scores in by_intent.items():
                avg_score = statistics.mean(scores)
                if avg_score < 7.0:
                    low_scoring_intents.append((intent, avg_score))
                    suggestions.append(f"🎯 Improve {intent} intent: avg score {avg_score:.1f}/10 - review prompt profile and examples")
        
        # From learned patterns
        if self.query_patterns:
            failures = self.query_patterns.get('failure_analysis', {})
            if failures:
                top_failure = max(failures.items(), key=lambda x: x[1].get('failure_count', 0))
                pattern, failure_data = top_failure
                suggestions.append(f"🔧 Fix top failure pattern: {failure_data.get('failure_count', 0)} failures in {pattern}")
        
        # From intent classification
        if self.self_improvement:
            failed_queries = self.self_improvement.get('failures', {}).get('total', 0)
            if failed_queries > 0:
                suggestions.append(f"📝 Add keywords for {failed_queries} failed queries - see actionable_keywords section")
        
        # From user behavior
        if self.production_insights:
            issues = self.production_insights.get('data_quality_issues', [])
            if issues:
                suggestions.append(f"🧹 Address {len(issues)} data quality issues affecting user experience")
        
        if not suggestions:
            suggestions.append("✅ System performing well - continue monitoring for new patterns")
        
        return suggestions
    
    def export_to_csv(self, output_file: str = "question_history_analysis.csv"):
        """Export analysis results to CSV"""
        import csv
        
        rows = []
        
        # Add evaluation results
        for result in self.eval_results:
            scores = result.get('scores', {})
            rows.append({
                'source': 'evaluation',
                'intent': result.get('intent', 'unknown'),
                'trace_id': result.get('trace_id', ''),
                'overall_score': scores.get('overall_score', 0),
                'factual_correctness': scores.get('factual_correctness', 0),
                'grounded_in_context': scores.get('grounded_in_context', 0),
                'helpfulness': scores.get('helpfulness', 0),
                'primary_issue': result.get('primary_issue', ''),
                'success_rate': '',
                'usage_count': '',
                'error_type': ''
            })
        
        # Add learned patterns
        patterns = self.query_patterns.get('patterns', {})
        for pattern_key, pattern_data in patterns.items():
            rows.append({
                'source': 'learned_pattern',
                'intent': 'pattern',
                'trace_id': pattern_key,
                'overall_score': '',
                'factual_correctness': '',
                'grounded_in_context': '',
                'helpfulness': '',
                'primary_issue': '',
                'success_rate': pattern_data.get('success_rate', 0),
                'usage_count': pattern_data.get('usage_count', 0),
                'error_type': ''
            })
        
        # Add failures
        failures = self.query_patterns.get('failure_analysis', {})
        for pattern_key, failure_data in failures.items():
            for error_type, count in failure_data.get('error_types', {}).items():
                rows.append({
                    'source': 'failure',
                    'intent': 'failure',
                    'trace_id': pattern_key,
                    'overall_score': '',
                    'factual_correctness': '',
                    'grounded_in_context': '',
                    'helpfulness': '',
                    'primary_issue': error_type,
                    'success_rate': '',
                    'usage_count': failure_data.get('failure_count', 0),
                    'error_type': error_type
                })
        
        # Write CSV
        if rows:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
            print(f"📊 Exported {len(rows)} records to {output_file}")
        else:
            print("❌ No data to export")
    
    def run_analysis(self, detailed: bool = False, export_csv: bool = False):
        """Run complete analysis"""
        self.load_data()
        
        print("\n" + "="*60)
        print("📊 QUESTION HISTORY ANALYSIS REPORT")
        print("="*60)
        
        # 1. Evaluation Scores Analysis
        print("\n🎯 EVALUATION SCORES ANALYSIS")
        print("-" * 40)
        eval_analysis = self.analyze_evaluation_scores()
        if "message" not in eval_analysis:
            print(f"Total Evaluations: {eval_analysis['total_evaluations']}")
            print(f"Intents Covered: {', '.join(eval_analysis['intents_covered'])}")
            
            overall = eval_analysis['overall_metrics']
            if overall:
                for metric, stats in overall.items():
                    if isinstance(stats, dict):
                        print(f"{metric}: {stats['avg']}/10 (range: {stats['min']}-{stats['max']})")
            
            if detailed:
                print("\nBy Intent:")
                for intent, data in eval_analysis['by_intent'].items():
                    print(f"  {intent}: {data['count']} evaluations")
                    for metric, stats in data['metrics'].items():
                        if isinstance(stats, dict):
                            print(f"    {metric}: {stats['avg']}/10")
        else:
            print(eval_analysis['message'])
        
        # 2. Learned Patterns Analysis
        print("\n🧠 LEARNED PATTERNS ANALYSIS")
        print("-" * 40)
        patterns_analysis = self.analyze_learned_patterns()
        if "message" not in patterns_analysis:
            print(f"Total Patterns: {patterns_analysis['total_patterns']}")
            print(f"Total Failures: {patterns_analysis['total_failures']}")
            perf = patterns_analysis['pattern_performance']
            print(f"Avg Success Rate: {perf['avg_success_rate']}")
            print(f"Total Usage: {perf['total_usage']}")
            
            if detailed and patterns_analysis['top_patterns']:
                print("\nTop Patterns:")
                for i, pattern in enumerate(patterns_analysis['top_patterns'][:5], 1):
                    print(f"  {i}. Usage: {pattern['usage_count']}, Success: {pattern['success_rate']}")
                    if pattern['example_queries']:
                        print(f"     Example: \"{pattern['example_queries'][0]}\"")
        else:
            print(patterns_analysis['message'])
        
        # 3. Intent Classification Analysis
        print("\n🎪 INTENT CLASSIFICATION ANALYSIS")
        print("-" * 40)
        intent_analysis = self.analyze_intent_classification()
        if "message" not in intent_analysis:
            perf = intent_analysis['overall_performance']
            print(f"Total Queries: {perf['total_queries']}")
            print(f"Success Rate: {perf['success_rate']}")
            print(f"Failed Queries: {perf['failed_queries']}")
            
            print("\nIntent Distribution:")
            for intent, data in intent_analysis['intent_distribution'].items():
                successful = data.get('successful_queries', 0)
                failed = data.get('failed_queries', 0)
                total = successful + failed
                if total > 0:
                    success_pct = (successful / total) * 100
                    print(f"  {intent}: {successful}✅ {failed}❌ ({success_pct:.1f}% success)")
            
            if intent_analysis['error_patterns']:
                print(f"\nTop Errors: {', '.join(intent_analysis['error_patterns'].keys())}")
        else:
            print(intent_analysis['message'])
        
        # 4. User Behavior Analysis
        print("\n👥 USER BEHAVIOR ANALYSIS")
        print("-" * 40)
        behavior_analysis = self.analyze_user_behavior()
        if "message" not in behavior_analysis:
            print("Query Types:")
            for query_type, count in behavior_analysis['query_types'].items():
                print(f"  {query_type}: {count} queries")
            
            if behavior_analysis['data_quality_issues'] > 0:
                print(f"\nData Quality Issues: {behavior_analysis['data_quality_issues']}")
                for issue in behavior_analysis['top_issues']:
                    print(f"  - {issue.get('issue', 'Unknown')}: {issue.get('frequency', 0)} occurrences")
        else:
            print(behavior_analysis['message'])
        
        # 5. Improvement Suggestions
        print("\n💡 IMPROVEMENT SUGGESTIONS")
        print("-" * 40)
        suggestions = self.generate_improvement_suggestions()
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")
        
        # Export CSV if requested
        if export_csv:
            print("\n📊 EXPORTING DATA")
            print("-" * 40)
            self.export_to_csv()
        
        print("\n" + "="*60)
        print("✅ Analysis Complete")
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description='Analyze question history for self-improvement')
    parser.add_argument('--detailed', action='store_true', help='Show detailed analysis')
    parser.add_argument('--export-csv', action='store_true', help='Export results to CSV')
    parser.add_argument('--data-dir', default='data', help='Data directory path')
    
    args = parser.parse_args()
    
    analyzer = QuestionHistoryAnalyzer(args.data_dir)
    analyzer.run_analysis(detailed=args.detailed, export_csv=args.export_csv)

if __name__ == "__main__":
    main()