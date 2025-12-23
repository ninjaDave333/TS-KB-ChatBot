#!/usr/bin/env python3
"""
Streaming Pipeline: Generate + Evaluate Simultaneously
Generates queries and immediately evaluates them with RAGAS
"""
import json
import requests
import time
from datetime import datetime
from collections import defaultdict
from pathlib import Path

OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2:3b"
API_URL = "http://localhost:8002/api/v1/query"
OUTPUT_FILE = "streaming_results.json"

def generate_query(template, intent, i):
    """Generate one query"""
    prompt = f"""Generate ONE natural language question:
Template: {template}
Intent: {intent}

Use: Client, Employee, Product, CalendarEvent, Opportunity
Regions: Israel, North, South, East, West
Years: 2023, 2024, 2025
Vendors: HashiCorp, Microsoft, AWS

Rules: Natural language only, under 15 words, business user style

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

def execute_query(query):
    """Execute against API"""
    try:
        resp = requests.post(API_URL, json={"query": query}, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "success": True,
                "answer": data.get("answer", ""),
                "data_count": len(data.get("data", [])),
                "execution_time": data.get("execution_time", 0)
            }
    except:
        pass
    return {"success": False}

def evaluate_ragas(query, answer):
    """Quick RAGAS evaluation"""
    prompt = f"""Rate 0-100: How well does this answer address the question?
Question: {query}
Answer: {answer}
Return only number:"""

    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=15
        )
        if resp.status_code == 200:
            result = resp.json().get("response", "50").strip()
            return int(''.join(filter(str.isdigit, result[:3])) or "50") / 100.0
    except:
        pass
    return 0.5

def streaming_pipeline(num_queries=200):
    """Generate and evaluate in streaming fashion"""
    print("=" * 70)
    print("STREAMING PIPELINE: Generate + Evaluate")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {num_queries} queries")
    print("=" * 70)
    
    templates = [
        "How many {node} in {region}?",
        "List top 5 {node} by {property}",
        "Which {node} has most {relationship}?",
        "Show {node} in {year}",
        "Count {node} by {property}"
    ]
    
    intents = ["sales_v1", "calendar_v1", "product_v1", "strict_v1"]
    results = []
    stats = defaultdict(lambda: {"count": 0, "success": 0, "total_score": 0.0})
    
    for i in range(num_queries):
        intent = intents[i % len(intents)]
        template = templates[i % len(templates)]
        
        print(f"\n[{i+1}/{num_queries}] Intent: {intent}")
        
        # Step 1: Generate
        print(f"  Generating...", end="", flush=True)
        query = generate_query(template, intent, i)
        if not query:
            print(" FAILED")
            continue
        print(f" done")
        print(f"  Query: {query[:60]}...")
        
        # Step 2: Execute
        print(f"  Executing...", end="", flush=True)
        api_result = execute_query(query)
        if not api_result["success"]:
            print(" FAILED")
            stats[intent]["count"] += 1
            continue
        print(f" done ({api_result.get('data_count', 0)} results)")
        
        # Step 3: Evaluate
        print(f"  Evaluating...", end="", flush=True)
        score = evaluate_ragas(query, api_result["answer"])
        print(f" score={score:.2f}")
        
        # Record
        result = {
            "query": query,
            "intent": intent,
            "answer": api_result["answer"],
            "data_count": api_result["data_count"],
            "ragas_score": score,
            "timestamp": datetime.now().isoformat()
        }
        results.append(result)
        
        stats[intent]["count"] += 1
        stats[intent]["success"] += 1
        stats[intent]["total_score"] += score
        
        # Save incrementally every 10 queries
        if (i + 1) % 10 == 0:
            with open(OUTPUT_FILE, "w") as f:
                json.dump({"results": results, "stats": dict(stats)}, f, indent=2)
            print(f"  [Checkpoint saved: {i+1} queries]")
        
        time.sleep(1)
    
    # Final report
    print("\n" + "=" * 70)
    print("STREAMING PIPELINE COMPLETE")
    print("=" * 70)
    print(f"\nTotal: {len(results)}/{num_queries}")
    print(f"\nBy Intent:")
    for intent, data in stats.items():
        if data["count"] > 0:
            avg_score = data["total_score"] / data["success"] if data["success"] > 0 else 0
            print(f"  {intent}: {data['success']}/{data['count']} success, avg_score={avg_score:.2f}")
    
    # Final save
    final_report = {
        "timestamp": datetime.now().isoformat(),
        "total_queries": len(results),
        "results": results,
        "stats": dict(stats)
    }
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(final_report, f, indent=2)
    
    print(f"\n✓ Saved to: {OUTPUT_FILE}")
    print(f"✓ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    num = int(input("How many queries? (default 200): ") or "200")
    streaming_pipeline(num)
