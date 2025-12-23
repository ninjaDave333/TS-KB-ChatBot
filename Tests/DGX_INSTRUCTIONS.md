# Run Offline Intent Tuner on DGX

## Step 1: Upload Files to DGX

From your Windows laptop:

```powershell
# Upload metrics file
scp d:\Projects\TS-KB-ChatBot\data\production_metrics.json dgx:/tmp/

# Upload deployment script
scp d:\Projects\TS-KB-ChatBot\Tests\deploy_to_dgx.sh dgx:/tmp/
```

## Step 2: SSH to DGX

```powershell
ssh dgx
```

## Step 3: Run on DGX

```bash
cd /tmp
chmod +x deploy_to_dgx.sh
./deploy_to_dgx.sh
```

**OR run manually:**

```bash
# Create standalone script
cat > /tmp/intent_tuner.py << 'EOF'
import json
import requests
import time
from datetime import datetime
from collections import defaultdict

metrics_file = "/tmp/production_metrics.json"
output_file = "/tmp/intent_tuning_results.json"
ollama_url = "http://localhost:11434"
model = "llama3.2:3b"

# Load metrics
with open(metrics_file) as f:
    metrics = json.load(f)

# Extract training data
training = defaultdict(list)
for q in metrics["query_history"]:
    if q["success"] and q["intent"] != "unknown":
        training[q["intent"]].append(q["query"])

print(f"Training examples: {dict((k, len(v)) for k, v in training.items())}")

# Test failed queries
failed = [q for q in metrics["query_history"] if not q["success"]]
results = []

for i, q in enumerate(failed, 1):
    print(f"\n[{i}/{len(failed)}] Testing: {q['query'][:50]}...")
    
    # Build prompt
    prompt = f"""Classify this query into one of: sales_v1, calendar_v1, product_v1, strict_v1

Examples:
sales_v1: {training.get('sales_v1', [''])[0] if training.get('sales_v1') else 'revenue queries'}
calendar_v1: {training.get('calendar_v1', [''])[0] if training.get('calendar_v1') else 'meeting queries'}
product_v1: {training.get('product_v1', [''])[0] if training.get('product_v1') else 'product queries'}
strict_v1: {training.get('strict_v1', [''])[0] if training.get('strict_v1') else 'general queries'}

Query: {q['query']}

Respond with ONLY the intent name:"""
    
    # Call Ollama
    try:
        resp = requests.post(
            f"{ollama_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=30
        )
        intent = resp.json().get("response", "unknown").strip().lower()
        print(f"  {q['intent']} -> {intent}")
        
        results.append({
            "query": q["query"],
            "current": q["intent"],
            "suggested": intent,
            "improved": intent != "unknown"
        })
    except Exception as e:
        print(f"  Error: {e}")
        results.append({"query": q["query"], "current": q["intent"], "suggested": "error", "improved": False})
    
    time.sleep(1)

# Save results
improved = sum(1 for r in results if r["improved"])
report = {
    "timestamp": datetime.now().isoformat(),
    "improved": improved,
    "total": len(results),
    "rate": (improved / len(results) * 100) if results else 0,
    "results": results
}

with open(output_file, "w") as f:
    json.dump(report, f, indent=2)

print(f"\n\nRESULTS: {improved}/{len(results)} improved ({report['rate']:.1f}%)")
print(f"Saved to: {output_file}")
EOF

# Run it
python3 /tmp/intent_tuner.py
```

## Step 4: Download Results

From your Windows laptop:

```powershell
scp dgx:/tmp/intent_tuning_results.json d:\Projects\TS-KB-ChatBot\data\
```

## Step 5: Review Results Tomorrow

```powershell
cd d:\Projects\TS-KB-ChatBot
code data\intent_tuning_results.json
```

---

## Quick One-Liner (Copy-Paste on DGX)

```bash
cd /tmp && \
curl -o production_metrics.json http://YOUR_LAPTOP_IP:8000/production_metrics.json && \
python3 -c "
import json, requests, time
from datetime import datetime
from collections import defaultdict

with open('production_metrics.json') as f: metrics = json.load(f)
training = defaultdict(list)
for q in metrics['query_history']:
    if q['success'] and q['intent'] != 'unknown': training[q['intent']].append(q['query'])

failed = [q for q in metrics['query_history'] if not q['success']]
results = []

for i, q in enumerate(failed, 1):
    print(f'[{i}/{len(failed)}] {q[\"query\"][:40]}...')
    prompt = f'Classify: {q[\"query\"]}\\nOptions: sales_v1, calendar_v1, product_v1, strict_v1\\nAnswer:'
    try:
        resp = requests.post('http://localhost:11434/api/generate', json={'model': 'llama3.2:3b', 'prompt': prompt, 'stream': False}, timeout=30)
        intent = resp.json().get('response', 'unknown').strip().lower().split()[0]
        print(f'  {q[\"intent\"]} -> {intent}')
        results.append({'query': q['query'], 'current': q['intent'], 'suggested': intent, 'improved': intent != 'unknown'})
    except: results.append({'query': q['query'], 'current': q['intent'], 'suggested': 'error', 'improved': False})
    time.sleep(1)

improved = sum(1 for r in results if r['improved'])
with open('intent_tuning_results.json', 'w') as f: json.dump({'improved': improved, 'total': len(results), 'rate': improved/len(results)*100, 'results': results}, f, indent=2)
print(f'\\nRESULTS: {improved}/{len(results)} improved')
"
```

---

## What You'll Get Tomorrow

File: `d:\Projects\TS-KB-ChatBot\data\intent_tuning_results.json`

```json
{
  "improved": 2,
  "total": 3,
  "rate": 66.7,
  "results": [
    {
      "query": "Who is invited to CalendarEvents...",
      "current": "unknown",
      "suggested": "calendar_v1",
      "improved": true
    }
  ]
}
```

If `rate > 50%` → Apply recommendations to production!
