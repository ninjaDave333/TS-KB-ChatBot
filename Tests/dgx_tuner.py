#!/usr/bin/env python3
"""
Offline Intent Classification Tuner - Standalone DGX Version
Run in directory with production_metrics.json
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

def check_ollama():
    """Check if Ollama is running"""
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        return resp.status_code == 200
    except:
        return False

def classify_with_ollama(query, training_examples):
    """Classify query using Ollama"""
    # Build simple prompt with examples
    examples_text = ""
    for intent, queries in training_examples.items():
        if queries:
            examples_text += f"\n{intent.upper()}: {queries[0][:60]}..."
    
    prompt = f"""Classify this database query into one intent:
- sales_v1 (deals, revenue, opportunities)
- calendar_v1 (meetings, recordings, events)
- product_v1 (products, vendors, installations)
- strict_v1 (general organizational queries)

Examples:{examples_text}

Query to classify: "{query}"

Respond with ONLY the intent name (e.g., calendar_v1):"""

    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1}
            },
            timeout=30
        )
        
        if resp.status_code == 200:
            result = resp.json().get("response", "").strip().lower()
            # Extract intent from response
            for intent in ["sales_v1", "calendar_v1", "product_v1", "strict_v1"]:
                if intent in result:
                    return intent
        return "unknown"
    except Exception as e:
        print(f"      Error: {e}")
        return "unknown"

def extract_keywords(query):
    """Extract meaningful keywords from query"""
    stopwords = {
        "what", "which", "have", "been", "that", "with", "from",
        "this", "there", "were", "most", "many", "how", "the", "are", "who"
    }
    words = query.lower().split()
    keywords = []
    for word in words:
        word = word.strip("?,.'\"")
        if len(word) > 3 and word not in stopwords:
            keywords.append(word)
    return keywords[:5]

def main():
    print("=" * 70)
    print("OFFLINE INTENT CLASSIFICATION TUNER")
    print("=" * 70)
    
    # Check Ollama
    print("\n[1/5] Checking Ollama...")
    if not check_ollama():
        print(f"  ERROR: Cannot connect to Ollama at {OLLAMA_URL}")
        print("  Make sure Ollama is running: ollama serve")
        return 1
    print(f"  Connected to {OLLAMA_URL}")
    print(f"  Using model: {MODEL}")
    
    # Load metrics
    print(f"\n[2/5] Loading {METRICS_FILE}...")
    try:
        with open(METRICS_FILE) as f:
            metrics = json.load(f)
    except FileNotFoundError:
        print(f"  ERROR: {METRICS_FILE} not found")
        return 1
    
    total = metrics.get("total_queries", 0)
    print(f"  Loaded {total} queries")
    
    if total == 0:
        print("  ERROR: No queries in metrics file")
        return 1
    
    # Extract training data from successful queries
    print("\n[3/5] Extracting training examples...")
    training = defaultdict(list)
    for q in metrics.get("query_history", []):
        if q.get("success") and q.get("intent") != "unknown":
            training[q["intent"]].append(q["query"])
    
    if not training:
        print("  ERROR: No successful queries to learn from")
        return 1
    
    for intent, queries in training.items():
        print(f"  {intent}: {len(queries)} examples")
    
    # Test failed queries
    print("\n[4/5] Testing failed queries with Ollama...")
    failed = [q for q in metrics.get("query_history", []) if not q.get("success")]
    
    if not failed:
        print("  No failed queries to test!")
        return 0
    
    print(f"  Found {len(failed)} failed queries")
    
    results = []
    for i, q in enumerate(failed, 1):
        query_text = q["query"]
        current_intent = q["intent"]
        
        print(f"\n  [{i}/{len(failed)}] {query_text[:50]}...")
        print(f"    Current: {current_intent}")
        
        # Classify with Ollama
        suggested_intent = classify_with_ollama(query_text, training)
        print(f"    Suggested: {suggested_intent}")
        
        # Extract keywords
        keywords = extract_keywords(query_text)
        
        # Check if improved
        improved = (suggested_intent != "unknown" and 
                   suggested_intent != current_intent)
        
        results.append({
            "query": query_text,
            "current_intent": current_intent,
            "suggested_intent": suggested_intent,
            "keywords": keywords,
            "error": q.get("error"),
            "improved": improved
        })
        
        time.sleep(1)  # Rate limit
    
    # Generate recommendations
    print("\n[5/5] Generating recommendations...")
    recommendations = defaultdict(set)
    for r in results:
        if r["improved"]:
            for kw in r["keywords"]:
                recommendations[r["suggested_intent"]].add(kw)
    
    # Build report
    improved_count = sum(1 for r in results if r["improved"])
    improvement_rate = (improved_count / len(results) * 100) if results else 0
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "configuration": {
            "ollama_url": OLLAMA_URL,
            "model": MODEL,
            "metrics_file": METRICS_FILE
        },
        "summary": {
            "total_failed": len(results),
            "improved": improved_count,
            "still_unknown": sum(1 for r in results if r["suggested_intent"] == "unknown"),
            "improvement_rate": improvement_rate
        },
        "results": results,
        "keyword_recommendations": {k: list(v) for k, v in recommendations.items()}
    }
    
    # Save report
    with open(OUTPUT_FILE, "w") as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"\nTotal Failed Queries: {len(results)}")
    print(f"Improved: {improved_count}")
    print(f"Still Unknown: {report['summary']['still_unknown']}")
    print(f"Improvement Rate: {improvement_rate:.1f}%")
    
    if recommendations:
        print(f"\nKeyword Recommendations:")
        for intent, keywords in recommendations.items():
            print(f"  {intent}: {', '.join(list(keywords)[:5])}")
    
    print(f"\nDetailed results saved to: {OUTPUT_FILE}")
    print("=" * 70)
    
    # Success criteria
    if improvement_rate > 50:
        print("\nSUCCESS: Recommendations ready for review!")
        return 0
    else:
        print("\nWARNING: Low improvement rate - collect more data")
        return 1

if __name__ == "__main__":
    exit(main())
