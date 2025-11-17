"""
Automated RAGAS quality gate for CI/CD pipeline.
"""

import sys
import json
from ragas_phase2_minimal import MinimalRAGAS

def quality_gate_check():
    """Run quality gate check with pass/fail thresholds."""
    
    # Quality thresholds
    THRESHOLDS = {
        'context_utilization': 0.8,
        'answer_similarity': 0.7,
        'context_relevancy': 0.8,
        'overall_minimum': 0.75
    }
    
    # Quick test cases for CI/CD
    test_cases = [
        {
            "question": "How many clients are in Israel?",
            "contexts": ["Client: Wix.com, Region: IL", "Client: Check Point, Region: IL"],
            "answer": "There are 2 clients in Israel: Wix.com and Check Point.",
            "ground_truth": "2 Israeli clients exist."
        }
    ]
    
    evaluator = MinimalRAGAS()
    
    print("Running RAGAS Quality Gate Check...")
    
    for case in test_cases:
        context_util = evaluator.context_utilization(
            case["question"], case["contexts"], case["answer"]
        )
        answer_sim = evaluator.answer_similarity(
            case["ground_truth"], case["answer"]
        )
        context_rel = evaluator.context_relevancy(
            case["question"], case["contexts"]
        )
        
        overall = (context_util + answer_sim + context_rel) / 3
        
        # Check thresholds
        passed = (
            context_util >= THRESHOLDS['context_utilization'] and
            answer_sim >= THRESHOLDS['answer_similarity'] and
            context_rel >= THRESHOLDS['context_relevancy'] and
            overall >= THRESHOLDS['overall_minimum']
        )
        
        result = {
            "context_utilization": context_util,
            "answer_similarity": answer_sim,
            "context_relevancy": context_rel,
            "overall_score": overall,
            "passed": passed,
            "thresholds": THRESHOLDS
        }
        
        print(f"Context Utilization: {context_util:.3f} (threshold: {THRESHOLDS['context_utilization']})")
        print(f"Answer Similarity: {answer_sim:.3f} (threshold: {THRESHOLDS['answer_similarity']})")
        print(f"Context Relevancy: {context_rel:.3f} (threshold: {THRESHOLDS['context_relevancy']})")
        print(f"Overall Score: {overall:.3f} (threshold: {THRESHOLDS['overall_minimum']})")
        print(f"Quality Gate: {'PASSED' if passed else 'FAILED'}")
        
        if not passed:
            print("[FAIL] Quality gate failed - deployment blocked")
            sys.exit(1)
    
    print("[PASS] Quality gate passed - deployment approved")
    return True

if __name__ == "__main__":
    quality_gate_check()