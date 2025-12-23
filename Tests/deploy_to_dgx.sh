#!/bin/bash
# Deploy and run offline intent tuner on DGX
# Run this script on DGX server

set -e

echo "========================================================================"
echo "DGX OFFLINE INTENT TUNER - DEPLOYMENT"
echo "========================================================================"

# Configuration
WORK_DIR="/tmp/intent_tuner_$(date +%Y%m%d_%H%M%S)"
OLLAMA_URL="http://localhost:11434"
MODEL="llama3.2:3b"

# Create working directory
echo ""
echo "[1/5] Creating working directory..."
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"
echo "  Working in: $WORK_DIR"

# Check Ollama
echo ""
echo "[2/5] Checking Ollama..."
if curl -s "$OLLAMA_URL/api/tags" > /dev/null; then
    echo "  ✓ Ollama is running"
else
    echo "  ✗ Ollama not running. Start with: ollama serve"
    exit 1
fi

# Check model
echo ""
echo "[3/5] Checking model availability..."
if curl -s "$OLLAMA_URL/api/tags" | grep -q "$MODEL"; then
    echo "  ✓ Model $MODEL is available"
else
    echo "  ✗ Model $MODEL not found"
    echo "  Pulling model (this may take a few minutes)..."
    ollama pull "$MODEL"
fi

# Create Python script
echo ""
echo "[4/5] Creating tuner script..."
cat > tuner.py << 'PYTHON_SCRIPT'
"""Offline Intent Classification Tuner - DGX Version"""
import json
import requests
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict

class OfflineIntentTuner:
    def __init__(self, metrics_data: Dict):
        self.metrics = metrics_data
        self.ollama_url = "http://localhost:11434"
        self.model = "llama3.2:3b"
        
    def extract_training_data(self) -> Dict[str, List[str]]:
        """Extract successful queries grouped by intent"""
        training = defaultdict(list)
        for q in self.metrics["query_history"]:
            if q["success"] and q["intent"] != "unknown":
                training[q["intent"]].append(q["query"])
        return dict(training)
    
    def classify_with_ollama(self, query: str, training_examples: Dict[str, List[str]]) -> Tuple[str, float]:
        """Use Ollama to classify query intent"""
        prompt = f"""You are an intent classifier for a Neo4j database query system.

Available intents and examples:

SALES_V1 - Deal/opportunity/revenue queries:
{chr(10).join(f"- {ex}" for ex in training_examples.get('sales_v1', [])[:3])}

CALENDAR_V1 - Meeting/recording/event queries:
{chr(10).join(f"- {ex}" for ex in training_examples.get('calendar_v1', [])[:3])}

PRODUCT_V1 - Product/vendor/solution queries:
{chr(10).join(f"- {ex}" for ex in training_examples.get('product_v1', [])[:3])}

STRICT_V1 - General/organizational queries:
{chr(10).join(f"- {ex}" for ex in training_examples.get('strict_v1', [])[:3])}

Classify: "{query}"

Respond with ONLY: INTENT_NAME CONFIDENCE
Example: calendar_v1 85"""

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False, "options": {"temperature": 0.1}},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json().get("response", "").strip().lower()
                parts = result.split()
                if len(parts) >= 2:
                    intent = parts[0]
                    confidence = float(parts[1]) / 100.0
                    return intent, confidence
            return "unknown", 0.0
        except Exception as e:
            print(f"    Error: {e}")
            return "unknown", 0.0
    
    def extract_keywords(self, query: str) -> List[str]:
        """Extract meaningful keywords"""
        stopwords = {"what", "which", "have", "been", "that", "with", "from", "this", "there", "were", "most", "many", "how", "the", "are"}
        words = [w.strip("?,.'\"") for w in query.lower().split()]
        return [w for w in words if len(w) > 3 and w not in stopwords][:5]
    
    def run(self):
        """Run tuning"""
        print("\n" + "=" * 70)
        print("OFFLINE INTENT TUNER - RUNNING")
        print("=" * 70)
        
        # Extract training
        print("\n[1/3] Extracting training data...")
        training = self.extract_training_data()
        for intent, examples in training.items():
            print(f"  {intent}: {len(examples)} examples")
        
        # Test failed queries
        print("\n[2/3] Testing failed queries...")
        failed = [q for q in self.metrics["query_history"] if not q["success"]]
        results = []
        
        for i, q in enumerate(failed, 1):
            print(f"\n  [{i}/{len(failed)}] {q['query'][:50]}...")
            intent, conf = self.classify_with_ollama(q["query"], training)
            keywords = self.extract_keywords(q["query"])
            print(f"    {q['intent']} -> {intent} ({conf:.0%})")
            
            results.append({
                "query": q["query"],
                "current": q["intent"],
                "suggested": intent,
                "confidence": conf,
                "keywords": keywords,
                "improved": intent != "unknown" and intent != q["intent"]
            })
            time.sleep(1)
        
        # Generate recommendations
        print("\n[3/3] Generating recommendations...")
        recommendations = defaultdict(set)
        for r in results:
            if r["improved"]:
                for kw in r["keywords"]:
                    recommendations[r["suggested"]].add(kw)
        
        # Build report
        improved = sum(1 for r in results if r["improved"])
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_failed": len(results),
                "improved": improved,
                "improvement_rate": (improved / len(results) * 100) if results else 0
            },
            "results": results,
            "recommendations": {k: list(v) for k, v in recommendations.items()}
        }
        
        # Save
        with open("intent_tuning_results.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)
        print(f"\nImproved: {improved}/{len(results)} ({report['summary']['improvement_rate']:.1f}%)")
        print(f"\nRecommendations:")
        for intent, kws in report["recommendations"].items():
            print(f"  {intent}: {', '.join(list(kws)[:5])}")
        print(f"\nSaved to: intent_tuning_results.json")
        
        return report

# Load metrics and run
if __name__ == "__main__":
    with open("production_metrics.json") as f:
        metrics = json.load(f)
    
    tuner = OfflineIntentTuner(metrics)
    tuner.run()
PYTHON_SCRIPT

echo "  ✓ Tuner script created"

# Wait for metrics file
echo ""
echo "[5/5] Waiting for production_metrics.json..."
echo "  Please upload production_metrics.json to: $WORK_DIR"
echo ""
echo "  From your laptop, run:"
echo "  scp d:\\Projects\\TS-KB-ChatBot\\data\\production_metrics.json dgx:$WORK_DIR/"
echo ""
read -p "Press Enter when file is uploaded..."

if [ ! -f "production_metrics.json" ]; then
    echo "  ✗ File not found"
    exit 1
fi

echo "  ✓ File found"

# Run tuner
echo ""
echo "========================================================================"
echo "RUNNING TUNER"
echo "========================================================================"
python3 tuner.py

# Show results
echo ""
echo "========================================================================"
echo "DOWNLOAD RESULTS"
echo "========================================================================"
echo ""
echo "From your laptop, run:"
echo "scp dgx:$WORK_DIR/intent_tuning_results.json d:\\Projects\\TS-KB-ChatBot\\data\\"
echo ""
echo "Results location: $WORK_DIR/intent_tuning_results.json"
