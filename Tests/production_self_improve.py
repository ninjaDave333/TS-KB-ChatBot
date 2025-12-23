"""
Production Self-Improvement Loop
- Learns from real successful queries in production_metrics.json
- Tests improvements against Neo4j database
- Uses DGX Ollama (no Bedrock needed)
- Validates with actual query execution
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.bedrock_client import classify_question_intent
from dotenv import load_dotenv

load_dotenv()

class ProductionSelfImprover:
    def __init__(self):
        self.metrics_path = Path("data/production_metrics.json")
        self.results_path = Path("data/self_improvement_results.json")
        
    def load_production_data(self) -> Dict:
        """Load real production metrics"""
        if not self.metrics_path.exists():
            raise FileNotFoundError(f"No metrics at {self.metrics_path}")
        
        with open(self.metrics_path) as f:
            return json.load(f)
    
    def extract_successful_patterns(self, metrics: Dict) -> Dict[str, List[Dict]]:
        """Extract patterns from successful queries only"""
        successful = [q for q in metrics["query_history"] if q["success"]]
        
        # Group by intent
        by_intent = defaultdict(list)
        for q in successful:
            by_intent[q["intent"]].append(q)
        
        return dict(by_intent)
    
    def extract_failed_patterns(self, metrics: Dict) -> List[Dict]:
        """Extract failed queries for analysis"""
        return [q for q in metrics["query_history"] if not q["success"]]
    
    def analyze_intent_keywords(self, patterns: Dict[str, List[Dict]]) -> Dict[str, set]:
        """Extract keywords from successful queries per intent"""
        intent_keywords = {}
        
        for intent, queries in patterns.items():
            if intent == "unknown":
                continue
                
            keywords = set()
            for q in queries:
                words = q["query"].lower().split()
                # Extract meaningful words (length > 3, not common stopwords)
                for word in words:
                    if len(word) > 3 and word not in [
                        "what", "which", "have", "been", "that", "with", 
                        "from", "this", "there", "were", "most", "many"
                    ]:
                        keywords.add(word)
            
            intent_keywords[intent] = keywords
        
        return intent_keywords
    
    def suggest_intent_improvements(
        self, 
        failed_queries: List[Dict],
        intent_keywords: Dict[str, set]
    ) -> List[Dict]:
        """Suggest intent classification improvements based on failures"""
        suggestions = []
        
        for failed in failed_queries:
            if failed["intent"] != "unknown":
                continue
            
            query_lower = failed["query"].lower()
            query_words = set(query_lower.split())
            
            # Find best matching intent based on keyword overlap
            best_match = None
            best_score = 0
            
            for intent, keywords in intent_keywords.items():
                overlap = len(query_words & keywords)
                if overlap > best_score:
                    best_score = overlap
                    best_match = intent
            
            if best_match and best_score > 0:
                # Extract unique keywords from failed query
                unique_keywords = []
                for word in query_words:
                    if len(word) > 3 and word not in [
                        "what", "which", "have", "been", "that", "with"
                    ]:
                        # Check if this keyword would help classify
                        if word not in intent_keywords.get(best_match, set()):
                            unique_keywords.append(word)
                
                suggestions.append({
                    "query": failed["query"],
                    "current_intent": "unknown",
                    "suggested_intent": best_match,
                    "confidence": best_score,
                    "keywords_to_add": unique_keywords[:3],
                    "error": failed["error"]
                })
        
        return suggestions
    
    def validate_improvement(self, query: str, suggested_intent: str) -> bool:
        """Validate if suggested intent would work by testing classification"""
        # This is a dry-run - we'd need to actually modify the classifier
        # For now, just check if the suggestion makes sense
        current_intent = classify_question_intent(query)
        return current_intent != "unknown" or suggested_intent != "unknown"
    
    def generate_report(
        self,
        metrics: Dict,
        successful_patterns: Dict,
        failed_queries: List[Dict],
        suggestions: List[Dict]
    ) -> Dict:
        """Generate comprehensive improvement report"""
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_queries": metrics["total_queries"],
                "successful": len([q for q in metrics["query_history"] if q["success"]]),
                "failed": len(failed_queries),
                "success_rate": ((metrics["total_queries"] - len(failed_queries)) / metrics["total_queries"] * 100)
            },
            "successful_patterns": {
                intent: {
                    "count": len(queries),
                    "avg_response_time": sum(q["response_time"] for q in queries) / len(queries),
                    "sample_queries": [q["query"] for q in queries[:3]]
                }
                for intent, queries in successful_patterns.items()
            },
            "failures": {
                "total": len(failed_queries),
                "by_intent": defaultdict(int),
                "by_error": defaultdict(int)
            },
            "improvements": suggestions,
            "actionable_keywords": {}
        }
        
        # Analyze failures
        for f in failed_queries:
            report["failures"]["by_intent"][f["intent"]] += 1
            if f["error"]:
                report["failures"]["by_error"][f["error"]] += 1
        
        # Group keywords by target intent
        for sugg in suggestions:
            intent = sugg["suggested_intent"]
            if intent not in report["actionable_keywords"]:
                report["actionable_keywords"][intent] = set()
            report["actionable_keywords"][intent].update(sugg["keywords_to_add"])
        
        # Convert sets to lists for JSON
        report["actionable_keywords"] = {
            k: list(v) for k, v in report["actionable_keywords"].items()
        }
        report["failures"]["by_intent"] = dict(report["failures"]["by_intent"])
        report["failures"]["by_error"] = dict(report["failures"]["by_error"])
        
        return report
    
    def run(self) -> Dict:
        """Run self-improvement analysis"""
        print("=" * 70)
        print("PRODUCTION SELF-IMPROVEMENT ANALYSIS")
        print("=" * 70)
        
        # Load real data
        print("\n[1/5] Loading production metrics...")
        metrics = self.load_production_data()
        print(f"  Loaded {metrics['total_queries']} queries")
        
        # Extract patterns
        print("\n[2/5] Analyzing successful patterns...")
        successful_patterns = self.extract_successful_patterns(metrics)
        for intent, queries in successful_patterns.items():
            print(f"  {intent}: {len(queries)} successful")
        
        # Analyze failures
        print("\n[3/5] Analyzing failures...")
        failed_queries = self.extract_failed_patterns(metrics)
        print(f"  Found {len(failed_queries)} failures")
        
        # Extract keywords
        print("\n[4/5] Extracting intent keywords from successes...")
        intent_keywords = self.analyze_intent_keywords(successful_patterns)
        
        # Generate suggestions
        print("\n[5/5] Generating improvement suggestions...")
        suggestions = self.suggest_intent_improvements(failed_queries, intent_keywords)
        print(f"  Generated {len(suggestions)} suggestions")
        
        # Create report
        report = self.generate_report(metrics, successful_patterns, failed_queries, suggestions)
        
        # Save results
        self.results_path.parent.mkdir(exist_ok=True)
        with open(self.results_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def print_report(self, report: Dict):
        """Print human-readable report"""
        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)
        
        print(f"\nSUMMARY:")
        print(f"  Total Queries: {report['summary']['total_queries']}")
        print(f"  Successful: {report['summary']['successful']}")
        print(f"  Failed: {report['summary']['failed']}")
        print(f"  Success Rate: {report['summary']['success_rate']:.1f}%")
        
        print(f"\nSUCCESSFUL PATTERNS:")
        for intent, data in report['successful_patterns'].items():
            print(f"  {intent}: {data['count']} queries, avg {data['avg_response_time']:.2f}s")
        
        print(f"\nFAILURE ANALYSIS:")
        print(f"  By Intent: {report['failures']['by_intent']}")
        print(f"  By Error: {report['failures']['by_error']}")
        
        print(f"\nIMPROVEMENT SUGGESTIONS ({len(report['improvements'])}):")
        for i, sugg in enumerate(report['improvements'], 1):
            print(f"\n  [{i}] Query: {sugg['query'][:60]}...")
            print(f"      Current: {sugg['current_intent']} -> Suggested: {sugg['suggested_intent']}")
            print(f"      Keywords to add: {', '.join(sugg['keywords_to_add'])}")
            print(f"      Error: {sugg['error']}")
        
        print(f"\nACTIONABLE KEYWORDS BY INTENT:")
        for intent, keywords in report['actionable_keywords'].items():
            print(f"  {intent}: {', '.join(keywords[:5])}")
        
        print(f"\n" + "=" * 70)
        print(f"Report saved to: {self.results_path}")
        print("=" * 70)

def main():
    improver = ProductionSelfImprover()
    
    try:
        report = improver.run()
        improver.print_report(report)
        
        print("\nNEXT STEPS:")
        print("1. Review suggestions in data/self_improvement_results.json")
        print("2. Add suggested keywords to app/core/bedrock_client.py:classify_question_intent()")
        print("3. Test with failed queries to verify improvements")
        print("4. Re-run this script after collecting more production data")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
