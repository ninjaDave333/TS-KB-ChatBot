#!/bin/bash

# Build and run TSKB-RAG in TS_AI_network
# Compatible with the production-like environment

echo "Building TSKB-RAG Docker image..."
sudo docker build -t tskb-rag .

echo "Running TSKB-RAG container..."
sudo docker run --rm \
  --env-file /home/ubuntu/mb-env-ProdLike/test_env/.env \
  --network TS_AI_network \
  --network-alias tskb-rag \
  -v /home/ubuntu/meetingsBotLogs:/app/logs \
  -v /home/ubuntu/ssl:/app/ssl:ro \
  -p 8002:8002 \
  tskb-rag

echo "TSKB-RAG is running at:"
echo "- API: http://localhost:8002"
echo "- Web UI: http://localhost:8002/promptui"