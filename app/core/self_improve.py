"""Self-improvement loop: learns from production metrics to optimize intent classification"""
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

class SelfImprover:
    def __init__(self, metrics_path: str = "data/production_metrics.json"):
        self.metrics_path = Path(metrics_path)
        self.improvements_path = Path("data/improvements.json")
        
    def analyze_failures(self) -> dict:
        """Analyze failed queries to identify patterns"""
        if not self.metrics_path.exists():
            return {"error": "No metrics found"}
        
        with open(self.metrics_path) as f:
            metrics = json.load(f)
        
        # Extract failed queries
        failures = [q for q in metrics.get("query_history", []) if not q["success"]]
        
        # Group by intent
        by_intent = defaultdict(list)
        for f in failures:
            by_intent[f["intent"]].append(f)
        
        # Extract keywords from failed queries
        keyword_suggestions = defaultdict(set)
        for intent, queries in by_intent.items():
            for q in queries:
                words = q["query"].lower().split()
                # Extract potential keywords (nouns, verbs)
                for word in words:
                    if len(word) > 3 and word not in ["what", "which", "have", "been", "that", "with", "from", "this"]:
                        keyword_suggestions[intent].add(word)
        
        return {
            "total_failures": len(failures),
            "by_intent": {k: len(v) for k, v in by_intent.items()},
            "failed_queries": failures,
            "keyword_suggestions": {k: list(v) for k, v in keyword_suggestions.items()}
        }
    
    def generate_recommendations(self) -> dict:
        """Generate actionable recommendations based on analysis"""
        analysis = self.analyze_failures()
        
        if "error" in analysis:
            return analysis
        
        recommendations = {
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis,
            "actions": []
        }
        
        # Recommendation 1: Fix unknown intent classification
        unknown_failures = analysis["by_intent"].get("unknown", 0)
        if unknown_failures > 0:
            unknown_keywords = analysis["keyword_suggestions"].get("unknown", [])
            recommendations["actions"].append({
                "priority": "HIGH",
                "type": "intent_classification",
                "issue": f"{unknown_failures} queries failed with 'unknown' intent",
                "solution": "Add keywords to classify_question_intent()",
                "suggested_keywords": unknown_keywords[:10],
                "code_location": "app/core/bedrock_client.py:classify_question_intent()"
            })
        
        # Recommendation 2: Improve prompt for specific intents
        for intent, count in analysis["by_intent"].items():
            if intent != "unknown" and count > 0:
                recommendations["actions"].append({
                    "priority": "MEDIUM",
                    "type": "prompt_tuning",
                    "issue": f"{count} queries failed with '{intent}' intent",
                    "solution": f"Review and enhance {intent} prompt profile",
                    "code_location": "app/core/prompts.py:PROMPT_PROFILES"
                })
        
        # Save recommendations
        self.improvements_path.parent.mkdir(exist_ok=True)
        with open(self.improvements_path, 'w') as f:
            json.dump(recommendations, f, indent=2)
        
        return recommendations
    
    def apply_keyword_improvements(self, keywords: list[str], target_intent: str) -> str:
        """Generate code snippet to add keywords to intent classifier"""
        keyword_str = ", ".join([f'"{k}"' for k in keywords])
        
        code = f"""
# Add to classify_question_intent() in app/core/bedrock_client.py
# For {target_intent} intent, add these keywords:

if any(kw in q_lower for kw in [{keyword_str}]):
    return "{target_intent}"
"""
        return code.strip()

def main():
    """Run self-improvement analysis"""
    improver = SelfImprover()
    
    print("=" * 70)
    print("SELF-IMPROVEMENT ANALYSIS")
    print("=" * 70)
    
    # Analyze failures
    recommendations = improver.generate_recommendations()
    
    if "error" in recommendations:
        print(f"\nError: {recommendations['error']}")
        return
    
    # Print summary
    print(f"\nTotal Failures: {recommendations['analysis']['total_failures']}")
    print(f"\nFailures by Intent:")
    for intent, count in recommendations['analysis']['by_intent'].items():
        print(f"  {intent}: {count}")
    
    # Print recommendations
    print(f"\n{'=' * 70}")
    print("RECOMMENDATIONS")
    print("=" * 70)
    
    for i, action in enumerate(recommendations['actions'], 1):
        print(f"\n[{action['priority']}] Action {i}: {action['type']}")
        print(f"  Issue: {action['issue']}")
        print(f"  Solution: {action['solution']}")
        print(f"  Location: {action['code_location']}")
        
        if "suggested_keywords" in action:
            print(f"  Keywords: {', '.join(action['suggested_keywords'][:5])}")
            
            # Generate code snippet
            code = improver.apply_keyword_improvements(
                action['suggested_keywords'][:5],
                "strict_v1"  # Default fallback
            )
            print(f"\n  Code to add:")
            for line in code.split('\n'):
                print(f"    {line}")
    
    print(f"\n{'=' * 70}")
    print(f"Recommendations saved to: {improver.improvements_path}")
    print("=" * 70)

if __name__ == "__main__":
    main()
