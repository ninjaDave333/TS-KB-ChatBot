"""
Manual self-learning analysis tool.
Run: python -m Tests.run_self_learning
"""
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.self_learner import generate_report, save_report

def main():
    print("🧠 Running Self-Learning Analysis...\n")
    
    # Generate report
    report = generate_report()
    
    # Display summary
    print("=" * 60)
    print("FAILURE ANALYSIS")
    print("=" * 60)
    fa = report['failure_analysis']
    print(f"Total Queries: {fa['total_queries']}")
    print(f"Total Failures: {fa['total_failures']} ({fa['failure_rate']}%)")
    print(f"Validation Retries: {fa['retry_count']}")
    print(f"\nError Breakdown:")
    for error_type, count in fa['error_breakdown'].items():
        print(f"  - {error_type}: {count}")
    
    print("\n" + "=" * 60)
    print("USER FEEDBACK ANALYSIS")
    print("=" * 60)
    fb = report['feedback_analysis']
    if 'error' in fb:
        print(f"⚠️  {fb['error']}")
    else:
        print(f"Total Feedback: {fb['total_feedback']}")
        print(f"Perfect (Helpful): {fb['helpful_count']} ({fb['satisfaction_rate']}%)")
        print(f"Partial (Almost): {fb['almost_count']} ({fb['partial_success_rate']}%)")
        print(f"Failed (Not Helpful): {fb['not_helpful_count']}")
        if fb['almost_by_intent']:
            print(f"\nAlmost by Intent:")
            for intent, count in fb['almost_by_intent'].items():
                print(f"  - {intent}: {count}")
        if fb['not_helpful_by_intent']:
            print(f"\nNot Helpful by Intent:")
            for intent, count in fb['not_helpful_by_intent'].items():
                print(f"  - {intent}: {count}")
    
    print("\n" + "=" * 60)
    print("INTENT CLASSIFICATION ANALYSIS")
    print("=" * 60)
    ia = report['intent_analysis']
    print(f"Unknown Intent Rate: {ia['unknown_rate']}%")
    print(f"Most Common Intent: {ia['most_common']}")
    print(f"\nIntent Distribution:")
    for intent, count in ia['intent_distribution'].items():
        print(f"  - {intent}: {count}")
    
    print("\n" + "=" * 60)
    print("SUGGESTIONS")
    print("=" * 60)
    sugg = report['suggestions']
    
    has_suggestions = False
    
    if sugg['prompt_rules']:
        has_suggestions = True
        print("\n📝 Prompt Rules:")
        for s in sugg['prompt_rules']:
            print(f"  • {s}")
    
    if sugg['intent_keywords']:
        has_suggestions = True
        print("\n🎯 Intent Keywords:")
        for s in sugg['intent_keywords']:
            print(f"  • {s}")
    
    if sugg['schema_hints']:
        has_suggestions = True
        print("\n📊 Schema Hints:")
        for s in sugg['schema_hints']:
            print(f"  • {s}")
    
    if sugg['few_shot_examples']:
        has_suggestions = True
        print("\n💡 Few-Shot Examples:")
        for s in sugg['few_shot_examples']:
            print(f"  • {s}")
    
    if not has_suggestions:
        print("\n✅ No improvements needed - system performing well!")
    
    # Save full report
    output_file = save_report()
    print(f"\n📄 Full report saved to: {output_file}")
    print("\n🔍 DETAILED ERROR QUERIES:")
    
    # Show actual failed queries
    if fa['error_details']:
        for error_type, queries in fa['error_details'].items():
            print(f"\n  {error_type}:")
            for q in queries:
                print(f"    - [{q['intent']}] {q['query'][:100]}...")
    
    print("\n🔍 PARTIAL SUCCESS QUERIES (Almost):")
    if 'almost_queries' in fb and fb['almost_queries']:
        for intent, queries in fb['almost_queries'].items():
            print(f"\n  {intent}:")
            for q in queries[:3]:  # Show first 3
                print(f"    - {q[:100]}...")
    else:
        print("  None found")
    
    print("\n🔍 FAILED QUERIES (Not Helpful):")
    if 'not_helpful_queries' in fb and fb['not_helpful_queries']:
        for intent, queries in fb['not_helpful_queries'].items():
            print(f"\n  {intent}:")
            for q in queries[:3]:  # Show first 3
                print(f"    - {q[:100]}...")
    else:
        print("  None found")

if __name__ == "__main__":
    main()
