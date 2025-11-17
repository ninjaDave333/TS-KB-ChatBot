#!/usr/bin/env python3

import requests
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# RAGAS imports
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

class TSKBRagasEvaluator:
    """Enhanced RAG evaluation using RAGAS framework"""
    
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
        """Initialize RAGAS metrics with evaluator LLM"""
        self.metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
            answer_correctness
        ]
    
    def create_evaluation_dataset(self) -> EvaluationDataset:
        """Create comprehensive evaluation dataset with ground truth"""
        
        test_cases = [
            {
                "user_input": "How many successful deals were conducted during 2025?",
                "reference": "Based on the data, there were X successful deals (Closed Won status) in 2025.",
                "expected_cypher_pattern": "WHERE o.stage = 'Closed Won' AND o.purchased_date",
                "category": "temporal_deals"
            },
            {
                "user_input": "List 5 clients in Israel with their account managers",
                "reference": "Israeli clients with their respective account managers from the MANAGED_BY relationship.",
                "expected_cypher_pattern": "WHERE c.region = 'IL'",
                "category": "location_relationships"
            },
            {
                "user_input": "How many HashiCorp products were purchased in 2025?",
                "reference": "Number of HashiCorp products purchased in 2025 with client details.",
                "expected_cypher_pattern": "WHERE p.vendor CONTAINS 'hashicorp' AND o.purchased_date",
                "category": "vendor_temporal"
            },
            {
                "user_input": "Show me 5 employees who manage the most clients",
                "reference": "Top 5 employees ranked by number of clients they manage.",
                "expected_cypher_pattern": "MANAGED_BY.*COUNT.*ORDER BY.*DESC",
                "category": "aggregation_relationships"
            },
            {
                "user_input": "What products does Wix have installed?",
                "reference": "List of products installed by Wix with installation details.",
                "expected_cypher_pattern": "WHERE c.sf_name CONTAINS 'Wix'.*HAS_INSTALLED",
                "category": "client_installations"
            }
        ]
        
        samples = []
        
        for case in test_cases:
            try:
                # Query the RAG system
                response = requests.post(
                    f"{self.api_base}/query",
                    json={"query": case["user_input"], "use_ai": True},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract contexts (from Cypher query and schema)
                    retrieved_contexts = [
                        f"Generated Cypher: {data.get('cypher_query', '')}",
                        f"Query method: {data.get('method', '')}",
                        f"Data count: {len(data.get('data', []))}"
                    ]
                    
                    # Create sample
                    sample = SingleTurnSample(
                        user_input=case["user_input"],
                        retrieved_contexts=retrieved_contexts,
                        response=data.get("answer", ""),
                        reference=case["reference"]
                    )
                    samples.append(sample)
                    
            except Exception as e:
                print(f"Error processing case: {case['user_input'][:50]}... - {e}")
                continue
        
        return EvaluationDataset(samples=samples)
    
    async def run_evaluation(self) -> Dict[str, Any]:
        """Run comprehensive RAGAS evaluation"""
        
        print("=== TSKB RAGAS Evaluation ===")
        print("Creating evaluation dataset...")
        
        # Create dataset
        eval_dataset = self.create_evaluation_dataset()
        print(f"Created dataset with {len(eval_dataset.samples)} samples")
        
        # Run evaluation
        print("Running RAGAS evaluation...")
        results = evaluate(
            dataset=eval_dataset,
            metrics=self.metrics,
            llm=self.evaluator_llm
        )
        
        return results
    
    def analyze_results(self, results) -> Dict[str, Any]:
        """Analyze RAGAS results and provide insights"""
        
        # Convert to pandas for analysis
        df = results.to_pandas()
        
        analysis = {
            "overall_scores": {},
            "metric_analysis": {},
            "recommendations": []
        }
        
        # Overall scores
        for metric in ['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall', 'answer_correctness']:
            if metric in df.columns:
                score = df[metric].mean()
                analysis["overall_scores"][metric] = round(score, 3)
        
        # Metric analysis
        for metric, score in analysis["overall_scores"].items():
            if score < 0.7:
                analysis["recommendations"].append(f"Low {metric} ({score:.3f}): Review {self._get_metric_recommendation(metric)}")
            elif score > 0.9:
                analysis["metric_analysis"][metric] = "Excellent performance"
            else:
                analysis["metric_analysis"][metric] = "Good performance"
        
        return analysis
    
    def _get_metric_recommendation(self, metric: str) -> str:
        """Get specific recommendations for low-scoring metrics"""
        recommendations = {
            "faithfulness": "generated answers alignment with retrieved contexts",
            "answer_relevancy": "answer relevance to user questions", 
            "context_precision": "retrieval precision and context quality",
            "context_recall": "context completeness for answering questions",
            "answer_correctness": "factual accuracy against ground truth"
        }
        return recommendations.get(metric, "this metric")
    
    def export_results(self, results, analysis: Dict[str, Any]) -> str:
        """Export detailed results and analysis"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export detailed results
        results_file = f"Tests/ragas_results_{timestamp}.json"
        df = results.to_pandas()
        df.to_json(results_file, orient='records', indent=2)
        
        # Export analysis summary
        summary_file = f"Tests/ragas_analysis_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        return results_file, summary_file
    
    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """Generate human-readable evaluation report"""
        
        report = []
        report.append("=== TSKB RAG EVALUATION REPORT ===")
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Overall Performance
        report.append("OVERALL PERFORMANCE:")
        for metric, score in analysis["overall_scores"].items():
            status = "🟢 Excellent" if score > 0.9 else "🟡 Good" if score > 0.7 else "🔴 Needs Improvement"
            report.append(f"  {metric}: {score:.3f} {status}")
        report.append("")
        
        # Recommendations
        if analysis["recommendations"]:
            report.append("RECOMMENDATIONS:")
            for rec in analysis["recommendations"]:
                report.append(f"  • {rec}")
            report.append("")
        
        # Metric Analysis
        report.append("METRIC ANALYSIS:")
        for metric, status in analysis["metric_analysis"].items():
            report.append(f"  {metric}: {status}")
        
        return "\n".join(report)

async def main():
    """Main evaluation function"""
    
    evaluator = TSKBRagasEvaluator()
    
    try:
        # Run evaluation
        results = await evaluator.run_evaluation()
        
        # Analyze results
        analysis = evaluator.analyze_results(results)
        
        # Export results
        results_file, summary_file = evaluator.export_results(results, analysis)
        
        # Generate and display report
        report = evaluator.generate_report(analysis)
        print(report)
        
        print(f"\nDetailed results: {results_file}")
        print(f"Analysis summary: {summary_file}")
        
    except Exception as e:
        print(f"Evaluation failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())