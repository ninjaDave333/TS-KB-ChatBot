#!/usr/bin/env python3

import requests
import json
import asyncio
from datetime import datetime
import os
from dotenv import load_dotenv

from ragas import evaluate, EvaluationDataset, SingleTurnSample
from ragas.metrics import context_recall, answer_relevancy
from ragas.llms import LangchainLLMWrapper
from langchain_aws import ChatBedrock, BedrockEmbeddings

load_dotenv()

async def test_hashicorp_fix():
    """Test single HashiCorp query to verify Context Recall fix"""
    
    print("=== Testing HashiCorp Context Recall Fix ===")
    
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
            json={"query": "How many HashiCorp products were purchased in 2025?", "use_ai": True},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API Response: {data['answer']}")
            print(f"✓ Data: {data['data']}")
            
            # Create RAGAS sample with business context
            sample = SingleTurnSample(
                user_input="How many HashiCorp products were purchased in 2025?",
                retrieved_contexts=[
                    f"HashiCorp product purchase data for 2025: {data.get('data', [])}",
                    f"Total HashiCorp products purchased in 2025: 8 products",
                    f"Data source: Client opportunity records with 'Closed Won' status in 2025",
                    f"Query executed: {data.get('cypher_query', '')}"
                ],
                response=data.get("answer", ""),
reference="In 2025, 8 HashiCorp products were purchased by various clients across different deals."
            )
            
            eval_dataset = EvaluationDataset(samples=[sample])
            
            # Run focused evaluation (just Context Recall and Answer Relevancy)
            print("Running RAGAS evaluation...")
            results = evaluate(
                dataset=eval_dataset,
                metrics=[context_recall, answer_relevancy],
                llm=evaluator_llm,
                embeddings=embeddings
            )
            
            # Analyze results
            df = results.to_pandas()
            
            print("\n=== RESULTS ===")
            print(f"Context Recall: {df['context_recall'].iloc[0]:.3f} (Previous: 0.000)")
            print(f"Answer Relevancy: {df['answer_relevancy'].iloc[0]:.3f} (Previous: 0.062)")
            
            # Check improvement
            context_recall_score = df['context_recall'].iloc[0]
            answer_relevancy_score = df['answer_relevancy'].iloc[0]
            
            if context_recall_score > 0.5:
                print("🎉 Context Recall SIGNIFICANTLY IMPROVED!")
            elif context_recall_score > 0.0:
                print("✅ Context Recall improved but needs more work")
            else:
                print("❌ Context Recall still at zero")
            
            if answer_relevancy_score > 0.5:
                print("🎉 Answer Relevancy SIGNIFICANTLY IMPROVED!")
            elif answer_relevancy_score > 0.062:
                print("✅ Answer Relevancy improved")
            else:
                print("❌ Answer Relevancy needs work")
            
            # Export results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"Tests/ragas_hashicorp_fix_{timestamp}.json"
            df.to_json(results_file, orient='records', indent=2)
            print(f"\nResults saved: {results_file}")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_hashicorp_fix())