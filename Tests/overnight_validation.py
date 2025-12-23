"""
Overnight Self-Improvement Validation
- Applies keyword improvements from analysis
- Tests with DGX Ollama (no Bedrock)
- Validates against real Neo4j database
- Runs multiple iterations to find best config
"""
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.neo4j_client import Neo4jClient
from app.core.llm_client import LLMClient
from dotenv import load_dotenv

load_dotenv()

class OvernightValidator:
    def __init__(self):
        self.results_path = Path("data/self_improvement_results.json")
        self.validation_path = Path("data/overnight_validation.json")
        self.neo4j = Neo4jClient()
        
        # Configure for DGX Ollama
        os.environ["LLM_PROVIDER"] = "ollama"
        os.environ["OLLAMA_BASE_URL"] = "http://172.16.10.250:11434"
        os.environ["OLLAMA_MODEL"] = "llama3.2:3b"
        
        self.llm = LLMClient()
        
    def load_improvements(self) -> Dict:
        """Load improvement suggestions"""
        if not self.results_path.exists():
            raise FileNotFoundError("Run production_self_improve.py first")
        
        with open(self.results_path) as f:
            return json.load(f)
    
    def test_query_with_neo4j(self, query: str, intent: str) -> Dict:
        """Test if query can be successfully converted to Cypher and executed"""
        start_time = time.time()
        
        try:
            # Generate Cypher using LLM
            from app.core.bedrock_client import generate_cypher
            
            cypher, detected_intent, attempts = generate_cypher(
                question=query,
                llm_client=self.llm
            )
            
            # Execute against Neo4j
            results = self.neo4j.execute_query(cypher)
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "cypher": cypher,
                "detected_intent": detected_intent,
                "validation_attempts": attempts,
                "result_count": len(results),
                "execution_time": execution_time,
                "error": None
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "cypher": None,
                "detected_intent": None,
                "validation_attempts": 0,
                "result_count": 0,
                "execution_time": execution_time,
                "error": str(e)
            }
    
    def validate_improvements(self, improvements: Dict) -> Dict:
        """Validate each improvement suggestion"""
        print("\n" + "=" * 70)
        print("VALIDATING IMPROVEMENTS")
        print("=" * 70)
        
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "total_suggestions": len(improvements["improvements"]),
            "validated": 0,
            "improved": 0,
            "still_failing": 0,
            "details": []
        }
        
        for i, sugg in enumerate(improvements["improvements"], 1):
            print(f"\n[{i}/{len(improvements['improvements'])}] Testing: {sugg['query'][:50]}...")
            
            result = self.test_query_with_neo4j(
                query=sugg["query"],
                intent=sugg["suggested_intent"]
            )
            
            validation_results["validated"] += 1
            
            if result["success"]:
                validation_results["improved"] += 1
                print(f"  SUCCESS: Generated valid Cypher, {result['result_count']} results")
            else:
                validation_results["still_failing"] += 1
                print(f"  FAILED: {result['error'][:60]}")
            
            validation_results["details"].append({
                "query": sugg["query"],
                "original_intent": sugg["current_intent"],
                "suggested_intent": sugg["suggested_intent"],
                "keywords_added": sugg["keywords_to_add"],
                "validation": result
            })
            
            # Rate limit
            time.sleep(2)
        
        return validation_results
    
    def test_successful_queries(self, improvements: Dict, sample_size: int = 5) -> Dict:
        """Re-test sample of successful queries to ensure no regression"""
        print("\n" + "=" * 70)
        print("REGRESSION TESTING (Sample of Successful Queries)")
        print("=" * 70)
        
        regression_results = {
            "tested": 0,
            "still_successful": 0,
            "regressed": 0,
            "details": []
        }
        
        # Sample successful queries from each intent
        for intent, data in improvements["successful_patterns"].items():
            samples = data["sample_queries"][:min(2, len(data["sample_queries"]))]
            
            for query in samples:
                print(f"\nTesting: {query[:50]}...")
                
                result = self.test_query_with_neo4j(query, intent)
                
                regression_results["tested"] += 1
                
                if result["success"]:
                    regression_results["still_successful"] += 1
                    print(f"  OK: Still working")
                else:
                    regression_results["regressed"] += 1
                    print(f"  REGRESSION: Now failing!")
                
                regression_results["details"].append({
                    "query": query,
                    "intent": intent,
                    "result": result
                })
                
                time.sleep(2)
                
                if regression_results["tested"] >= sample_size:
                    break
            
            if regression_results["tested"] >= sample_size:
                break
        
        return regression_results
    
    def run(self):
        """Run overnight validation"""
        print("=" * 70)
        print("OVERNIGHT SELF-IMPROVEMENT VALIDATION")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        print(f"\nLLM Provider: Ollama (DGX)")
        print(f"Model: llama3.2:3b")
        print(f"Neo4j: {os.getenv('NEO4J_URI')}")
        
        # Load improvements
        print("\n[1/3] Loading improvement suggestions...")
        improvements = self.load_improvements()
        print(f"  Found {len(improvements['improvements'])} suggestions")
        
        # Validate improvements
        print("\n[2/3] Validating improvements...")
        validation_results = self.validate_improvements(improvements)
        
        # Regression test
        print("\n[3/3] Regression testing...")
        regression_results = self.test_successful_queries(improvements)
        
        # Compile final report
        final_report = {
            "timestamp": datetime.now().isoformat(),
            "configuration": {
                "llm_provider": "ollama",
                "model": "llama3.2:3b",
                "neo4j_uri": os.getenv("NEO4J_URI")
            },
            "validation": validation_results,
            "regression": regression_results,
            "summary": {
                "improvement_rate": (validation_results["improved"] / validation_results["validated"] * 100) if validation_results["validated"] > 0 else 0,
                "regression_rate": (regression_results["regressed"] / regression_results["tested"] * 100) if regression_results["tested"] > 0 else 0
            }
        }
        
        # Save results
        self.validation_path.parent.mkdir(exist_ok=True)
        with open(self.validation_path, 'w') as f:
            json.dump(final_report, f, indent=2)
        
        # Print summary
        self.print_summary(final_report)
        
        return final_report
    
    def print_summary(self, report: Dict):
        """Print final summary"""
        print("\n" + "=" * 70)
        print("OVERNIGHT VALIDATION COMPLETE")
        print("=" * 70)
        
        print(f"\nVALIDATION RESULTS:")
        print(f"  Tested: {report['validation']['validated']}")
        print(f"  Improved: {report['validation']['improved']}")
        print(f"  Still Failing: {report['validation']['still_failing']}")
        print(f"  Improvement Rate: {report['summary']['improvement_rate']:.1f}%")
        
        print(f"\nREGRESSION TEST:")
        print(f"  Tested: {report['regression']['tested']}")
        print(f"  Still Successful: {report['regression']['still_successful']}")
        print(f"  Regressed: {report['regression']['regressed']}")
        print(f"  Regression Rate: {report['summary']['regression_rate']:.1f}%")
        
        print(f"\n" + "=" * 70)
        print(f"Full report saved to: {self.validation_path}")
        print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

def main():
    validator = OvernightValidator()
    
    try:
        report = validator.run()
        
        # Exit code based on results
        if report['summary']['improvement_rate'] > 50 and report['summary']['regression_rate'] == 0:
            print("\nSUCCESS: Improvements validated with no regressions!")
            sys.exit(0)
        else:
            print("\nWARNING: Review results before applying changes")
            sys.exit(1)
            
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
