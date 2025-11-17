#!/usr/bin/env python3

import requests
import json
import asyncio
from datetime import datetime
import os
from dotenv import load_dotenv

from ragas import evaluate, EvaluationDataset, SingleTurnSample
from ragas.metrics import answer_relevancy
from ragas.llms import LangchainLLMWrapper
from langchain_aws import ChatBedrock, BedrockEmbeddings

load_dotenv()

async def test_israeli_clients_fix():
    """Test Israeli clients Answer Relevancy fix"""
    
    print("=== Testing Israeli Clients Answer Relevancy Fix ===")
    
    # Setup RAGAS
    evaluator_llm = LangchainLLMWrapper(
        ChatBedrock(
            model_id=os.getenv("AWS_BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0"),
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )
    )
    
    embeddings = BedrockEmbeddings(
        model_id="amazon.titan-embed-text-v1",
        region_name=os.getenv("AWS_REGION", "us-east-1")
    )
    
    # Test the API
    print("Querying TSKB API...")
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/query",
            json={"query": "List 5 clients in Israel with their account managers", "use_ai": True},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API Response: {data['answer']}")
            print(f"✓ Data Count: {len(data['data'])}")
            print(f"✓ Sample: {data['data'][0] if data['data'] else 'No data'}")
            
            # Create RAGAS sample
            sample = SingleTurnSample(
                user_input="List 5 clients in Israel with their account managers",
                retrieved_contexts=[
                    f"Query: List 5 clients in Israel with their account managers",
                    f"Database results: {str(data.get('data', []))}",
                    f"The database found {len(data.get('data', []))} Israeli clients with their account managers.",
                    f"Generated Cypher: {data.get('cypher_query', '')}"
                ],
                response=data.get("answer", ""),
                reference="Here are 5 Israeli clients with their respective account managers from the database."
            )
            
            eval_dataset = EvaluationDataset(samples=[sample])
            
            # Run focused evaluation (just Answer Relevancy)
            print("Running RAGAS evaluation...")
            results = evaluate(
                dataset=eval_dataset,
                metrics=[answer_relevancy],
                llm=evaluator_llm,
                embeddings=embeddings
            )
            
            # Analyze results
            df = results.to_pandas()
            
            print("\n=== RESULTS ===")
            print(f"Answer Relevancy: {df['answer_relevancy'].iloc[0]:.3f} (Previous: 0.000)")
            
            # Check improvement
            answer_relevancy_score = df['answer_relevancy'].iloc[0]
            
            if answer_relevancy_score > 0.8:
                print("🎉 Answer Relevancy EXCELLENT!")
            elif answer_relevancy_score > 0.5:
                print("✅ Answer Relevancy significantly improved")
            elif answer_relevancy_score > 0.0:
                print("🟡 Answer Relevancy improved but needs more work")
            else:
                print("❌ Answer Relevancy still at zero")
            
            # Export results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"Tests/ragas_israeli_fix_{timestamp}.json"
            df.to_json(results_file, orient='records', indent=2)
            print(f"\nResults saved: {results_file}")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_israeli_clients_fix())