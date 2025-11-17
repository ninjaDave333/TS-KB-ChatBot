#!/bin/bash

# Build and run TSKB-RAG in TS_AI_network
# Compatible with the production-like environment
docker stop tskb-rag
docker rm tskb-rag
docker system prune -f

echo "Building TSKB-RAG Docker image..."
docker build -f Dockerfile -t tskb-rag .

echo "Running TSKB-RAG container..."
docker run -d \
  --name tskb-rag \
  --env-file ../.env \
  --network TS_AI_network \
  --network-alias tskb-rag \
  -p 8002:8002 \
  --restart unless-stopped \
  -v /home/ubuntu/meetingsBotLogs:/app/logs \
  -v /home/ubuntu/ssl:/app/ssl:ro \
  -v /home/ubuntu/meetingsBotLogs/persistentData:/app/data \
  tskb-rag

echo "TSKB-RAG is running at:"
echo "- API: http://localhost:8002"
echo "- Web UI: http://localhost:8002/promptui"

docker logs tskb-rag --follow