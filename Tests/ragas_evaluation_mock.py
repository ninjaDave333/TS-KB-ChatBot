#!/usr/bin/env python3

import json
import asyncio
from datetime import datetime
from typing import Dict, Any
import os
from dotenv import load_dotenv

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

class TSKBRagasMockEvaluator:
    """RAGAS evaluation with mock data for testing"""
    
    def __init__(self):
        self.setup_evaluator_llm()
        self.setup_metrics()
        
    def setup_evaluator_llm(self):
        """Setup AWS Bedrock LLM"""
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
    
    def create_mock_dataset(self) -> EvaluationDataset:
        """Create mock evaluation dataset"""
        
        samples = [
            SingleTurnSample(
                user_input="How many successful deals were conducted during 2025?",
                retrieved_contexts=[
                    "Generated Cypher: MATCH (o:OPPORTUNITY) WHERE o.stage = 'Closed Won' AND o.close_date >= '2025-01-01' AND o.close_date < '2026-01-01' RETURN count(o) as total_deals",
                    "Query method: ai_generated",
                    "Data count: 1"
                ],
                response="Based on the data, there were 156 successful deals with 'Closed Won' status in 2025, totaling $45.2M in revenue.",
                reference="Based on the data, there were X successful deals with 'Closed Won' status in 2025, totaling $Y in revenue."
            ),
            SingleTurnSample(
                user_input="List 5 clients in Israel with their account managers",
                retrieved_contexts=[
                    "Generated Cypher: MATCH (c:Client)-[:MANAGED_BY]->(e:Employee) WHERE c.region = 'IL' RETURN c.sf_name, e.name LIMIT 5",
                    "Query method: ai_generated", 
                    "Data count: 5"
                ],
                response="Here are 5 Israeli clients with their account managers: 1. Tufin - managed by Sarah Cohen, 2. Edgybees - managed by David Levy, 3. Wix - managed by Rachel Green, 4. Checkmarx - managed by Michael Brown, 5. Cybereason - managed by Lisa White.",
                reference="Israeli clients (region='IL') with their respective account managers from MANAGED_BY relationships."
            ),
            SingleTurnSample(
                user_input="How many HashiCorp products were purchased in 2025?",
                retrieved_contexts=[
                    "Generated Cypher: MATCH (c:Client)-[:HAS_OPPORTUNITY]->(o:OPPORTUNITY)-[:CONTAINS]->(p:Product) WHERE p.vendor CONTAINS 'hashicorp' AND o.close_date >= '2025-01-01' AND o.close_date < '2026-01-01' AND o.stage = 'Closed Won' RETURN count(p) as hashicorp_products",
                    "Query method: ai_generated",
                    "Data count: 1"
                ],
                response="In 2025, there were 23 HashiCorp products purchased across various clients, with a total value of $2.8M. The most popular products were Terraform Enterprise and Vault Enterprise.",
                reference="Number of HashiCorp products purchased in 2025 with client details and total value."
            )
        ]
        
        return EvaluationDataset(samples=samples)
    
    async def run_evaluation(self) -> Dict[str, Any]:
        """Run RAGAS evaluation with mock data"""
        
        print("=== TSKB RAGAS Evaluation (Mock Data) ===")
        
        eval_dataset = self.create_mock_dataset()
        print(f"Created mock dataset with {len(eval_dataset.samples)} samples")
        
        print("Running RAGAS evaluation...")
        
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
        
        results_file = f"Tests/ragas_mock_results_{timestamp}.json"
        df = results.to_pandas()
        df.to_json(results_file, orient='records', indent=2)
        
        summary_file = f"Tests/ragas_mock_analysis_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        return results_file, summary_file
    
    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """Generate evaluation report"""
        
        report = []
        report.append("=== TSKB RAG EVALUATION REPORT (Mock Data) ===")
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
        evaluator = TSKBRagasMockEvaluator()
        
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