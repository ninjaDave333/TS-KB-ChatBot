#!/usr/bin/env python3
"""
Overnight RAGAS Evaluation
1. Loads synthetic queries
2. Executes against production API
3. Evaluates with RAGAS metrics using Ollama
4. Generates comprehensive report
"""
import json
import requests
import time
from datetime import datetime
from collections import defaultdict

OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2:3b"
QUERIES_FILE = "synthetic_queries.json"
OUTPUT_FILE = "ragas_evaluation_results.json"

def load_synthetic_queries():
    """Load generated queries"""
    with open(QUERIES_FILE) as f:
        return json.load(f)

def execute_query_against_api(query, api_url="http://localhost:8002/api/v1/query"):
    """Execute query against production API"""
    try:
        resp = requests.post(
            api_url,
            json={"query": query},
            timeout=30
        )
        
        if resp.status_code == 200:
            data = resp.json()
            return {
                "success": True,
                "answer": data.get("answer", ""),
                "data": data.get("data", []),
                "cypher": data.get("cypher", ""),
                "execution_time": data.get("execution_time", 0)
            }
        else:
            return {"success": False, "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def evaluate_with_ollama(query, answer, expected_intent):
    """Simple RAGAS-style evaluation using Ollama"""
    
    # 1. Answer Relevancy: Does answer address the question?
    relevancy_prompt = f"""Rate how well this answer addresses the question (0-100):

Question: {query}
Answer: {answer}

Consider:
- Does it directly answer the question?
- Is it complete?
- Is it accurate?

Return ONLY a number 0-100:"""

    # 2. Faithfulness: Is answer grounded in data?
    faithfulness_prompt = f"""Rate how factual and grounded this answer is (0-100):

Answer: {answer}

Consider:
- Does it make unsupported claims?
- Is it based on actual data?
- Does it hallucinate information?

Return ONLY a number 0-100:"""

    scores = {}
    
    # Get relevancy score
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": MODEL, "prompt": relevancy_prompt, "stream": False},
            timeout=20
        )
        if resp.status_code == 200:
            result = resp.json().get("response", "50").strip()
            scores["relevancy"] = int(''.join(filter(str.isdigit, result[:3])) or "50") / 100.0
    except:
        scores["relevancy"] = 0.5
    
    time.sleep(1)
    
    # Get faithfulness score
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": MODEL, "prompt": faithfulness_prompt, "stream": False},
            timeout=20
        )
        if resp.status_code == 200:
            result = resp.json().get("response", "50").strip()
            scores["faithfulness"] = int(''.join(filter(str.isdigit, result[:3])) or "50") / 100.0
    except:
        scores["faithfulness"] = 0.5
    
    # Overall score
    scores["overall"] = (scores["relevancy"] + scores["faithfulness"]) / 2
    
    return scores

def run_overnight_evaluation(sample_size=50):
    """Run overnight RAGAS evaluation"""
    print("=" * 70)
    print("OVERNIGHT RAGAS EVALUATION")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Load queries
    print("\n[1/4] Loading synthetic queries...")
    dataset = load_synthetic_queries()
    queries = dataset["queries"][:sample_size]
    print(f"  Loaded {len(queries)} queries")
    
    # Check Ollama
    print("\n[2/4] Checking Ollama...")
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if resp.status_code != 200:
            print("  ✗ Ollama not running")
            return
        print(f"  ✓ Connected")
    except:
        print("  ✗ Cannot connect")
        return
    
    # Execute and evaluate
    print(f"\n[3/4] Executing and evaluating {len(queries)} queries...")
    print(f"  Estimated time: {len(queries) * 10 / 60:.1f} minutes")
    
    results = []
    by_intent = defaultdict(list)
    
    for i, q in enumerate(queries, 1):
        query_text = q["query"]
        expected_intent = q["expected_intent"]
        
        print(f"\n  [{i}/{len(queries)}] {query_text[:50]}...")
        print(f"      Expected intent: {expected_intent}")
        print(f"      Executing...", end="", flush=True)
        
        # Execute query
        start = time.time()
        api_result = execute_query_against_api(query_text)
        exec_time = time.time() - start
        
        if not api_result["success"]:
            print(f" FAILED: {api_result.get('error', 'Unknown')}")
            results.append({
                "query": query_text,
                "expected_intent": expected_intent,
                "success": False,
                "error": api_result.get("error")
            })
            continue
        
        print(f" done ({exec_time:.1f}s)")
        print(f"      Evaluating with RAGAS...", end="", flush=True)
        
        # Evaluate with RAGAS
        scores = evaluate_with_ollama(
            query_text,
            api_result["answer"],
            expected_intent
        )
        
        print(f" done")
        print(f"      Relevancy: {scores['relevancy']:.2f}, Faithfulness: {scores['faithfulness']:.2f}")
        
        result = {
            "query": query_text,
            "expected_intent": expected_intent,
            "success": True,
            "answer": api_result["answer"],
            "data_count": len(api_result.get("data", [])),
            "execution_time": api_result.get("execution_time", 0),
            "ragas_scores": scores
        }
        
        results.append(result)
        by_intent[expected_intent].append(result)
        
        time.sleep(2)  # Rate limit
    
    # Generate report
    print(f"\n[4/4] Generating report...")
    
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    
    # Calculate averages
    avg_scores = {
        "relevancy": sum(r["ragas_scores"]["relevancy"] for r in successful) / len(successful) if successful else 0,
        "faithfulness": sum(r["ragas_scores"]["faithfulness"] for r in successful) / len(successful) if successful else 0,
        "overall": sum(r["ragas_scores"]["overall"] for r in successful) / len(successful) if successful else 0
    }
    
    # By intent
    intent_scores = {}
    for intent, intent_results in by_intent.items():
        if intent_results:
            intent_scores[intent] = {
                "count": len(intent_results),
                "avg_relevancy": sum(r["ragas_scores"]["relevancy"] for r in intent_results) / len(intent_results),
                "avg_faithfulness": sum(r["ragas_scores"]["faithfulness"] for r in intent_results) / len(intent_results),
                "avg_overall": sum(r["ragas_scores"]["overall"] for r in intent_results) / len(intent_results)
            }
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_queries": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(results) * 100 if results else 0
        },
        "ragas_scores": avg_scores,
        "by_intent": intent_scores,
        "results": results
    }
    
    # Save
    with open(OUTPUT_FILE, "w") as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 70)
    print("RAGAS EVALUATION RESULTS")
    print("=" * 70)
    print(f"\nTotal Queries: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
    
    print(f"\nRAGAS Scores (Average):")
    print(f"  Relevancy: {avg_scores['relevancy']:.2f}")
    print(f"  Faithfulness: {avg_scores['faithfulness']:.2f}")
    print(f"  Overall: {avg_scores['overall']:.2f}")
    
    print(f"\nBy Intent:")
    for intent, scores in intent_scores.items():
        print(f"  {intent}: {scores['count']} queries, overall={scores['avg_overall']:.2f}")
    
    print(f"\n✓ Saved to: {OUTPUT_FILE}")
    print(f"✓ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    if avg_scores['overall'] > 0.7:
        print("\n✓ GOOD: Overall quality above 70%")
    else:
        print("\n⚠ WARNING: Quality needs improvement")

if __name__ == "__main__":
    sample_size = int(input("How many queries to evaluate? (default 50): ") or "50")
    run_overnight_evaluation(sample_size)
