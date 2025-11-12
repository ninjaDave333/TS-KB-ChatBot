#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database.neo4j_client import Neo4jClient
from app.core.bedrock_client import BedrockClient

def test_model(model_id, query):
    """Test a specific model"""
    print(f"\n{'='*60}")
    print(f"Testing Model: {model_id}")
    print(f"{'='*60}")
    
    # Set environment variable
    os.environ['AWS_BEDROCK_MODEL_ID'] = model_id
    
    # Reinitialize client with new model
    bedrock = BedrockClient()
    client = Neo4jClient()
    schema = client.get_schema()
    
    try:
        print(f"\nQuery: {query}")
        cypher = bedrock.generate_cypher(query, schema)
        print(f"\nGenerated Cypher:\n{cypher}")
        
        # Check for issues
        issues = []
        if 'WITH' in cypher and cypher.count(',') > cypher.count('as'):
            issues.append("⚠️  Potential trailing comma")
        if '2025' not in cypher and '2025' in query:
            issues.append("⚠️  Missing year filter")
        if 'samples' in cypher and 'collect' not in cypher:
            issues.append("⚠️  Undefined variable 'samples'")
        
        # Try to execute
        try:
            result = client.execute_query(cypher)
            print(f"\n✅ Query executed successfully!")
            print(f"Results: {len(result)} records")
            if result:
                print(f"Sample: {result[0]}")
            
            if issues:
                print(f"\n⚠️  Issues found: {', '.join(issues)}")
            
            return {
                "model": model_id,
                "success": True,
                "cypher": cypher,
                "issues": issues,
                "result_count": len(result)
            }
            
        except Exception as exec_error:
            print(f"\n❌ Execution failed: {exec_error}")
            return {
                "model": model_id,
                "success": False,
                "cypher": cypher,
                "issues": issues + [f"Execution error: {str(exec_error)[:100]}"],
                "result_count": 0
            }
            
    except Exception as e:
        print(f"\n❌ Generation failed: {e}")
        return {
            "model": model_id,
            "success": False,
            "cypher": None,
            "issues": [f"Generation error: {str(e)[:100]}"],
            "result_count": 0
        }

def main():
    print("="*60)
    print("MODEL COMPARISON TEST")
    print("="*60)
    
    # Test queries
    test_queries = [
        "how many successful deals were conducted during 2025, show 5 examples",
        "list 5 clients in israel with their account managers",
        "how many hashicorp products were purchased in 2025"
    ]
    
    # Models to test (only Sonnet 4 available in this account)
    models = [
        "us.anthropic.claude-sonnet-4-20250514-v1:0"
    ]
    
    results = []
    
    for query in test_queries:
        print(f"\n\n{'#'*60}")
        print(f"QUERY: {query}")
        print(f"{'#'*60}")
        
        for model in models:
            result = test_model(model, query)
            result['query'] = query
            results.append(result)
    
    # Summary
    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    for model in models:
        model_results = [r for r in results if r['model'] == model]
        success_count = sum(1 for r in model_results if r['success'])
        total = len(model_results)
        
        print(f"\n{model}:")
        print(f"  Success Rate: {success_count}/{total} ({round(success_count/total*100, 1)}%)")
        
        # Count issues
        all_issues = []
        for r in model_results:
            all_issues.extend(r['issues'])
        
        if all_issues:
            from collections import Counter
            issue_counts = Counter(all_issues)
            print(f"  Common Issues:")
            for issue, count in issue_counts.most_common(3):
                print(f"    - {issue}: {count}x")
    
    # Recommendation
    print(f"\n{'='*60}")
    print("RECOMMENDATION")
    print(f"{'='*60}")
    
    if len(models) == 1:
        success = sum(1 for r in results if r['success'])
        print(f"✅ Using {models[0]}")
        print(f"   Success Rate: {success}/{len(results)} ({round(success/len(results)*100, 1)}%)")
    else:
        haiku_success = sum(1 for r in results if r['model'] == models[0] and r['success'])
        sonnet_success = sum(1 for r in results if r['model'] == models[1] and r['success'])
        
        if sonnet_success > haiku_success:
            print(f"✅ Use Claude Sonnet 4 - Better success rate ({sonnet_success} vs {haiku_success})")
        elif haiku_success > sonnet_success:
            print(f"✅ Use Claude Haiku 3.5 - Better success rate ({haiku_success} vs {sonnet_success})")
        else:
            print(f"⚖️  Both models tied - Use Haiku for cost/speed")

if __name__ == "__main__":
    main()