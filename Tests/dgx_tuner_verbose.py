#!/usr/bin/env python3
"""
Offline Intent Classification Tuner - Verbose DGX Version
Shows detailed progress during execution
"""
import json
import requests
import time
from datetime import datetime
from collections import defaultdict

# Configuration
OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2:3b"
METRICS_FILE = "production_metrics.json"
OUTPUT_FILE = "intent_tuning_results.json"

print("=" * 70)
print("OFFLINE INTENT CLASSIFICATION TUNER")
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

# Check Ollama
print("\n[1/5] Checking Ollama connection...")
print(f"  URL: {OLLAMA_URL}")
print(f"  Model: {MODEL}")
try:
    resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
    if resp.status_code == 200:
        print("  ✓ Ollama is running")
    else:
        print(f"  ✗ Ollama returned status {resp.status_code}")
        exit(1)
except Exception as e:
    print(f"  ✗ Cannot connect: {e}")
    exit(1)

# Load metrics
print(f"\n[2/5] Loading {METRICS_FILE}...")
try:
    with open(METRICS_FILE) as f:
        metrics = json.load(f)
    print(f"  ✓ Loaded {metrics.get('total_queries', 0)} queries")
except Exception as e:
    print(f"  ✗ Error: {e}")
    exit(1)

# Extract training
print("\n[3/5] Extracting training examples from successful queries...")
training = defaultdict(list)
for q in metrics.get("query_history", []):
    if q.get("success") and q.get("intent") != "unknown":
        training[q["intent"]].append(q["query"])

if not training:
    print("  ✗ No successful queries found")
    exit(1)

for intent, queries in training.items():
    print(f"  {intent}: {len(queries)} examples")

# Get failed queries
failed = [q for q in metrics.get("query_history", []) if not q.get("success")]
if not failed:
    print("\n  ✓ No failed queries - nothing to improve!")
    exit(0)

print(f"\n[4/5] Testing {len(failed)} failed queries with Ollama...")
print("  (This will take ~30 seconds)")

results = []
for i, q in enumerate(failed, 1):
    print(f"\n  [{i}/{len(failed)}] Query: {q['query'][:50]}...")
    print(f"      Current intent: {q['intent']}")
    print(f"      Calling Ollama...", end="", flush=True)
    
    # Build prompt
    prompt = f"Classify into: sales_v1, calendar_v1, product_v1, strict_v1\nQuery: {q['query']}\nAnswer with only intent:"
    
    try:
        start = time.time()
        resp = requests.post(f"{OLLAMA_URL}/api/generate", 
            json={"model": MODEL, "prompt": prompt, "stream": False}, timeout=30)
        elapsed = time.time() - start
        
        print(f" done ({elapsed:.1f}s)")
        
        intent = resp.json().get("response", "unknown").strip().lower().split()[0]
        print(f"      Suggested intent: {intent}")
        
        improved = intent != "unknown" and intent != q["intent"]
        if improved:
            print(f"      ✓ IMPROVED!")
        else:
            print(f"      - No improvement")
        
        results.append({
            "query": q["query"],
            "current": q["intent"],
            "suggested": intent,
            "improved": improved,
            "error": q.get("error")
        })
    except Exception as e:
        print(f" ERROR: {e}")
        results.append({
            "query": q["query"],
            "current": q["intent"],
            "suggested": "error",
            "improved": False,
            "error": str(e)
        })
    
    time.sleep(1)

# Generate recommendations
print("\n[5/5] Generating recommendations...")
improved_count = sum(1 for r in results if r["improved"])
improvement_rate = (improved_count / len(results) * 100) if results else 0

# Extract keywords from improved queries
recommendations = defaultdict(set)
for r in results:
    if r["improved"]:
        words = r["query"].lower().split()
        keywords = [w.strip("?,.'\"") for w in words if len(w) > 3]
        for kw in keywords[:3]:
            recommendations[r["suggested"]].add(kw)

report = {
    "timestamp": datetime.now().isoformat(),
    "summary": {
        "total_failed": len(results),
        "improved": improved_count,
        "improvement_rate": improvement_rate
    },
    "results": results,
    "keyword_recommendations": {k: list(v) for k, v in recommendations.items()}
}

# Save
with open(OUTPUT_FILE, "w") as f:
    json.dump(report, f, indent=2)

# Print summary
print("\n" + "=" * 70)
print("RESULTS")
print("=" * 70)
print(f"\nTotal Failed Queries: {len(results)}")
print(f"Improved: {improved_count}")
print(f"Improvement Rate: {improvement_rate:.1f}%")

if recommendations:
    print(f"\nKeyword Recommendations:")
    for intent, keywords in recommendations.items():
        print(f"  {intent}: {', '.join(list(keywords)[:5])}")

print(f"\n✓ Detailed results saved to: {OUTPUT_FILE}")
print(f"✓ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

if improvement_rate > 50:
    print("\n✓ SUCCESS: Recommendations ready for review!")
else:
    print("\n⚠ WARNING: Low improvement rate - collect more data")
