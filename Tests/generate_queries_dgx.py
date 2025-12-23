"""
Step 1: Generate queries on DGX using Ollama, save to JSON file.
Run this on your dev machine - it connects to DGX remotely.
"""
import json
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# DGX Configuration
DGX_HOST = os.getenv("LOCAL_DGX_IP", "172.16.10.250").strip('"')
OLLAMA_URL = f"http://{DGX_HOST}:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"
OUTPUT_FILE = "generated_queries.json"

def load_schema():
    """Load schema for context."""
    schema_file = Path("data/schema_snapshot.json")
    if schema_file.exists():
        with open(schema_file, 'r') as f:
            return json.load(f)
    return {"nodes": [], "relationships": []}

def generate_queries(schema: dict, count: int = 30):
    """Generate queries using DGX Ollama."""
    
    nodes = ", ".join(schema.get("nodes", []))
    relationships = ", ".join(schema.get("relationships", []))
    
    prompt = f"""Generate {count} diverse business questions for a Neo4j database.

Database schema:
- Nodes: {nodes}
- Relationships: {relationships}

Generate questions covering:
1. Sales queries (deals, revenue, opportunities, clients)
2. Calendar queries (meetings, recordings, participants, owners)
3. Product queries (vendors, installations, non-TeraSky products)
4. Employee queries (managers, activity, assignments)
5. Complex queries (combining multiple entities)

Return ONLY a JSON array of questions:
["question 1?", "question 2?", ...]

Make questions realistic and varied."""

    print(f"Generating {count} queries on DGX ({DGX_HOST})...")
    print(f"Model: {OLLAMA_MODEL}")
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.8
            },
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return []
        
        result = response.json()
        text = result.get("response", "")
        
        # Extract JSON array
        start = text.find("[")
        end = text.rfind("]") + 1
        
        if start >= 0 and end > start:
            queries = json.loads(text[start:end])
            # Validate and filter
            valid_queries = []
            for q in queries:
                if isinstance(q, str) and len(q) > 10 and q.strip():
                    valid_queries.append(q.strip())
            return valid_queries[:count]
        
        print("Could not parse JSON from response")
        return []
        
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Response text: {text[start:end] if 'text' in locals() else 'N/A'}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def save_queries(queries: list, filename: str):
    """Save queries to JSON file with validation."""
    if not queries:
        print("ERROR: No queries to save")
        return False
    
    output = {
        "generated_count": len(queries),
        "model": OLLAMA_MODEL,
        "dgx_host": DGX_HOST,
        "queries": queries
    }
    
    # Validate JSON structure
    try:
        json_str = json.dumps(output, indent=2)
        json.loads(json_str)  # Validate it's valid JSON
    except Exception as e:
        print(f"ERROR: Invalid JSON structure: {e}")
        return False
    
    with open(filename, 'w') as f:
        f.write(json_str)
    
    print(f"\nSaved {len(queries)} queries to: {filename}")
    
    # Validate saved file
    try:
        with open(filename, 'r') as f:
            loaded = json.load(f)
            assert loaded["generated_count"] == len(queries)
            assert len(loaded["queries"]) == len(queries)
        print("✓ JSON validation passed")
        return True
    except Exception as e:
        print(f"ERROR: Saved file validation failed: {e}")
        return False

def main():
    print("=" * 60)
    print("DGX Query Generator (Step 1)")
    print("=" * 60)
    
    # Check DGX Ollama
    try:
        response = requests.get(f"http://{DGX_HOST}:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print(f"ERROR: DGX Ollama not responding at {DGX_HOST}:11434")
            return
        print(f"✓ DGX Ollama available at {DGX_HOST}")
    except Exception as e:
        print(f"ERROR: Cannot reach DGX Ollama: {e}")
        return
    
    # Load schema
    schema = load_schema()
    print(f"✓ Schema loaded: {len(schema.get('nodes', []))} nodes")
    
    # Generate queries
    queries = generate_queries(schema, count=30)
    
    if not queries:
        print("ERROR: No queries generated")
        return
    
    print(f"✓ Generated {len(queries)} queries")
    
    # Preview
    print("\nPreview (first 5):")
    for i, q in enumerate(queries[:5], 1):
        print(f"  {i}. {q}")
    
    # Save
    save_queries(queries, OUTPUT_FILE)
    
    print("\n" + "=" * 60)
    print("Next step:")
    print(f"  python Tests/run_generated_queries.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
