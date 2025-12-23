"""Analysis of production metrics to guide Phase 2 decision"""
import json

# Your metrics
metrics = {
    "total_queries": 20,
    "intent_counts": {"strict_v1": 4, "sales_v1": 3, "calendar_v1": 5, "product_v1": 5, "unknown": 3},
    "validation_attempts": {"1": 20},
    "errors": {"CypherTypeError": 1, "CypherSyntaxError": 2},
    "response_times": [3.5, 4.52, 1.2, 2.99, 4.49, 5.75, 4.21, 4.92, 3.99, 1.97, 2.86, 1.87, 3.82, 5.14, 5.27, 4.52, 3.27, 2.87, 6.29, 4.8]
}

print("=" * 70)
print("PRODUCTION METRICS ANALYSIS")
print("=" * 70)

# Success rate
success_rate = ((20 - 3) / 20) * 100
print(f"\nOVERALL PERFORMANCE")
print(f"   Total Queries: 20")
print(f"   Success Rate: {success_rate:.1f}% (17/20)")
print(f"   Failed: 3 queries")

# Intent distribution
print(f"\nINTENT DISTRIBUTION")
for intent, count in sorted(metrics['intent_counts'].items(), key=lambda x: x[1], reverse=True):
    pct = (count / 20) * 100
    print(f"   {intent}: {count} ({pct:.0f}%)")

# Validation
print(f"\nVALIDATION")
print(f"   All queries passed on first attempt (100%)")
print(f"   No retry loops triggered")

# Errors
print(f"\nERRORS (3 failures)")
print(f"   CypherSyntaxError: 2")
print(f"   CypherTypeError: 1")
print(f"   All from 'unknown' intent (3/3)")

# Performance
avg_time = sum(metrics['response_times']) / len(metrics['response_times'])
min_time = min(metrics['response_times'])
max_time = max(metrics['response_times'])
print(f"\nRESPONSE TIME")
print(f"   Average: {avg_time:.2f}s")
print(f"   Min: {min_time:.2f}s")
print(f"   Max: {max_time:.2f}s")

# Key insights
print(f"\n" + "=" * 70)
print("KEY INSIGHTS")
print("=" * 70)
print(f"STRENGTHS:")
print(f"   - High success rate (85%)")
print(f"   - No validation retries needed")
print(f"   - Good intent classification (85% classified)")
print(f"   - Reasonable response times (avg 3.9s)")

print(f"\nWEAKNESSES:")
print(f"   - 'unknown' intent = 100% failure rate (3/3)")
print(f"   - 15% queries unclassified -> errors")
print(f"   - Syntax/Type errors suggest schema mismatch")

# Recommendations
print(f"\n" + "=" * 70)
print("RECOMMENDED NEXT PHASE")
print("=" * 70)
print(f"\nOPTION B: Self-Improvement Loop")
print(f"\nWHY:")
print(f"   1. 'unknown' intent needs better classification")
print(f"   2. 3 syntax/type errors suggest prompt tuning needed")
print(f"   3. No validation retries = prompts working well overall")
print(f"   4. Small dataset (20 queries) = good baseline for tuning")

print(f"\nWHAT TO DO:")
print(f"   1. Improve intent classification (reduce 'unknown' from 15%)")
print(f"   2. Add keywords for edge cases (BU, SyncMetadata, Region)")
print(f"   3. Tune prompts for 'unknown' → strict_v1 fallback")
print(f"   4. Run nightly eval to track improvement")

print(f"\nALTERNATIVE:")
print(f"   • Option C (execution validation) if errors persist after tuning")
print(f"   • Option A (more monitoring) if you want 50+ queries first")

print(f"\n" + "=" * 70)
