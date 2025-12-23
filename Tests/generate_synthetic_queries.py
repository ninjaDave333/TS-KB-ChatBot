#!/usr/bin/env python3
"""
Synthetic Query Generator - Uses Ollama to generate diverse test queries
Runs overnight to create comprehensive evaluation dataset
"""
import json
import requests
import time
from datetime import datetime
from collections import defaultdict

OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2:3b"
SCHEMA_FILE = "neo4j_schema.json"
OUTPUT_FILE = "synthetic_queries.json"

# Neo4j Schema (simplified)
SCHEMA = {
    "nodes": ["Client", "Employee", "Product", "CalendarEvent", "Recording", "Opportunity", "Vendor", "BU", "Skill"],
    "relationships": ["MANAGED_BY", "PURCHASED", "INVITED_TO", "OWNS", "HAS_SKILL", "BELONGS_TO"],
    "properties": {
        "Client": ["sf_name", "region", "industry"],
        "Employee": ["name", "email", "title"],
        "Product": ["name", "vendor", "sf_family"],
        "CalendarEvent": ["title", "startTime", "owner"],
        "Opportunity": ["name", "close_date", "opportunity_stage", "total_price"]
    }
}

QUERY_TEMPLATES = [
    "How many {node} are in the database?",
    "List top 5 {node} by {property}",
    "Which {node1} has the most {relationship} to {node2}?",
    "Show me {node} where {property} contains '{value}'",
    "Count {node} grouped by {property}",
    "Find {node1} that are {relationship} {node2} in {region}",
    "What is the average {property} for {node}?",
    "List {node} created in {year}",
    "Show {node1} with no {relationship} to {node2}",
    "Which {node} has the highest {property}?"
]

def generate_query_with_ollama(template, schema, intent):
    """Generate realistic query using Ollama"""
    prompt = f"""You are a business user asking questions about a Neo4j database.

Generate ONE natural language question based on:
Template: {template}
Intent: {intent}

Available data:
- Nodes: Client, Employee, Product, CalendarEvent, Opportunity
- Regions: Israel, North, South, East, West
- Years: 2023, 2024, 2025
- Vendors: HashiCorp, Microsoft, AWS, Google

Rules:
1. Use ONLY natural language (NO SQL, NO Cypher)
2. Sound like a business user asking a question
3. Be specific with values (use real regions, years, vendors)
4. Keep it under 15 words
5. Return ONLY the question

Examples:
- "How many clients are in Israel?"
- "List top 5 employees by client count"
- "Which products did Microsoft sell in 2024?"
- "Show me meetings scheduled for next week"

Your question:"""

    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0.8, "max_tokens": 50}},
            timeout=30
        )
        
        if resp.status_code == 200:
            return resp.json().get("response", "").strip()
        return None
    except:
        return None

def generate_synthetic_dataset(num_queries=50):
    """Generate synthetic queries overnight"""
    print("=" * 70)
    print("SYNTHETIC QUERY GENERATOR")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {num_queries} queries")
    print("=" * 70)
    
    # Check Ollama
    print("\n[1/3] Checking Ollama...")
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if resp.status_code != 200:
            print("  ✗ Ollama not running")
            return
        print(f"  ✓ Connected to {OLLAMA_URL}")
        print(f"  ✓ Using model: {MODEL}")
    except:
        print("  ✗ Cannot connect to Ollama")
        return
    
    # Generate queries
    print(f"\n[2/3] Generating {num_queries} synthetic queries...")
    print(f"  Estimated time: {num_queries * 3 / 60:.1f} minutes")
    
    intents = ["sales_v1", "calendar_v1", "product_v1", "strict_v1"]
    queries = []
    
    for i in range(num_queries):
        intent = intents[i % len(intents)]
        template = QUERY_TEMPLATES[i % len(QUERY_TEMPLATES)]
        
        print(f"\n  [{i+1}/{num_queries}] Generating {intent} query...", end="", flush=True)
        
        start = time.time()
        query = generate_query_with_ollama(template, SCHEMA, intent)
        elapsed = time.time() - start
        
        if query:
            print(f" done ({elapsed:.1f}s)")
            print(f"      Query: {query[:60]}...")
            
            queries.append({
                "query": query,
                "expected_intent": intent,
                "template": template,
                "generated_at": datetime.now().isoformat()
            })
        else:
            print(f" FAILED")
        
        time.sleep(1)  # Rate limit
    
    # Save dataset
    print(f"\n[3/3] Saving dataset...")
    dataset = {
        "generated_at": datetime.now().isoformat(),
        "total_queries": len(queries),
        "by_intent": {intent: len([q for q in queries if q["expected_intent"] == intent]) for intent in intents},
        "queries": queries
    }
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(dataset, f, indent=2)
    
    # Summary
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"\nGenerated: {len(queries)}/{num_queries} queries")
    print(f"\nBy Intent:")
    for intent, count in dataset["by_intent"].items():
        print(f"  {intent}: {count}")
    print(f"\n✓ Saved to: {OUTPUT_FILE}")
    print(f"✓ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return dataset

if __name__ == "__main__":
    # Generate 50 queries (takes ~2.5 minutes)
    # For overnight: increase to 200+ queries
    num_queries = int(input("How many queries to generate? (default 50): ") or "50")
    generate_synthetic_dataset(num_queries)
