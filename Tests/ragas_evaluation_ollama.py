#!/usr/bin/env python3

import requests
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# RAGAS imports with Ollama
from ragas import evaluate, EvaluationDataset, SingleTurnSample
from ragas.metrics import (
    faithfulness,
    answer_relevancy, 
    context_precision,
    context_recall,
    answer_correctness
)
from ragas.llms import LangchainLLMWrapper
from langchain_community.llms import Ollama

load_dotenv()

class TSKBRagasOllamaEvaluator:
    """RAGAS evaluation using local Ollama on NVIDIA DGX"""
    
    def __init__(self, model="llama3.1"):
        self.api_base = "http://localhost:8000/api/v1"
        self.ollama_host = os.getenv("LOCAL_DGX_IP", "172.16.10.250").strip('"')
        self.ollama_port = 11434
        self.dgx_user = os.getenv("LOCAL_DGX_USER", "terasky").strip('"')
        self.dgx_pass = os.getenv("LOCAL_DGX_PASS", "terasky").strip('"')
        self.model = model
        self.setup_evaluator_llm()
        self.setup_metrics()
        
    def setup_evaluator_llm(self):
        """Setup Ollama LLM for RAGAS evaluation"""
        ollama_url = f"http://{self.ollama_host}:{self.ollama_port}"
        
        # Test connection
        try:
            response = requests.get(f"{ollama_url}/api/tags")
            if response.status_code == 200:
                print(f"✓ Connected to Ollama at {ollama_url}")
                models = response.json().get('models', [])
                available_models = [m['name'] for m in models]
                print(f"Available models: {available_models}")
                
                if not any(self.model in m for m in available_models):
                    print(f"⚠ Model {self.model} not found. Using first available model.")
                    if available_models:
                        self.model = available_models[0].split(':')[0]
                        print(f"Using model: {self.model}")
            else:
                raise Exception(f"Ollama not responding: {response.status_code}")
                
        except Exception as e:
            print(f"✗ Cannot connect to Ollama: {e}")
            raise
        
        self.evaluator_llm = LangchainLLMWrapper(
            Ollama(
                model=self.model,
                base_url=ollama_url,
                temperature=0.1
            )
        )
    
    def setup_metrics(self):
        """Initialize RAGAS metrics with Ollama LLM"""
        self.metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
            answer_correctness
        ]
    
    def create_evaluation_dataset(self) -> EvaluationDataset:
        """Create evaluation dataset with ground truth"""
        
        test_cases = [
            {
                "user_input": "How many successful deals were conducted during 2025?",
                "reference": "Based on the data, there were X successful deals with 'Closed Won' status in 2025, totaling $Y in revenue.",
                "category": "temporal_deals"
            },
            {
                "user_input": "List 5 clients in Israel with their account managers",
                "reference": "Israeli clients (region='IL') with their respective account managers from MANAGED_BY relationships.",
                "category": "location_relationships"
            },
            {
                "user_input": "How many HashiCorp products were purchased in 2025?",
                "reference": "Number of HashiCorp products purchased in 2025 with client details and total value.",
                "category": "vendor_temporal"
            },
            {
                "user_input": "Show me 5 employees who manage the most clients",
                "reference": "Top 5 employees ranked by number of clients they manage through MANAGED_BY relationships.",
                "category": "aggregation_relationships"
            },
            {
                "user_input": "What products does Wix have installed?",
                "reference": "List of products installed by Wix through HAS_INSTALLED relationships with installation details.",
                "category": "client_installations"
            }
        ]
        
        samples = []
        
        print("Querying TSKB system for evaluation data...")
        for i, case in enumerate(test_cases, 1):
            print(f"Processing case {i}/{len(test_cases)}: {case['category']}")
            
            try:
                response = requests.post(
                    f"{self.api_base}/query",
                    json={"query": case["user_input"], "use_ai": True},
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract contexts
                    retrieved_contexts = [
                        f"Generated Cypher: {data.get('cypher_query', '')}",
                        f"Query method: {data.get('method', '')}",
                        f"Data count: {len(data.get('data', []))}"
                    ]
                    
                    # Add sample data context if available
                    if data.get('data'):
                        sample_data = str(data['data'][:2])  # First 2 records
                        retrieved_contexts.append(f"Sample data: {sample_data}")
                    
                    sample = SingleTurnSample(
                        user_input=case["user_input"],
                        retrieved_contexts=retrieved_contexts,
                        response=data.get("answer", ""),
                        reference=case["reference"]
                    )
                    samples.append(sample)
                    print(f"  ✓ Success: {len(data.get('data', []))} records")
                    
                else:
                    print(f"  ✗ API Error: {response.status_code}")
                    
            except Exception as e:
                print(f"  ✗ Error: {e}")
                continue
        
        print(f"Created dataset with {len(samples)} samples")
        return EvaluationDataset(samples=samples)
    
    async def run_evaluation(self) -> Dict[str, Any]:
        """Run RAGAS evaluation using Ollama"""
        
        print("=== TSKB RAGAS Evaluation (Ollama) ===")
        print(f"Using Ollama at {self.ollama_host}:{self.ollama_port}")
        print(f"Model: {self.model}")
        
        # Create dataset
        eval_dataset = self.create_evaluation_dataset()
        
        if len(eval_dataset.samples) == 0:
            raise Exception("No evaluation samples created. Check TSKB API connectivity.")
        
        # Run evaluation
        print(f"\nRunning RAGAS evaluation on {len(eval_dataset.samples)} samples...")
        print("This may take several minutes with local LLM...")
        
        results = evaluate(
            dataset=eval_dataset,
            metrics=self.metrics,
            llm=self.evaluator_llm
        )
        
        return results
    
    def analyze_results(self, results) -> Dict[str, Any]:
        """Analyze RAGAS results"""
        
        df = results.to_pandas()
        
        analysis = {
            "overall_scores": {},
            "metric_analysis": {},
            "recommendations": [],
            "ollama_info": {
                "host": self.ollama_host,
                "model": self.model,
                "evaluation_time": datetime.now().isoformat()
            }
        }
        
        # Calculate scores
        for metric in ['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall', 'answer_correctness']:
            if metric in df.columns:
                score = df[metric].mean()
                analysis["overall_scores"][metric] = round(score, 3)
        
        # Generate recommendations
        for metric, score in analysis["overall_scores"].items():
            if score < 0.7:
                analysis["recommendations"].append(f"Improve {metric} ({score:.3f}): {self._get_recommendation(metric)}")
            elif score > 0.9:
                analysis["metric_analysis"][metric] = "Excellent"
            else:
                analysis["metric_analysis"][metric] = "Good"
        
        return analysis
    
    def _get_recommendation(self, metric: str) -> str:
        """Get recommendations for low scores"""
        recs = {
            "faithfulness": "Ensure answers align with retrieved contexts",
            "answer_relevancy": "Improve answer relevance to questions", 
            "context_precision": "Enhance retrieval precision",
            "context_recall": "Improve context completeness",
            "answer_correctness": "Verify factual accuracy"
        }
        return recs.get(metric, "Review this metric")
    
    def export_results(self, results, analysis: Dict[str, Any]) -> tuple:
        """Export results with Ollama metadata"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export detailed results
        results_file = f"Tests/ragas_ollama_results_{timestamp}.json"
        df = results.to_pandas()
        df.to_json(results_file, orient='records', indent=2)
        
        # Export analysis
        summary_file = f"Tests/ragas_ollama_analysis_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        return results_file, summary_file
    
    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """Generate evaluation report"""
        
        report = []
        report.append("=== TSKB RAG EVALUATION REPORT (Ollama) ===")
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Ollama Host: {analysis['ollama_info']['host']}")
        report.append(f"Model: {analysis['ollama_info']['model']}")
        report.append("")
        
        # Scores
        report.append("OVERALL PERFORMANCE:")
        for metric, score in analysis["overall_scores"].items():
            status = "🟢 Excellent" if score > 0.9 else "🟡 Good" if score > 0.7 else "🔴 Needs Work"
            report.append(f"  {metric}: {score:.3f} {status}")
        report.append("")
        
        # Recommendations
        if analysis["recommendations"]:
            report.append("RECOMMENDATIONS:")
            for rec in analysis["recommendations"]:
                report.append(f"  • {rec}")
        
        return "\n".join(report)

async def main():
    """Main evaluation function"""
    
    # Configuration from .env
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
    
    try:
        evaluator = TSKBRagasOllamaEvaluator(
            model=OLLAMA_MODEL
        )
        
        # Run evaluation
        results = await evaluator.run_evaluation()
        
        # Analyze results
        analysis = evaluator.analyze_results(results)
        
        # Export results
        results_file, summary_file = evaluator.export_results(results, analysis)
        
        # Generate report
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