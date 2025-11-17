#!/usr/bin/env python3

import requests
import json
from langchain_community.llms import Ollama

def test_ollama_connection(host="172.16.10.250", port=11434):
    """Test connection to Ollama on NVIDIA DGX"""
    
    ollama_url = f"http://{host}:{port}"
    
    print(f"Testing Ollama connection to {ollama_url}")
    
    try:
        # Test API endpoint
        response = requests.get(f"{ollama_url}/api/tags", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            
            print(f"✓ Connected successfully!")
            print(f"Available models ({len(models)}):")
            
            for model in models:
                name = model.get('name', 'Unknown')
                size = model.get('size', 0)
                size_gb = round(size / (1024**3), 1) if size > 0 else 0
                print(f"  - {name} ({size_gb}GB)")
            
            # Test LangChain integration
            if models:
                test_model = models[0]['name'].split(':')[0]
                print(f"\nTesting LangChain integration with {test_model}...")
                
                llm = Ollama(
                    model=test_model,
                    base_url=ollama_url,
                    temperature=0.1
                )
                
                test_prompt = "What is 2+2? Answer briefly."
                response = llm.invoke(test_prompt)
                print(f"✓ LangChain test successful!")
                print(f"Response: {response[:100]}...")
                
                return True, models
            else:
                print("⚠ No models available")
                return False, []
                
        else:
            print(f"✗ HTTP Error: {response.status_code}")
            return False, []
            
    except requests.exceptions.ConnectTimeout:
        print(f"✗ Connection timeout to {ollama_url}")
        print("Check if Ollama is running on the DGX")
        return False, []
        
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to {ollama_url}")
        print("Check network connectivity and Ollama service")
        return False, []
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False, []

def recommend_models():
    """Recommend models for RAGAS evaluation"""
    
    recommendations = {
        "llama3.1": "Best overall performance for evaluation tasks",
        "llama3.1:8b": "Good balance of speed and quality",
        "llama3.1:70b": "Highest quality but slower",
        "mistral": "Fast and efficient for evaluation",
        "codellama": "Good for technical content evaluation"
    }
    
    print("\nRecommended models for RAGAS evaluation:")
    for model, desc in recommendations.items():
        print(f"  - {model}: {desc}")
    
    print("\nTo pull a model on DGX:")
    print("  ollama pull llama3.1")

if __name__ == "__main__":
    success, models = test_ollama_connection()
    
    if success:
        print(f"\n✓ Ollama is ready for RAGAS evaluation!")
        print("Run: .\\Tests\\run_ragas_ollama.ps1")
    else:
        print(f"\n✗ Ollama setup needed")
        recommend_models()