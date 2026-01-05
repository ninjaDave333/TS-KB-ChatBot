#!/usr/bin/env python3
"""
Production Traces Analysis Tool

Analyzes traces.jsonl from production deployment to extract:
- Query patterns and success rates
- Intent classification performance
- Error patterns and failure analysis
- User behavior insights
- Performance metrics

Usage:
    python -m Tests.analyze_traces --data-dir ref_data
    python -m Tests.analyze_traces --data-dir ref_data --export-csv
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict, Counter
import statistics
from datetime import datetime, timedelta

class TracesAnalyzer:
    def __init__(self, data_dir: str = "ref_data"):
        self.data_dir = Path(data_dir)
        self.traces = []
        
    def load_traces(self):
        """Load traces from traces.jsonl"""
        traces_file = self.data_dir / "traces.jsonl"
        if not traces_file.exists():
            print(f"❌ {traces_file} not found")
            return
            
        with open(traces_file, 'r', encoding='utf-8') as f:
            self.traces = [json.loads(line) for line in f if line.strip()]
        print(f"✅ Loaded {len(self.traces)} traces")
    
    def analyze_intent_performance(self) -> Dict[str, Any]:
        """Analyze intent classification and success rates"""
        by_intent = defaultdict(lambda: {"total": 0, "success": 0, "errors": []})
        routing_paths = Counter()
        
        for trace in self.traces:
            intent = trace.get('intent', 'unknown')
            routing = trace.get('routing_path', 'unknown')
            has_data = trace.get('neo4j_result_summary', {}).get('has_data', False)
            
            by_intent[intent]["total"] += 1
            if has_data:
                by_intent[intent]["success"] += 1
            else:
                by_intent[intent]["errors"].append(trace.get('trace_id'))
            
            routing_paths[routing] += 1
        
        # Calculate success rates
        intent_stats = {}
        for intent, data in by_intent.items():
            success_rate = (data["success"] / data["total"]) * 100 if data["total"] > 0 else 0
            intent_stats[intent] = {
                "total_queries": data["total"],
                "successful": data["success"],
                "success_rate": round(success_rate, 1),
                "error_count": len(data["errors"])
            }
        
        return {
            "intent_distribution": intent_stats,
            "routing_methods": dict(routing_paths),
            "total_traces": len(self.traces)
        }
    
    def analyze_query_patterns(self) -> Dict[str, Any]:
        """Analyze common query patterns and Cypher generation"""
        cypher_patterns = Counter()
        query_types = Counter()
        ai_vs_pattern = {"ai_generated": 0, "learned_pattern": 0, "other": 0}
        
        for trace in self.traces:
            cypher = trace.get('cypher_query', '')
            routing = trace.get('routing_path', '')
            
            # Extract query pattern
            if 'MATCH' in cypher:
                # Simple pattern extraction
                if 'Employee' in cypher and 'CalendarEvent' in cypher:
                    cypher_patterns['employee_calendar'] += 1
                elif 'Client' in cypher and 'OPPORTUNITY' in cypher:
                    cypher_patterns['client_opportunity'] += 1
                elif 'Recording' in cypher:
                    cypher_patterns['recording_analysis'] += 1
                elif 'Product' in cypher:
                    cypher_patterns['product_query'] += 1
                else:
                    cypher_patterns['other'] += 1
            
            # Routing analysis
            if 'ai_generated' in routing:
                ai_vs_pattern['ai_generated'] += 1
            elif 'learned_pattern' in routing:
                ai_vs_pattern['learned_pattern'] += 1
            else:
                ai_vs_pattern['other'] += 1
        
        return {
            "cypher_patterns": dict(cypher_patterns),
            "generation_methods": ai_vs_pattern,
            "pattern_efficiency": {
                "learned_pattern_rate": round((ai_vs_pattern['learned_pattern'] / len(self.traces)) * 100, 1),
                "ai_generation_rate": round((ai_vs_pattern['ai_generated'] / len(self.traces)) * 100, 1)
            }
        }
    
    def analyze_performance_metrics(self) -> Dict[str, Any]:
        """Analyze response times and data quality"""
        timestamps = []
        data_counts = []
        successful_queries = 0
        
        for trace in self.traces:
            # Parse timestamp
            try:
                ts = datetime.fromisoformat(trace['timestamp'].replace('Z', '+00:00'))
                timestamps.append(ts)
            except:
                pass
            
            # Data quality
            result_summary = trace.get('neo4j_result_summary', {})
            if result_summary.get('has_data', False):
                successful_queries += 1
                data_counts.append(result_summary.get('record_count', 0))
        
        # Time analysis
        time_analysis = {}
        if timestamps:
            timestamps.sort()
            time_analysis = {
                "date_range": {
                    "start": timestamps[0].isoformat(),
                    "end": timestamps[-1].isoformat(),
                    "span_days": (timestamps[-1] - timestamps[0]).days
                },
                "queries_per_day": round(len(timestamps) / max(1, (timestamps[-1] - timestamps[0]).days), 1)
            }
        
        # Data quality
        data_analysis = {}
        if data_counts:
            data_analysis = {
                "avg_records_returned": round(statistics.mean(data_counts), 1),
                "max_records": max(data_counts),
                "queries_with_data": len(data_counts),
                "empty_result_rate": round(((len(self.traces) - successful_queries) / len(self.traces)) * 100, 1)
            }
        
        return {
            "time_analysis": time_analysis,
            "data_quality": data_analysis,
            "overall_success_rate": round((successful_queries / len(self.traces)) * 100, 1)
        }
    
    def identify_failure_patterns(self) -> Dict[str, Any]:
        """Identify common failure patterns"""
        failures = []
        error_patterns = Counter()
        
        for trace in self.traces:
            result_summary = trace.get('neo4j_result_summary', {})
            if not result_summary.get('has_data', False):
                failures.append({
                    'trace_id': trace.get('trace_id'),
                    'intent': trace.get('intent', 'unknown'),
                    'routing': trace.get('routing_path', 'unknown'),
                    'cypher': trace.get('cypher_query', '')[:100] + '...' if trace.get('cypher_query') else 'None'
                })
                
                # Categorize error
                intent = trace.get('intent', 'unknown')
                if intent == 'unknown':
                    error_patterns['unknown_intent'] += 1
                elif not trace.get('cypher_query'):
                    error_patterns['no_cypher_generated'] += 1
                else:
                    error_patterns['empty_results'] += 1
        
        return {
            "total_failures": len(failures),
            "failure_rate": round((len(failures) / len(self.traces)) * 100, 1),
            "error_categories": dict(error_patterns),
            "sample_failures": failures[:5]  # First 5 failures
        }
    
    def generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Analyze intent performance
        intent_analysis = self.analyze_intent_performance()
        for intent, stats in intent_analysis['intent_distribution'].items():
            if stats['success_rate'] < 80 and stats['total_queries'] > 2:
                recommendations.append(f"🎯 Improve {intent} intent: {stats['success_rate']}% success rate ({stats['total_queries']} queries)")
        
        # Analyze routing efficiency
        pattern_analysis = self.analyze_query_patterns()
        learned_rate = pattern_analysis['pattern_efficiency']['learned_pattern_rate']
        if learned_rate < 50:
            recommendations.append(f"🧠 Increase learned pattern usage: currently {learned_rate}% (target: >50%)")
        
        # Analyze failures
        failure_analysis = self.identify_failure_patterns()
        if failure_analysis['failure_rate'] > 20:
            recommendations.append(f"🔧 Address high failure rate: {failure_analysis['failure_rate']}% of queries return no data")
        
        # Check for unknown intents
        unknown_count = intent_analysis['intent_distribution'].get('unknown', {}).get('total_queries', 0)
        if unknown_count > 5:
            recommendations.append(f"📝 Add intent classification for {unknown_count} 'unknown' queries")
        
        if not recommendations:
            recommendations.append("✅ System performing well - continue monitoring")
        
        return recommendations
    
    def export_csv(self, output_file: str = "traces_analysis.csv"):
        """Export traces to CSV for further analysis"""
        import csv
        
        rows = []
        for trace in self.traces:
            result_summary = trace.get('neo4j_result_summary', {})
            rows.append({
                'trace_id': trace.get('trace_id', ''),
                'timestamp': trace.get('timestamp', ''),
                'intent': trace.get('intent', 'unknown'),
                'routing_path': trace.get('routing_path', 'unknown'),
                'has_data': result_summary.get('has_data', False),
                'record_count': result_summary.get('record_count', 0),
                'cypher_length': len(trace.get('cypher_query', '')),
                'has_final_answer': bool(trace.get('final_answer'))
            })
        
        if rows:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
            print(f"📊 Exported {len(rows)} traces to {output_file}")
    
    def run_analysis(self, export_csv: bool = False):
        """Run complete analysis"""
        self.load_traces()
        
        if not self.traces:
            print("❌ No traces to analyze")
            return
        
        print("\n" + "="*60)
        print("📊 PRODUCTION TRACES ANALYSIS")
        print("="*60)
        
        # Intent Performance
        print("\n🎯 INTENT CLASSIFICATION PERFORMANCE")
        print("-" * 40)
        intent_analysis = self.analyze_intent_performance()
        print(f"Total Traces: {intent_analysis['total_traces']}")
        
        print("\nIntent Distribution:")
        for intent, stats in intent_analysis['intent_distribution'].items():
            print(f"  {intent}: {stats['total_queries']} queries, {stats['success_rate']}% success")
        
        print(f"\nRouting Methods: {intent_analysis['routing_methods']}")
        
        # Query Patterns
        print("\n🧠 QUERY PATTERN ANALYSIS")
        print("-" * 40)
        pattern_analysis = self.analyze_query_patterns()
        print("Cypher Patterns:")
        for pattern, count in pattern_analysis['cypher_patterns'].items():
            print(f"  {pattern}: {count} queries")
        
        efficiency = pattern_analysis['pattern_efficiency']
        print(f"\nGeneration Efficiency:")
        print(f"  Learned Patterns: {efficiency['learned_pattern_rate']}%")
        print(f"  AI Generated: {efficiency['ai_generation_rate']}%")
        
        # Performance Metrics
        print("\n⚡ PERFORMANCE METRICS")
        print("-" * 40)
        perf_analysis = self.analyze_performance_metrics()
        print(f"Overall Success Rate: {perf_analysis['overall_success_rate']}%")
        
        if 'time_analysis' in perf_analysis and perf_analysis['time_analysis']:
            time_info = perf_analysis['time_analysis']
            print(f"Date Range: {time_info.get('start', 'N/A')} to {time_info.get('end', 'N/A')}")
            print(f"Queries per Day: {time_info.get('queries_per_day', 'N/A')}")
        
        if 'data_quality' in perf_analysis and perf_analysis['data_quality']:
            data_info = perf_analysis['data_quality']
            print(f"Avg Records Returned: {data_info.get('avg_records_returned', 'N/A')}")
            print(f"Empty Result Rate: {data_info.get('empty_result_rate', 'N/A')}%")
        
        # Failure Analysis
        print("\n❌ FAILURE ANALYSIS")
        print("-" * 40)
        failure_analysis = self.identify_failure_patterns()
        print(f"Total Failures: {failure_analysis['total_failures']}")
        print(f"Failure Rate: {failure_analysis['failure_rate']}%")
        
        print("Error Categories:")
        for error, count in failure_analysis['error_categories'].items():
            print(f"  {error}: {count}")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS")
        print("-" * 40)
        recommendations = self.generate_recommendations()
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        if export_csv:
            print("\n📊 EXPORTING DATA")
            print("-" * 40)
            self.export_csv()
        
        print("\n" + "="*60)
        print("✅ Analysis Complete")
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description='Analyze production traces.jsonl')
    parser.add_argument('--data-dir', default='ref_data', help='Data directory path')
    parser.add_argument('--export-csv', action='store_true', help='Export to CSV')
    
    args = parser.parse_args()
    
    analyzer = TracesAnalyzer(args.data_dir)
    analyzer.run_analysis(export_csv=args.export_csv)

if __name__ == "__main__":
    main()