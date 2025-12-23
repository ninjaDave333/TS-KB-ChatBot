"""
Offline Intent Classification Tuner
- Uses DGX Ollama for intent classification
- Learns from production successful queries
- Tests improvements on failed queries
- NO app modifications - only generates recommendations
- Fully offline - no Bedrock, no external APIs
"""
import json
import requests
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict

class OfflineIntentTuner:
    def __init__(self):
        self.metrics_path = Path("data/production_metrics.json")
        self.output_path = Path("data/intent_tuning_recommendations.json")
        self.ollama_url = "http://172.16.10.250:11434"
        self.model = "llama3.2:3b"
        
    def check_ollama(self) -> bool:
        """Verify Ollama is accessible"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def load_production_data(self) -> Dict:
        """Load production metrics"""
        with open(self.metrics_path) as f:
            return json.load(f)
    
    def extract_training_data(self, metrics: Dict) -> Dict[str, List[str]]:
        """Extract successful queries grouped by intent"""
        training = defaultdict(list)
        
        for q in metrics["query_history"]:
            if q["success"] and q["intent"] != "unknown":
                training[q["intent"]].append(q["query"])
        
        return dict(training)
    
    def classify_with_ollama(self, query: str, training_examples: Dict[str, List[str]]) -> Tuple[str, float]:
        """Use Ollama to classify query intent based on training examples"""
        
        # Build prompt with examples
        prompt = f"""You are an intent classifier for a Neo4j database query system.

Available intents and their examples:

SALES_V1 - Deal/opportunity/revenue queries:
{chr(10).join(f"- {ex}" for ex in training_examples.get('sales_v1', [])[:3])}

CALENDAR_V1 - Meeting/recording/event queries:
{chr(10).join(f"- {ex}" for ex in training_examples.get('calendar_v1', [])[:3])}

PRODUCT_V1 - Product/vendor/solution queries:
{chr(10).join(f"- {ex}" for ex in training_examples.get('product_v1', [])[:3])}

STRICT_V1 - General/organizational queries:
{chr(10).join(f"- {ex}" for ex in training_examples.get('strict_v1', [])[:3])}

Classify this query: "{query}"

Respond with ONLY the intent name (sales_v1, calendar_v1, product_v1, or strict_v1) and confidence (0-100).
Format: INTENT_NAME CONFIDENCE
Example: calendar_v1 85"""

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json().get("response", "").strip().lower()
                
                # Parse response
                parts = result.split()
                if len(parts) >= 2:
                    intent = parts[0]
                    try:
                        confidence = float(parts[1]) / 100.0
                    except:
                        confidence = 0.5
                    
                    return intent, confidence
                
            return "unknown", 0.0
            
        except Exception as e:
            print(f"    Ollama error: {e}")
            return "unknown", 0.0
    
    def extract_keywords_from_query(self, query: str) -> List[str]:
        """Extract meaningful keywords from query"""
        stopwords = {
            "what", "which", "have", "been", "that", "with", "from", 
            "this", "there", "were", "most", "many", "how", "the", "are"
        }
        
        words = query.lower().split()
        keywords = []
        
        for word in words:
            # Clean word
            word = word.strip("?,.'\"")
            # Keep if meaningful
            if len(word) > 3 and word not in stopwords:
                keywords.append(word)
        
        return keywords[:5]  # Top 5 keywords
    
    def test_failed_queries(
        self, 
        failed_queries: List[Dict],
        training_examples: Dict[str, List[str]]
    ) -> List[Dict]:
        """Test Ollama classification on failed queries"""
        
        results = []
        
        for i, failed in enumerate(failed_queries, 1):
            print(f"\n  [{i}/{len(failed_queries)}] Testing: {failed['query'][:50]}...")
            
            # Classify with Ollama
            suggested_intent, confidence = self.classify_with_ollama(
                failed["query"],
                training_examples
            )
            
            # Extract keywords
            keywords = self.extract_keywords_from_query(failed["query"])
            
            print(f"    Current: {failed['intent']} -> Suggested: {suggested_intent} (confidence: {confidence:.0%})")
            
            results.append({
                "query": failed["query"],
                "current_intent": failed["intent"],
                "suggested_intent": suggested_intent,
                "confidence": confidence,
                "keywords": keywords,
                "error": failed["error"],
                "improved": suggested_intent != "unknown" and suggested_intent != failed["intent"]
            })
            
            time.sleep(1)  # Rate limit
        
        return results
    
    def test_successful_queries(
        self,
        successful_queries: List[Dict],
        training_examples: Dict[str, List[str]]
    ) -> List[Dict]:
        """Test Ollama on successful queries to check for regressions"""
        
        results = []
        sample_size = min(10, len(successful_queries))
        sample = successful_queries[:sample_size]
        
        for i, success in enumerate(sample, 1):
            print(f"\n  [{i}/{sample_size}] Testing: {success['query'][:50]}...")
            
            # Classify with Ollama
            suggested_intent, confidence = self.classify_with_ollama(
                success["query"],
                training_examples
            )
            
            matches = suggested_intent == success["intent"]
            print(f"    Expected: {success['intent']} -> Got: {suggested_intent} ({'MATCH' if matches else 'MISMATCH'})")
            
            results.append({
                "query": success["query"],
                "expected_intent": success["intent"],
                "suggested_intent": suggested_intent,
                "confidence": confidence,
                "matches": matches
            })
            
            time.sleep(1)
        
        return results
    
    def generate_keyword_recommendations(
        self,
        failed_results: List[Dict],
        training_examples: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """Generate keyword recommendations per intent"""
        
        recommendations = defaultdict(set)
        
        for result in failed_results:
            if result["improved"]:
                intent = result["suggested_intent"]
                # Add keywords that would help classify this query
                for kw in result["keywords"]:
                    recommendations[intent].add(kw)
        
        return {k: list(v) for k, v in recommendations.items()}
    
    def generate_code_changes(self, keyword_recommendations: Dict[str, List[str]]) -> str:
        """Generate code snippet for manual application"""
        
        code = """# Recommended changes to app/core/bedrock_client.py:classify_question_intent()
# Add these keywords to improve intent classification

def classify_question_intent(question: str) -> str:
    q_lower = question.lower()
    
"""
        
        for intent, keywords in keyword_recommendations.items():
            if keywords:
                kw_str = ", ".join([f'"{kw}"' for kw in keywords[:5]])
                code += f"""    # Enhanced {intent} classification
    if any(kw in q_lower for kw in [{kw_str}]):
        return "{intent}"
    
"""
        
        code += """    # ... rest of existing logic
    return "strict_v1"  # default fallback
"""
        
        return code
    
    def run(self):
        """Run offline intent tuning"""
        print("=" * 70)
        print("OFFLINE INTENT CLASSIFICATION TUNER")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Check Ollama
        print("\n[1/6] Checking Ollama connection...")
        if not self.check_ollama():
            print("  ERROR: Cannot connect to DGX Ollama")
            print(f"  URL: {self.ollama_url}")
            return None
        print(f"  Connected to {self.ollama_url}")
        print(f"  Model: {self.model}")
        
        # Load data
        print("\n[2/6] Loading production metrics...")
        metrics = self.load_production_data()
        print(f"  Loaded {metrics['total_queries']} queries")
        
        # Extract training data
        print("\n[3/6] Extracting training examples from successful queries...")
        training_examples = self.extract_training_data(metrics)
        for intent, examples in training_examples.items():
            print(f"  {intent}: {len(examples)} examples")
        
        # Test failed queries
        print("\n[4/6] Testing Ollama classification on failed queries...")
        failed_queries = [q for q in metrics["query_history"] if not q["success"]]
        failed_results = self.test_failed_queries(failed_queries, training_examples)
        
        # Test successful queries (regression check)
        print("\n[5/6] Regression testing on successful queries...")
        successful_queries = [q for q in metrics["query_history"] if q["success"]]
        regression_results = self.test_successful_queries(successful_queries, training_examples)
        
        # Generate recommendations
        print("\n[6/6] Generating recommendations...")
        keyword_recommendations = self.generate_keyword_recommendations(
            failed_results,
            training_examples
        )
        
        code_changes = self.generate_code_changes(keyword_recommendations)
        
        # Compile report
        report = {
            "timestamp": datetime.now().isoformat(),
            "configuration": {
                "ollama_url": self.ollama_url,
                "model": self.model,
                "metrics_file": str(self.metrics_path)
            },
            "summary": {
                "total_failed": len(failed_results),
                "improved": sum(1 for r in failed_results if r["improved"]),
                "still_unknown": sum(1 for r in failed_results if r["suggested_intent"] == "unknown"),
                "improvement_rate": (sum(1 for r in failed_results if r["improved"]) / len(failed_results) * 100) if failed_results else 0,
                "regression_tested": len(regression_results),
                "regression_matches": sum(1 for r in regression_results if r["matches"]),
                "regression_rate": (sum(1 for r in regression_results if not r["matches"]) / len(regression_results) * 100) if regression_results else 0
            },
            "failed_query_results": failed_results,
            "regression_results": regression_results,
            "keyword_recommendations": keyword_recommendations,
            "code_changes": code_changes
        }
        
        # Save report
        self.output_path.parent.mkdir(exist_ok=True)
        with open(self.output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        self.print_summary(report)
        
        return report
    
    def print_summary(self, report: Dict):
        """Print human-readable summary"""
        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)
        
        print(f"\nFAILED QUERY ANALYSIS:")
        print(f"  Total Failed: {report['summary']['total_failed']}")
        print(f"  Improved: {report['summary']['improved']}")
        print(f"  Still Unknown: {report['summary']['still_unknown']}")
        print(f"  Improvement Rate: {report['summary']['improvement_rate']:.1f}%")
        
        print(f"\nREGRESSION TEST:")
        print(f"  Tested: {report['summary']['regression_tested']}")
        print(f"  Matches: {report['summary']['regression_matches']}")
        print(f"  Regression Rate: {report['summary']['regression_rate']:.1f}%")
        
        print(f"\nKEYWORD RECOMMENDATIONS:")
        for intent, keywords in report['keyword_recommendations'].items():
            print(f"  {intent}: {', '.join(keywords[:5])}")
        
        print(f"\nCODE CHANGES:")
        print(report['code_changes'])
        
        print(f"\n" + "=" * 70)
        print(f"Full report saved to: {self.output_path}")
        print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        print(f"\nNEXT STEPS:")
        print(f"1. Review recommendations in {self.output_path}")
        print(f"2. If improvement rate > 50% and regression rate < 10%:")
        print(f"   - Apply code changes to app/core/bedrock_client.py")
        print(f"   - Test manually with failed queries")
        print(f"   - Deploy to production")
        print(f"3. If results unsatisfactory:")
        print(f"   - Collect more production data")
        print(f"   - Re-run this script")

def main():
    tuner = OfflineIntentTuner()
    
    try:
        report = tuner.run()
        
        if report:
            # Success criteria
            if (report['summary']['improvement_rate'] > 50 and 
                report['summary']['regression_rate'] < 10):
                print("\n✓ SUCCESS: Recommendations ready for manual review!")
                return 0
            else:
                print("\n⚠ WARNING: Review results carefully before applying")
                return 1
        else:
            print("\n✗ FAILED: Could not complete tuning")
            return 1
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
