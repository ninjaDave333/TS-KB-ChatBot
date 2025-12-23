"""Quick verification of metrics collection after manual query run"""
import json
import os
from pathlib import Path

def verify_metrics():
    metrics_path = Path("../data/production_metrics.json")
    
    if not metrics_path.exists():
        print("❌ Metrics file not found at:", metrics_path.absolute())
        return
    
    with open(metrics_path, 'r') as f:
        metrics = json.load(f)
    
    print("=" * 60)
    print("METRICS VERIFICATION")
    print("=" * 60)
    
    # Summary stats
    print(f"\n📊 Total Queries: {metrics['total_queries']}")
    print(f"✅ Successful: {metrics['successful_queries']}")
    print(f"❌ Failed: {metrics['failed_queries']}")
    print(f"📈 Success Rate: {metrics['success_rate']:.1f}%")
    
    # Intent distribution
    print(f"\n🎯 Intent Distribution:")
    for intent, count in sorted(metrics['intent_distribution'].items(), key=lambda x: x[1], reverse=True):
        print(f"   {intent}: {count}")
    
    # Validation attempts
    print(f"\n🔄 Validation Attempts:")
    for attempts, count in sorted(metrics['validation_attempts'].items()):
        print(f"   {attempts} attempt(s): {count} queries")
    
    # Response time stats
    print(f"\n⏱️  Response Time:")
    print(f"   Average: {metrics['avg_response_time']:.2f}s")
    print(f"   Min: {metrics['min_response_time']:.2f}s")
    print(f"   Max: {metrics['max_response_time']:.2f}s")
    
    # Recent queries
    print(f"\n📝 Recent Queries ({len(metrics['recent_queries'])}):")
    for q in metrics['recent_queries'][-5:]:
        status = "✅" if q['success'] else "❌"
        print(f"   {status} [{q['intent']}] {q['query'][:60]}...")
    
    # Errors
    if metrics['error_types']:
        print(f"\n⚠️  Error Types:")
        for error, count in sorted(metrics['error_types'].items(), key=lambda x: x[1], reverse=True):
            print(f"   {error}: {count}")
    else:
        print(f"\n✅ No errors recorded")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    verify_metrics()
