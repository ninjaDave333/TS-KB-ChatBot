"""
Production Pattern Analysis - Extract learning insights from real user interactions
"""

import re
from collections import defaultdict, Counter
from datetime import datetime
import json

class ProductionPatternAnalyzer:
    """Analyze production logs to extract learning patterns"""
    
    def __init__(self):
        self.query_patterns = []
        self.performance_data = []
        self.user_sessions = defaultdict(list)
        self.refinement_chains = []
    
    def parse_log_entry(self, log_text: str):
        """Parse a single log entry to extract query information"""
        lines = log_text.strip().split('\n')
        
        queries = []
        for line in lines:
            # Extract query attempts
            if "Attempting AI generation for:" in line:
                query = line.split("Attempting AI generation for: ")[1]
                queries.append(query)
            
            # Extract performance data
            if "Method:" in line and "Time:" in line:
                parts = line.split(" | ")
                method = parts[0].split("Method: ")[1] if "Method: " in parts[0] else "unknown"
                data_count = int(parts[1].split("Data: ")[1].split(" items")[0]) if "Data: " in parts[1] else 0
                time_str = parts[2].split("Time: ")[1].replace("s", "") if "Time: " in parts[2] else "0"
                execution_time = float(time_str)
                
                if queries:
                    self.performance_data.append({
                        'query': queries[-1],
                        'method': method,
                        'data_count': data_count,
                        'execution_time': execution_time
                    })
        
        return queries
    
    def analyze_query_refinement_chains(self, queries):
        """Identify query refinement patterns"""
        # Look for similar queries that build on each other
        for i in range(len(queries) - 1):
            current = queries[i].lower()
            next_query = queries[i + 1].lower()
            
            # Check if next query is a refinement of current
            if self._is_refinement(current, next_query):
                self.refinement_chains.append({
                    'original': queries[i],
                    'refined': queries[i + 1],
                    'refinement_type': self._classify_refinement(current, next_query)
                })
    
    def _is_refinement(self, query1: str, query2: str) -> bool:
        """Check if query2 is a refinement of query1"""
        # Simple heuristic: if query2 contains most words from query1 plus additional filters
        words1 = set(query1.split())
        words2 = set(query2.split())
        
        # At least 60% word overlap and query2 is longer
        overlap = len(words1.intersection(words2)) / len(words1) if words1 else 0
        return overlap > 0.6 and len(query2) > len(query1)
    
    def _classify_refinement(self, query1: str, query2: str) -> str:
        """Classify the type of refinement"""
        if "not unknown" in query2 and "not unknown" not in query1:
            return "data_quality_filter"
        elif any(word in query2 for word in ["and", "where", "with"]) and len(query2) > len(query1):
            return "additional_filter"
        elif any(word in query2 for word in ["top", "limit", "first"]) and not any(word in query1 for word in ["top", "limit", "first"]):
            return "result_limiting"
        else:
            return "general_refinement"
    
    def extract_common_patterns(self):
        """Extract common query patterns from the data"""
        patterns = {
            'teams_recording': [],
            'israeli_clients': [],
            'temporal_business': [],
            'data_quality_filters': []
        }
        
        for perf in self.performance_data:
            query = perf['query'].lower()
            
            if any(term in query for term in ['meeting', 'recording', 'external', 'internal']):
                patterns['teams_recording'].append(perf)
            elif 'israeli' in query or 'israel' in query:
                patterns['israeli_clients'].append(perf)
            elif any(term in query for term in ['2025', '2024', 'year']):
                patterns['temporal_business'].append(perf)
            elif 'unknown' in query:
                patterns['data_quality_filters'].append(perf)
        
        return patterns
    
    def generate_insights(self):
        """Generate actionable insights from the analysis"""
        patterns = self.extract_common_patterns()
        
        insights = {
            'query_volume_by_type': {k: len(v) for k, v in patterns.items()},
            'average_performance': {},
            'refinement_patterns': Counter([r['refinement_type'] for r in self.refinement_chains]),
            'data_quality_issues': [],
            'user_behavior_insights': [],
            'recommendations': []
        }
        
        # Calculate average performance by pattern type
        for pattern_type, queries in patterns.items():
            if queries:
                avg_time = sum(q['execution_time'] for q in queries) / len(queries)
                avg_data = sum(q['data_count'] for q in queries) / len(queries)
                insights['average_performance'][pattern_type] = {
                    'avg_execution_time': round(avg_time, 2),
                    'avg_data_count': round(avg_data, 1)
                }
        
        # Identify data quality issues
        unknown_queries = [q for q in self.performance_data if 'unknown' in q['query'].lower()]
        if unknown_queries:
            insights['data_quality_issues'].append({
                'issue': 'Unknown manager filtering',
                'frequency': len(unknown_queries),
                'impact': 'Users repeatedly trying to filter out Unknown values'
            })
        
        # User behavior insights
        if self.refinement_chains:
            insights['user_behavior_insights'].append({
                'pattern': 'Iterative query refinement',
                'frequency': len(self.refinement_chains),
                'description': 'Users refine queries based on initial results'
            })
        
        # Generate recommendations
        if patterns['data_quality_filters']:
            insights['recommendations'].append(
                "Implement automatic 'Unknown' filtering for manager queries"
            )
        
        if patterns['teams_recording']:
            insights['recommendations'].append(
                "Create specialized Teams Recording query templates"
            )
        
        return insights

def analyze_sample_logs():
    """Analyze the sample logs provided"""
    
    sample_queries = [
        "How many external meetings recorded?",
        "How many internal meetings recorded?", 
        "How many total meetings recorded?",
        "List 10 Israeli clients with managers",
        "List Israeli clients with managers that is not Unknown",
        "List Israeli clients with managers that is not Unknown and not managed by Unknown",
        "who are the top 10 most active clients in 2025 ?"
    ]
    
    sample_performance = [
        {'query': sample_queries[0], 'method': 'ai_generated', 'data_count': 1, 'execution_time': 1.53},
        {'query': sample_queries[1], 'method': 'ai_generated', 'data_count': 1, 'execution_time': 1.29},
        {'query': sample_queries[2], 'method': 'ai_generated', 'data_count': 1, 'execution_time': 1.97},
        {'query': sample_queries[3], 'method': 'ai_generated', 'data_count': 10, 'execution_time': 3.27},
        {'query': sample_queries[4], 'method': 'ai_generated', 'data_count': 30, 'execution_time': 1.64},
        {'query': sample_queries[5], 'method': 'ai_generated', 'data_count': 30, 'execution_time': 1.73},
        {'query': sample_queries[6], 'method': 'ai_generated', 'data_count': 10, 'execution_time': 1.64}
    ]
    
    analyzer = ProductionPatternAnalyzer()
    analyzer.performance_data = sample_performance
    analyzer.analyze_query_refinement_chains(sample_queries)
    
    insights = analyzer.generate_insights()
    
    print("=== Production Pattern Analysis ===")
    print(f"Total queries analyzed: {len(sample_queries)}")
    print(f"Query refinement chains detected: {len(analyzer.refinement_chains)}")
    
    print("\n=== Query Volume by Type ===")
    for pattern_type, count in insights['query_volume_by_type'].items():
        print(f"  {pattern_type}: {count} queries")
    
    print("\n=== Average Performance ===")
    for pattern_type, perf in insights['average_performance'].items():
        print(f"  {pattern_type}:")
        print(f"    Avg execution time: {perf['avg_execution_time']}s")
        print(f"    Avg data count: {perf['avg_data_count']}")
    
    print("\n=== Refinement Patterns ===")
    for refinement_type, count in insights['refinement_patterns'].items():
        print(f"  {refinement_type}: {count} occurrences")
    
    print("\n=== Data Quality Issues ===")
    for issue in insights['data_quality_issues']:
        print(f"  - {issue['issue']}: {issue['frequency']} queries affected")
        print(f"    Impact: {issue['impact']}")
    
    print("\n=== User Behavior Insights ===")
    for insight in insights['user_behavior_insights']:
        print(f"  - {insight['pattern']}: {insight['frequency']} occurrences")
        print(f"    Description: {insight['description']}")
    
    print("\n=== Recommendations ===")
    for i, rec in enumerate(insights['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    print("\n=== Detected Refinement Chains ===")
    for i, chain in enumerate(analyzer.refinement_chains, 1):
        print(f"  Chain {i} ({chain['refinement_type']}):")
        print(f"    Original: {chain['original']}")
        print(f"    Refined:  {chain['refined']}")
    
    return insights

if __name__ == "__main__":
    insights = analyze_sample_logs()
    
    # Save insights for Dynamic RAG system
    with open('data/production_insights.json', 'w') as f:
        json.dump(insights, f, indent=2)
    
    print(f"\n=== Insights saved to data/production_insights.json ===")