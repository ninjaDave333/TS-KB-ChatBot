#!/usr/bin/env python3
"""
Teams Recording RAGAS Evaluation - Minimal Implementation
"""

import requests
import json
import boto3
from datetime import datetime

class TeamsRagasEvaluator:
    def __init__(self):
        self.api_base = "http://localhost:8000/api/v1"
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.model_id = "us.anthropic.claude-sonnet-4-20250514-v1:0"
    
    def evaluate_teams_queries(self):
        """Evaluate Teams Recording queries"""
        
        test_cases = [
            {
                "query": "How many external meetings recorded?",
                "expected": "304 external meetings",
                "category": "external_meeting_count"
            },
            {
                "query": "Most active employee meeting wise", 
                "expected": "Gabi Brayer with 88 meetings",
                "category": "employee_ranking"
            },
            {
                "query": "David Gidony meetings breakdown internal external",
                "expected": "External: 75, Internal: 8",
                "category": "meeting_breakdown"
            },
            {
                "query": "Top 3 clients most recorded meetings",
                "expected": "PayKey, FireFly, Ametos with 88 meetings each",
                "category": "client_ranking"
            }
        ]
        
        results = []
        
        for case in test_cases:
            print(f"\nEvaluating: {case['query']}")
            
            # Get RAG response
            response = requests.post(
                f"{self.api_base}/query",
                json={"query": case["query"]},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Evaluate metrics
                metrics = self.evaluate_response(case, data)
                results.append({
                    "query": case["query"],
                    "category": case["category"],
                    "answer": data["answer"],
                    "data_count": len(data.get("data", [])),
                    "method": data.get("method"),
                    "metrics": metrics
                })
                
                print(f"  Answer Quality: {metrics['answer_quality']:.2f}")
                print(f"  Data Accuracy: {metrics['data_accuracy']:.2f}")
                print(f"  Method: {data.get('method')}")
        
        return results
    
    def evaluate_response(self, case, data):
        """Evaluate response quality"""
        
        answer = data.get("answer", "")
        data_count = len(data.get("data", []))
        method = data.get("method", "")
        
        # Answer Quality (0-1)
        answer_quality = 0.0
        if "external meetings" in case["query"].lower():
            if "304" in answer:
                answer_quality = 1.0
            elif "external" in answer.lower():
                answer_quality = 0.7
        elif "most active" in case["query"].lower():
            if "Gabi Brayer" in answer and "88" in answer:
                answer_quality = 1.0
            elif "Gabi Brayer" in answer:
                answer_quality = 0.8
        elif "breakdown" in case["query"].lower():
            if "External: 75" in answer and "Internal: 8" in answer:
                answer_quality = 1.0
            elif "External" in answer and "Internal" in answer:
                answer_quality = 0.8
        elif "top" in case["query"].lower() and "client" in case["query"].lower():
            if "PayKey" in answer and "88" in answer:
                answer_quality = 1.0
            elif "PayKey" in answer:
                answer_quality = 0.7
        
        # Data Accuracy (0-1)
        data_accuracy = 1.0 if data_count > 0 else 0.0
        
        # Method Score (0-1)
        method_score = 1.0 if method == "ai_generated" else 0.5
        
        return {
            "answer_quality": answer_quality,
            "data_accuracy": data_accuracy,
            "method_score": method_score,
            "overall_score": (answer_quality + data_accuracy + method_score) / 3
        }
    
    def generate_report(self, results):
        """Generate evaluation report"""
        
        report = []
        report.append("=== Teams Recording RAGAS Evaluation ===")
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Individual results
        for result in results:
            report.append(f"Query: {result['query']}")
            report.append(f"  Category: {result['category']}")
            report.append(f"  Method: {result['method']}")
            report.append(f"  Data Count: {result['data_count']}")
            report.append(f"  Answer Quality: {result['metrics']['answer_quality']:.2f}")
            report.append(f"  Data Accuracy: {result['metrics']['data_accuracy']:.2f}")
            report.append(f"  Overall Score: {result['metrics']['overall_score']:.2f}")
            report.append("")
        
        # Summary
        avg_quality = sum(r['metrics']['answer_quality'] for r in results) / len(results)
        avg_accuracy = sum(r['metrics']['data_accuracy'] for r in results) / len(results)
        avg_overall = sum(r['metrics']['overall_score'] for r in results) / len(results)
        
        report.append("=== SUMMARY ===")
        report.append(f"Average Answer Quality: {avg_quality:.3f}")
        report.append(f"Average Data Accuracy: {avg_accuracy:.3f}")
        report.append(f"Average Overall Score: {avg_overall:.3f}")
        report.append("")
        
        # Assessment
        if avg_overall >= 0.9:
            report.append("EXCELLENT: Teams Recording integration performing excellently")
        elif avg_overall >= 0.7:
            report.append("GOOD: Teams Recording integration performing well")
        else:
            report.append("NEEDS IMPROVEMENT: Teams Recording integration needs attention")
        
        return "\n".join(report)

def main():
    evaluator = TeamsRagasEvaluator()
    results = evaluator.evaluate_teams_queries()
    report = evaluator.generate_report(results)
    
    print(report)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"Tests/teams_ragas_results_{timestamp}.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()