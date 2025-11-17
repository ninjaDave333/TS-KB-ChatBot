#!/usr/bin/env python3

import requests
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# RAGAS imports with AWS Bedrock
from ragas import evaluate, EvaluationDataset, SingleTurnSample
from ragas.metrics import (
    faithfulness,
    answer_relevancy, 
    context_precision,
    context_recall,
    answer_correctness
)
from ragas.llms import LangchainLLMWrapper
from langchain_aws import ChatBedrock

load_dotenv()

class TSKBRagasBedrockEvaluator:
    """RAGAS evaluation using AWS Bedrock"""
    
    def __init__(self):
        self.api_base = "http://localhost:8000/api/v1"
        self.setup_evaluator_llm()
        self.setup_metrics()
        
    def setup_evaluator_llm(self):
        """Setup AWS Bedrock LLM for RAGAS evaluation"""
        self.evaluator_llm = LangchainLLMWrapper(
            ChatBedrock(
                model_id=os.getenv("AWS_BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0"),
                region_name=os.getenv("AWS_REGION", "us-east-1")
            )
        )
    
    def setup_metrics(self):
        """Initialize RAGAS metrics"""
        self.metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
            answer_correctness
        ]
    
    def create_evaluation_dataset(self) -> EvaluationDataset:
        """Create evaluation dataset"""
        
        test_cases = [
            {
                "user_input": "How many successful deals were conducted during 2025?",
                "reference": "There were 547 successful deals with 'Closed Won' status conducted during 2025.",
            },
            {
                "user_input": "List 5 clients in Israel with their account managers",
                "reference": "No Israeli clients found in the database with account manager information.",
            },
            {
                "user_input": "How many HashiCorp products were purchased in 2025?",
                "reference": "In 2025, 8 HashiCorp products were purchased by various clients.",
            }
        ]
        
        samples = []
        
        print("Querying TSKB system for evaluation data...")
        for i, case in enumerate(test_cases, 1):
            print(f"Processing case {i}/{len(test_cases)}")
            
            try:
                response = requests.post(
                    f"{self.api_base}/query",
                    json={"query": case["user_input"], "use_ai": True},
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    retrieved_contexts = [
                        f"Query: {case['user_input']}",
                        f"Database results: {str(data.get('data', []))}",
                        f"The database found {len(data.get('data', []))} records with the requested information.",
                        f"Generated Cypher: {data.get('cypher_query', '')}"
                    ]
                    
                    sample = SingleTurnSample(
                        user_input=case["user_input"],
                        retrieved_contexts=retrieved_contexts,
                        response=data.get("answer", ""),
                        reference=case["reference"]
                    )
                    samples.append(sample)
                    print(f"  ✓ Success: {len(data.get('data', []))} records")
                    
            except Exception as e:
                print(f"  ✗ Error: {e}")
                continue
        
        print(f"Created dataset with {len(samples)} samples")
        return EvaluationDataset(samples=samples)
    
    async def run_evaluation(self) -> Dict[str, Any]:
        """Run RAGAS evaluation"""
        
        print("=== TSKB RAGAS Evaluation (AWS Bedrock) ===")
        
        eval_dataset = self.create_evaluation_dataset()
        
        if len(eval_dataset.samples) == 0:
            raise Exception("No evaluation samples created. Check TSKB API connectivity.")
        
        print(f"\nRunning RAGAS evaluation on {len(eval_dataset.samples)} samples...")
        
        # Use AWS Bedrock embeddings
        from langchain_aws import BedrockEmbeddings
        embeddings = BedrockEmbeddings(
            model_id="amazon.titan-embed-text-v1",
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )
        
        results = evaluate(
            dataset=eval_dataset,
            metrics=self.metrics,
            llm=self.evaluator_llm,
            embeddings=embeddings
        )
        
        return results
    
    def analyze_results(self, results) -> Dict[str, Any]:
        """Analyze RAGAS results"""
        
        df = results.to_pandas()
        
        analysis = {
            "overall_scores": {},
            "recommendations": [],
            "evaluation_time": datetime.now().isoformat()
        }
        
        for metric in ['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall', 'answer_correctness']:
            if metric in df.columns:
                score = df[metric].mean()
                analysis["overall_scores"][metric] = round(score, 3)
        
        for metric, score in analysis["overall_scores"].items():
            if score < 0.7:
                analysis["recommendations"].append(f"Improve {metric} ({score:.3f})")
        
        return analysis
    
    def export_results(self, results, analysis: Dict[str, Any]) -> tuple:
        """Export results"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        results_file = f"Tests/ragas_bedrock_results_{timestamp}.json"
        df = results.to_pandas()
        df.to_json(results_file, orient='records', indent=2)
        
        summary_file = f"Tests/ragas_bedrock_analysis_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        return results_file, summary_file
    
    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """Generate evaluation report"""
        
        report = []
        report.append("=== TSKB RAG EVALUATION REPORT (AWS Bedrock) ===")
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        report.append("OVERALL PERFORMANCE:")
        for metric, score in analysis["overall_scores"].items():
            status = "🟢 Excellent" if score > 0.9 else "🟡 Good" if score > 0.7 else "🔴 Needs Work"
            report.append(f"  {metric}: {score:.3f} {status}")
        report.append("")
        
        if analysis["recommendations"]:
            report.append("RECOMMENDATIONS:")
            for rec in analysis["recommendations"]:
                report.append(f"  • {rec}")
        
        return "\n".join(report)

async def main():
    """Main evaluation function"""
    
    try:
        evaluator = TSKBRagasBedrockEvaluator()
        
        results = await evaluator.run_evaluation()
        analysis = evaluator.analyze_results(results)
        results_file, summary_file = evaluator.export_results(results, analysis)
        
        report = evaluator.generate_report(analysis)
        print(report)
        
        print(f"\nResults exported:")
        print(f"  Detailed: {results_file}")
        print(f"  Summary: {summary_file}")
        
    except Exception as e:
        print(f"Evaluation failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())