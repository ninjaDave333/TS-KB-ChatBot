"""
Simple automated query runner with predefined diverse queries.
No external dependencies - just runs realistic queries to populate metrics.
"""
import requests
import time
from typing import List, Dict

API_URL = "http://localhost:8002/api/v1/query"

# Diverse predefined queries covering all intent types
QUERIES = [
    # Sales queries (sales_v1)
    "Top 5 clients with most deals in 2024",
    "How many successful deals closed in 2025?",
    "What is the total revenue from closed won opportunities?",
    "List clients with failed opportunities in 2024",
    "Which account managers have the most closed deals?",
    
    # Calendar queries (calendar_v1)
    "List all meetings David Gidony is owner of in the past 2 months",
    "How many external meetings were recorded in 2024?",
    "Show meetings with more than 5 participants",
    "Which employee has the most recorded meetings?",
    "List all meetings for client PayKey",
    
    # Product queries (product_v1)
    "5 top selling security products during 2023-2025",
    "How many non-TeraSky products do we have?",
    "List all HashiCorp products installed",
    "Which vendors have the most products in our portfolio?",
    "Show products with successful deals in 2025",
    
    # Mixed/complex queries (strict_v1)
    "How many Israeli clients do we have?",
    "List employees operating in the US",
    "Show all clients managed by specific account manager",
    "What products are installed at WIX?",
    "How many opportunities are in pipeline stage?",
]

def send_query(query: str) -> Dict:
    """Send query to API and return response."""
    try:
        response = requests.post(
            API_URL,
            json={"query": query, "use_ai": True},
            timeout=30
        )
        return {
            "query": query,
            "status": response.status_code,
            "success": response.status_code == 200,
            "response": response.json() if response.status_code == 200 else None
        }
    except Exception as e:
        return {
            "query": query,
            "status": 0,
            "success": False,
            "error": str(e)
        }

def run_queries(queries: List[str], delay: float = 3.0):
    """Run queries with delay between requests."""
    print(f"Running {len(queries)} queries...")
    print("=" * 60)
    
    results = []
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] {query}")
        
        result = send_query(query)
        results.append(result)
        
        if result["success"]:
            resp = result["response"]
            method = resp.get('method', 'unknown')
            data_count = len(resp.get('data', []))
            exec_time = resp.get('execution_time', 0)
            print(f"  ✓ {method} - {data_count} results - {exec_time:.2f}s")
        else:
            print(f"  ✗ Failed: {result.get('error', 'Unknown')}")
        
        if i < len(queries):
            time.sleep(delay)
    
    return results

def print_summary(results: List[Dict]):
    """Print summary."""
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    total = len(results)
    success = sum(1 for r in results if r["success"])
    
    print(f"Total: {total}")
    print(f"Success: {success} ({success/total*100:.1f}%)")
    print(f"Failed: {total - success}")
    
    print("\n" + "=" * 60)
    print("Dashboard: http://localhost:8002/dashboard")
    print("=" * 60)

def main():
    """Main execution."""
    print("Automated Query Runner")
    print("=" * 60)
    
    # Check API
    try:
        response = requests.get("http://localhost:8002/health", timeout=5)
        if response.status_code != 200:
            print("ERROR: API not running")
            return
        print("✓ API available\n")
    except:
        print("ERROR: API not running")
        return
    
    # Run queries
    results = run_queries(QUERIES, delay=3.0)
    
    # Summary
    print_summary(results)

if __name__ == "__main__":
    main()
