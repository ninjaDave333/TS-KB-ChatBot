"""Quick test: Check if DGX Ollama can generate valid Cypher"""
import requests
import json

DGX_URL = "http://172.16.10.250:11434"

def check_available_models():
    """Check what models are available on DGX"""
    try:
        response = requests.get(f"{DGX_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [m["name"] for m in models]
        return []
    except:
        return []

def test_cypher_generation(model: str, question: str):
    """Test if model can generate Cypher"""
    prompt = f"""Convert this question to Neo4j Cypher query:
Question: {question}

Schema:
- Nodes: Client, Employee, Product, CalendarEvent
- Relationships: MANAGED_BY, PURCHASED, INVITED_TO

Generate ONLY the Cypher query, no explanation:"""

    try:
        response = requests.post(
            f"{DGX_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "")
        return None
    except Exception as e:
        return f"Error: {e}"

def main():
    print("=" * 70)
    print("DGX OLLAMA CYPHER CAPABILITY TEST")
    print("=" * 70)
    
    # Check models
    print("\n[1/2] Checking available models...")
    models = check_available_models()
    
    if not models:
        print("  ERROR: Cannot connect to DGX Ollama")
        return
    
    print(f"  Found {len(models)} models:")
    for m in models:
        print(f"    - {m}")
    
    # Recommend best model
    recommended = None
    priority = ["llama3.1:70b", "llama3.1:8b", "llama3.1", "llama3.2:3b", "codellama"]
    for p in priority:
        for m in models:
            if p in m:
                recommended = m
                break
        if recommended:
            break
    
    if not recommended:
        recommended = models[0] if models else None
    
    print(f"\n  Recommended: {recommended}")
    
    # Test Cypher generation
    print("\n[2/2] Testing Cypher generation...")
    test_question = "How many clients are in Israel?"
    print(f"  Question: {test_question}")
    
    result = test_cypher_generation(recommended, test_question)
    
    print(f"\n  Generated:")
    print(f"  {result[:200]}...")
    
    # Validate if it looks like Cypher
    is_cypher = "MATCH" in result.upper() and "RETURN" in result.upper()
    
    print("\n" + "=" * 70)
    if is_cypher:
        print("RESULT: Model CAN generate Cypher")
        print("  Recommendation: Use for overnight validation")
    else:
        print("RESULT: Model CANNOT generate valid Cypher")
        print("  Recommendation: Use Bedrock or upgrade to llama3.1:70b")
    print("=" * 70)

if __name__ == "__main__":
    main()
