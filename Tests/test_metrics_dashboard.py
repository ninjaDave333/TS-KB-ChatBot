"""
Quick test script for metrics collector functionality.
Run this to verify metrics collection and dashboard data.
"""
import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.metrics_collector import metrics_collector

def test_metrics_collector():
    """Test basic metrics collector functionality."""
    print("Testing Metrics Collector...")
    print("=" * 60)
    
    # Reset metrics for clean test
    metrics_collector.reset_metrics()
    print("[OK] Metrics reset")
    
    # Record some test queries
    test_queries = [
        ("Top 5 clients with most deals", "sales_v1", 1, 2.5, True, None),
        ("List meetings for David", "calendar_v1", 1, 1.8, True, None),
        ("Show HashiCorp products", "product_v1", 2, 3.2, True, None),
        ("Invalid query test", "strict_v1", 2, 1.5, False, "ValidationError"),
        ("Another sales query", "sales_v1", 1, 2.1, True, None),
    ]
    
    for query, intent, attempts, time, success, error in test_queries:
        metrics_collector.record_query(query, intent, attempts, time, success, error)
        print(f"[OK] Recorded: {query[:30]}... (intent={intent}, attempts={attempts})")
    
    print("\n" + "=" * 60)
    print("Metrics Summary:")
    print("=" * 60)
    
    # Get metrics
    metrics = metrics_collector.get_metrics()
    
    print(f"\nTotal Queries: {metrics['total_queries']}")
    print(f"\nIntent Distribution:")
    for intent, count in metrics['intent_distribution'].items():
        print(f"  - {intent}: {count}")
    
    print(f"\nValidation Attempts:")
    for attempts, count in metrics['validation_attempts'].items():
        print(f"  - {attempts} attempt(s): {count}")
    
    print(f"\nPerformance:")
    print(f"  - Avg Response Time: {metrics['performance']['avg_response_time']}s")
    print(f"  - Min Response Time: {metrics['performance']['min_response_time']}s")
    print(f"  - Max Response Time: {metrics['performance']['max_response_time']}s")
    
    print(f"\nErrors:")
    if metrics['errors']:
        for error_type, count in metrics['errors'].items():
            print(f"  - {error_type}: {count}")
    else:
        print("  - No errors recorded")
    
    print(f"\nRecent Queries: {len(metrics['recent_queries'])}")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Metrics Collector Test Complete!")
    print("=" * 60)
    
    # Verify metrics file was created
    metrics_file = Path("data/production_metrics.json")
    if metrics_file.exists():
        print(f"\n[OK] Metrics file created: {metrics_file}")
        print(f"  File size: {metrics_file.stat().st_size} bytes")
    else:
        print(f"\n[ERROR] Metrics file not found: {metrics_file}")
    
    return metrics

if __name__ == "__main__":
    try:
        metrics = test_metrics_collector()
        print("\n" + "=" * 60)
        print("Next Steps:")
        print("=" * 60)
        print("1. Start the server: python -m uvicorn app.main:app --reload --port 8002")
        print("2. Open dashboard: http://localhost:8002/dashboard")
        print("3. Run some queries via: http://localhost:8002/promptui")
        print("4. Watch metrics update in real-time!")
        print("=" * 60)
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
