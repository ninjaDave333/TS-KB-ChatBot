#!/usr/bin/env python3
"""
Offline Streaming: Generate + Classify (No API needed)
Tests query generation and intent classification only
"""
import json
import requests
import time
from datetime import datetime
from collections import defaultdict

OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2:3b"
OUTPUT_FILE = "offline_streaming_results.json"

def generate_query(intent, i):
    """Generate one query"""
    prompt = f"""Generate ONE natural language business question for intent: {intent}

Available data:
- Nodes: Client, Employee, Product, CalendarEvent, Opportunity
- Regions: Israel, North, South, East, West  
- Years: 2023, 2024, 2025
- Vendors: HashiCorp, Microsoft, AWS, Google

Intent types:
- sales_v1: deals, revenue, opportunities, closed won
- calendar_v1: meetings, recordings, events, scheduled
- product_v1: products, vendors, installations, licenses
- strict_v1: employees, organizational, general queries

Generate a {intent} question. Natural language, under 15 words.

Your question:"""

    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0.8}},
            timeout=30
        )
        if resp.status_code == 200:
            return resp.json().get("response", "").strip()
    except:
        pass
    return None

def classify_query(query):
    """Classify query intent"""
    prompt = f"""Classify this query into ONE intent:
- sales_v1 (deals, revenue, opportunities)
- calendar_v1 (meetings, events, recordings)
- product_v1 (products, vendors, installations)
- strict_v1 (employees, organizational)

Query: {query}

Return ONLY the intent name:"""

    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=20
        )
        if resp.status_code == 200:
            result = resp.json().get("response", "").strip().lower()
            for intent in ["sales_v1", "calendar_v1", "product_v1", "strict_v1"]:
                if intent in result:
                    return intent
    except:
        pass
    return "unknown"

def offline_streaming(num_queries=200):
    """Generate and classify queries offline"""
    print("=" * 70)
    print("OFFLINE STREAMING: Generate + Classify")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {num_queries} queries")
    print("=" * 70)
    
    intents = ["sales_v1", "calendar_v1", "product_v1", "strict_v1"]
    results = []
    stats = defaultdict(lambda: {"generated": 0, "correct": 0, "misclassified": 0})
    
    for i in range(num_queries):
        expected_intent = intents[i % len(intents)]
        
        print(f"\n[{i+1}/{num_queries}] Expected: {expected_intent}")
        
        # Generate
        print(f"  Generating...", end="", flush=True)
        query = generate_query(expected_intent, i)
        if not query:
            print(" FAILED")
            continue
        print(f" done")
        print(f"  Query: {query[:60]}...")
        
        # Classify
        print(f"  Classifying...", end="", flush=True)
        detected_intent = classify_query(query)
        print(f" {detected_intent}")
        
        # Check accuracy
        correct = detected_intent == expected_intent
        if correct:
            print(f"  ✓ CORRECT")
            stats[expected_intent]["correct"] += 1
        else:
            print(f"  ✗ WRONG (expected {expected_intent}, got {detected_intent})")
            stats[expected_intent]["misclassified"] += 1
        
        stats[expected_intent]["generated"] += 1
        
        result = {
            "query": query,
            "expected_intent": expected_intent,
            "detected_intent": detected_intent,
            "correct": correct,
            "timestamp": datetime.now().isoformat()
        }
        results.append(result)
        
        # Save checkpoint every 10
        if (i + 1) % 10 == 0:
            with open(OUTPUT_FILE, "w") as f:
                json.dump({"results": results, "stats": dict(stats)}, f, indent=2)
            print(f"  [Checkpoint: {i+1} queries]")
        
        time.sleep(1)
    
    # Final report
    print("\n" + "=" * 70)
    print("OFFLINE STREAMING COMPLETE")
    print("=" * 70)
    print(f"\nTotal: {len(results)}/{num_queries}")
    
    total_correct = sum(s["correct"] for s in stats.values())
    total_generated = sum(s["generated"] for s in stats.values())
    accuracy = (total_correct / total_generated * 100) if total_generated > 0 else 0
    
    print(f"Overall Accuracy: {accuracy:.1f}% ({total_correct}/{total_generated})")
    
    print(f"\nBy Intent:")
    for intent, data in stats.items():
        if data["generated"] > 0:
            intent_acc = (data["correct"] / data["generated"] * 100)
            print(f"  {intent}: {data['correct']}/{data['generated']} correct ({intent_acc:.1f}%)")
    
    # Final save
    final_report = {
        "timestamp": datetime.now().isoformat(),
        "total_queries": len(results),
        "accuracy": accuracy,
        "results": results,
        "stats": dict(stats)
    }
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(final_report, f, indent=2)
    
    print(f"\n✓ Saved to: {OUTPUT_FILE}")
    print(f"✓ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    if accuracy > 70:
        print("\n✓ GOOD: Intent classification accuracy > 70%")
    else:
        print("\n⚠ WARNING: Intent classification needs improvement")

if __name__ == "__main__":
    num = int(input("How many queries? (default 200): ") or "200")
    offline_streaming(num)
