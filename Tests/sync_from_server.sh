#!/bin/bash
# Sync production data from server to local ref_data

SERVER="ubuntu@aipg.dudelabz.com"
KEY="D:/Projects/aipg.pem"
REMOTE_PATH="/home/ubuntu/mb-env-ProdLike/test_env/tskb-rag-chatbot/ref_data"
LOCAL_PATH="ref_data"

echo "Fetching production data from server..."

# Critical files for pattern learning
scp -i "$KEY" "$SERVER:$REMOTE_PATH/production_metrics.json" "$LOCAL_PATH/"
scp -i "$KEY" "$SERVER:$REMOTE_PATH/traces.jsonl" "$LOCAL_PATH/"
scp -i "$KEY" "$SERVER:$REMOTE_PATH/query_patterns.json" "$LOCAL_PATH/"

# Optional: Learning state files
scp -i "$KEY" "$SERVER:$REMOTE_PATH/production_insights.json" "$LOCAL_PATH/" 2>/dev/null || true
scp -i "$KEY" "$SERVER:$REMOTE_PATH/self_learning_report.json" "$LOCAL_PATH/" 2>/dev/null || true

echo "✓ Sync complete"
echo "Files updated:"
ls -lh "$LOCAL_PATH"/{production_metrics.json,traces.jsonl,query_patterns.json}
