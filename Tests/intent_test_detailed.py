#!/usr/bin/env python3
import requests
import json
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"

INTENTS = ["sales_v1", "calendar_v1", "product_v1", "strict_v1"]

def generate_query(intent):
    prompt = f"""Generate ONE natural language question for a Neo4j knowledge base about TeraSky clients, products, and meetings.

Intent: {intent}

Examples:
- sales_v1: "Which clients closed the most deals in Q4 2024?"
- calendar_v1: "Show me all meetings David attended last week"
- product_v1: "What HashiCorp products were purchased in 2025?"
- strict_v1: "How many opportunities are in the pipeline?"

Generate ONLY the question, no explanation:"""

    resp = requests.post(OLLAMA_URL, json={"model": MODEL, "prompt": prompt, "stream": False}, timeout=30)
    return resp.json()["response"].strip().strip('"')

def classify_query(query):
    prompt = f"""Classify this question into ONE intent category.

Question: "{query}"

Categories:
- sales_v1: deals, opportunities, revenue, clients, purchases
- calendar_v1: meetings, recordings, calendar events, attendees
- product_v1: products, vendors, solutions, licenses
- strict_v1: general/ambiguous questions

Return ONLY the category name (sales_v1, calendar_v1, product_v1, or strict_v1):"""

    resp = requests.post(OLLAMA_URL, json={"model": MODEL, "prompt": prompt, "stream": False}, timeout=30)
    return resp.json()["response"].strip()

def main():
    results = []
    correct = 0
    total = 0
    stats = {intent: {"correct": 0, "total": 0} for intent in INTENTS}
    misclassifications = []

    for i in range(100):
        expected = INTENTS[i % 4]
        query = generate_query(expected)
        predicted = classify_query(query)
        
        is_correct = predicted == expected
        if is_correct:
            correct += 1
            stats[expected]["correct"] += 1
        else:
            misclassifications.append({
                "query": query,
                "expected": expected,
                "predicted": predicted
            })
        
        stats[expected]["total"] += 1
        total += 1
        
        status = "✓" if is_correct else "✗"
        print(f"[{i+1}/100] {expected} -> {predicted} {status}")
        time.sleep(0.1)

    print(f"\n{'='*70}")
    print(f"RESULTS: {correct}/{total} ({int(correct/total*100)}%)")
    for intent in INTENTS:
        s = stats[intent]
        pct = int(s["correct"]/s["total"]*100) if s["total"] > 0 else 0
        print(f"  {intent}: {s['correct']}/{s['total']} ({pct}%)")

    with open('intent_test_results.json', 'w') as f:
        json.dump({
            'accuracy': int(correct / total * 100),
            'stats': stats,
            'misclassifications': misclassifications
        }, f, indent=2)
    
    print(f"\nSaved to: intent_test_results.json")

if __name__ == "__main__":
    main()
