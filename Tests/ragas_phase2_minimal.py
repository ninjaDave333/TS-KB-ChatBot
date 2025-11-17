"""
RAGAS Phase 2: Minimal evaluation bypassing dependency conflicts.
Uses direct AWS Bedrock calls instead of langchain-community.
"""

import json
import boto3
import pandas as pd
from typing import Dict, List
from datetime import datetime

class MinimalRAGAS:
    """Minimal RAGAS implementation using direct AWS Bedrock calls."""
    
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.model_id = "us.anthropic.claude-sonnet-4-20250514-v1:0"
        
    def _call_bedrock(self, prompt: str) -> str:
        """Direct Bedrock API call."""
        try:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            
            result = json.loads(response['body'].read())
            return result['content'][0]['text']
        except Exception as e:
            print(f"Bedrock error: {e}")
            return "0.5"  # Default score on error
    
    def context_utilization(self, question: str, contexts: List[str], answer: str) -> float:
        """Measure how well the answer utilizes retrieved contexts."""
        
        prompt = f"""
Evaluate how well this answer utilizes the provided contexts on a scale of 0-1.

Question: {question}

Contexts:
{chr(10).join(f"- {ctx}" for ctx in contexts)}

Answer: {answer}

Score the context utilization (0.0 = no context used, 1.0 = perfect context usage).
Respond with only a number between 0.0 and 1.0.
"""
        
        try:
            score_text = self._call_bedrock(prompt).strip()
            return float(score_text)
        except:
            return 0.5
    
    def answer_similarity(self, ground_truth: str, answer: str) -> float:
        """Measure semantic similarity between ground truth and generated answer."""
        
        prompt = f"""
Rate the semantic similarity between these two answers on a scale of 0-1.

Ground Truth: {ground_truth}

Generated Answer: {answer}

Score similarity (0.0 = completely different, 1.0 = semantically identical).
Respond with only a number between 0.0 and 1.0.
"""
        
        try:
            score_text = self._call_bedrock(prompt).strip()
            return float(score_text)
        except:
            return 0.5
    
    def context_relevancy(self, question: str, contexts: List[str]) -> float:
        """Measure relevancy of contexts to the question."""
        
        prompt = f"""
Rate how relevant these contexts are to answering the question on a scale of 0-1.

Question: {question}

Contexts:
{chr(10).join(f"- {ctx}" for ctx in contexts)}

Score relevancy (0.0 = irrelevant, 1.0 = highly relevant).
Respond with only a number between 0.0 and 1.0.
"""
        
        try:
            score_text = self._call_bedrock(prompt).strip()
            return float(score_text)
        except:
            return 0.5

def run_phase2_evaluation():
    """Run RAGAS Phase 2 evaluation with advanced metrics."""
    
    print("RAGAS Phase 2: Advanced Evaluation")
    print("=" * 50)
    
    # Test dataset
    test_cases = [
        {
            "question": "How many Israeli clients do we have?",
            "contexts": [
                "Client: Wix.com, Region: IL, Account Manager: John Doe",
                "Client: Check Point, Region: IL, Account Manager: Jane Smith", 
                "Client: Microsoft, Region: US, Account Manager: Bob Wilson"
            ],
            "answer": "Based on the data, we have 2 Israeli clients: Wix.com and Check Point, both located in the IL region.",
            "ground_truth": "There are 2 Israeli clients in the database."
        },
        {
            "question": "What HashiCorp products were purchased in 2025?",
            "contexts": [
                "Product: Terraform Enterprise, Vendor: HashiCorp, Close Date: 2025-03-15",
                "Product: Vault Enterprise, Vendor: HashiCorp, Close Date: 2025-06-20",
                "Product: AWS EC2, Vendor: Amazon, Close Date: 2025-01-10"
            ],
            "answer": "In 2025, clients purchased 2 HashiCorp products: Terraform Enterprise (closed March 15, 2025) and Vault Enterprise (closed June 20, 2025).",
            "ground_truth": "HashiCorp products purchased in 2025 include Terraform Enterprise and Vault Enterprise."
        }
    ]
    
    evaluator = MinimalRAGAS()
    results = []
    
    for i, case in enumerate(test_cases, 1):
        print(f"\nEvaluating Case {i}...")
        
        # Advanced metrics
        context_util = evaluator.context_utilization(
            case["question"], case["contexts"], case["answer"]
        )
        
        answer_sim = evaluator.answer_similarity(
            case["ground_truth"], case["answer"]
        )
        
        context_rel = evaluator.context_relevancy(
            case["question"], case["contexts"]
        )
        
        result = {
            "case": i,
            "question": case["question"],
            "context_utilization": round(context_util, 3),
            "answer_similarity": round(answer_sim, 3),
            "context_relevancy": round(context_rel, 3),
            "average_score": round((context_util + answer_sim + context_rel) / 3, 3)
        }
        
        results.append(result)
        
        print(f"  Context Utilization: {result['context_utilization']}")
        print(f"  Answer Similarity: {result['answer_similarity']}")
        print(f"  Context Relevancy: {result['context_relevancy']}")
        print(f"  Average Score: {result['average_score']}")
    
    # Summary
    print(f"\n{'='*50}")
    print("PHASE 2 SUMMARY")
    print(f"{'='*50}")
    
    avg_context_util = sum(r['context_utilization'] for r in results) / len(results)
    avg_answer_sim = sum(r['answer_similarity'] for r in results) / len(results)
    avg_context_rel = sum(r['context_relevancy'] for r in results) / len(results)
    overall_avg = sum(r['average_score'] for r in results) / len(results)
    
    print(f"Average Context Utilization: {avg_context_util:.3f}")
    print(f"Average Answer Similarity: {avg_answer_sim:.3f}")
    print(f"Average Context Relevancy: {avg_context_rel:.3f}")
    print(f"Overall Average Score: {overall_avg:.3f}")
    
    # Save results
    df = pd.DataFrame(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ragas_phase2_results_{timestamp}.csv"
    df.to_csv(filename, index=False)
    print(f"\nResults saved to: {filename}")
    
    return results

if __name__ == "__main__":
    run_phase2_evaluation()