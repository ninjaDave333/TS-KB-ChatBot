"""
Automated query generator for populating production metrics.
Uses local Ollama to generate diverse, realistic queries based on Neo4j schema.
"""
import asyncio
import json
import requests
from pathlib import Path
from typing import List, Dict
import time

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"  # Fast, lightweight model
API_URL = "http://localhost:8002/api/v1/query"
SCHEMA_FILE = "data/schema_snapshot.json"

def load_schema() -> Dict:
    """Load Neo4j schema for context."""
    with open(SCHEMA_FILE, 'r') as f:
        return json.load(f)

def generate_queries_with_ollama(schema: Dict, count: int = 20) -> List[str]:
    """Generate diverse queries using local Ollama."""
    
    # Build schema context
    nodes = ", ".join(schema.get("nodes", []))
    relationships = ", ".join(schema.get("relationships", []))
    
    prompt = f"""Generate {count} diverse, realistic business questions for a Neo4j database with:
Nodes: {nodes}
Relationships: {relationships}

Focus on:
- Sales queries (deals, revenue, clients)
- Calendar queries (meetings, recordings, participants)
- Product queries (vendors, installations, licenses)
- Employee queries (managers, activity, assignments)

Return ONLY a JSON array of questions, no explanation:
["question1", "question2", ...]"""

    print(f"Generating {count} queries with Ollama ({OLLAMA_MODEL})...")
    
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.8
        },
        timeout=60
    )
    
    if response.status_code != 200:
        raise Exception(f"Ollama error: {response.text}")
    
    # Parse response
    result = response.json()
    text = result.get("response", "")
    
    # Extract JSON array
    try:
        # Find JSON array in response
        start = text.find("[")
        end = text.rfind("]") + 1
        if start >= 0 and end > start:
            queries = json.loads(text[start:end])
            return queries[:count]
    except:
        pass
    
    # Fallback: split by newlines and clean
    lines = [line.strip().strip('"').strip("'").strip(",") 
             for line in text.split("\n") if line.strip()]
    return [q for q in lines if len(q) > 10 and "?" in q][:count]

def send_query(query: str) -> Dict:
    """Send query to API and return response."""
    try:
        response = requests.post(
            API_URL,
            json={"query": query, "use_ai": True},
            timeout=30
        )
        return {
            "query": query,
            "status": response.status_code,
            "success": response.status_code == 200,
            "response": response.json() if response.status_code == 200 else None
        }
    except Exception as e:
        return {
            "query": query,
            "status": 0,
            "success": False,
            "error": str(e)
        }

def run_automated_queries(queries: List[str], delay: float = 2.0):
    """Run queries against API with delay between requests."""
    print(f"\nRunning {len(queries)} queries against API...")
    print("=" * 60)
    
    results = []
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] {query}")
        
        result = send_query(query)
        results.append(result)
        
        if result["success"]:
            resp = result["response"]
            print(f"  ✓ Success: {resp.get('method', 'unknown')} - {len(resp.get('data', []))} results")
        else:
            print(f"  ✗ Failed: {result.get('error', 'Unknown error')}")
        
        # Delay between requests
        if i < len(queries):
            time.sleep(delay)
    
    return results

def print_summary(results: List[Dict]):
    """Print summary of test run."""
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    total = len(results)
    success = sum(1 for r in results if r["success"])
    failed = total - success
    
    print(f"Total Queries: {total}")
    print(f"Successful: {success} ({success/total*100:.1f}%)")
    print(f"Failed: {failed} ({failed/total*100:.1f}%)")
    
    if failed > 0:
        print("\nFailed Queries:")
        for r in results:
            if not r["success"]:
                print(f"  - {r['query'][:60]}...")

def main():
    """Main execution."""
    print("Automated Query Generator for Production Metrics")
    print("=" * 60)
    
    # Check Ollama availability
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("ERROR: Ollama not running. Start with: ollama serve")
            return
        print(f"✓ Ollama available")
    except:
        print("ERROR: Ollama not running. Start with: ollama serve")
        return
    
    # Check API availability
    try:
        response = requests.get("http://localhost:8002/health", timeout=5)
        if response.status_code != 200:
            print("ERROR: API not running. Start server first.")
            return
        print(f"✓ API available")
    except:
        print("ERROR: API not running. Start server first.")
        return
    
    # Load schema
    schema = load_schema()
    print(f"✓ Schema loaded: {len(schema.get('nodes', []))} nodes, {len(schema.get('relationships', []))} relationships")
    
    # Generate queries
    queries = generate_queries_with_ollama(schema, count=20)
    print(f"✓ Generated {len(queries)} queries")
    
    if not queries:
        print("ERROR: No queries generated. Check Ollama response.")
        return
    
    # Run queries
    results = run_automated_queries(queries, delay=2.0)
    
    # Print summary
    print_summary(results)
    
    print("\n" + "=" * 60)
    print("Check dashboard: http://localhost:8002/dashboard")
    print("=" * 60)

if __name__ == "__main__":
    main()
