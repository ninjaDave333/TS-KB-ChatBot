# SSH Deployment Configuration

*** always get explicit permission before running any of these commands !!! ***

## Remote DEV Server Access
- **Host**: aipg.dudelabz.com:22
- **User**: ubuntu
- **SSH Key**: D:\Projects\aipg.pem
- **Project Path**: /home/ubuntu/mb-env-ProdLike/test_env/tskb-rag-chatbot

## SSH Commands

### Test Connection
```bash
ssh -i D:\Projects\aipg.pem ubuntu@aipg.dudelabz.com "ls -la /home/ubuntu/mb-env-ProdLike/test_env/tskb-rag-chatbot"
```

### Copy Single File
```bash
scp -i D:\Projects\aipg.pem <local-file> ubuntu@aipg.dudelabz.com:/home/ubuntu/mb-env-ProdLike/test_env/tskb-rag-chatbot/<remote-path>
```

### Copy Directory
```bash
scp -i D:\Projects\aipg.pem -r <local-dir> ubuntu@aipg.dudelabz.com:/home/ubuntu/mb-env-ProdLike/test_env/tskb-rag-chatbot/<remote-path>
```

### Execute Remote Command
```bash
ssh -i D:\Projects\aipg.pem ubuntu@aipg.dudelabz.com "<command>"
```

## Docker Rebuild Commands

### Use build_and_run_auto.sh Script always on new code update/change(Recommended)
```bash
ssh -i D:\Projects\aipg.pem ubuntu@aipg.dudelabz.com "cd /home/ubuntu/mb-env-ProdLike/test_env/tskb-rag-chatbot && sudo ./use build_and_run_auto.sh"
```

### Manual Rebuild Container
```bash
ssh -i D:\Projects\aipg.pem ubuntu@aipg.dudelabz.com "cd /home/ubuntu/mb-env-ProdLike/test_env/tskb-rag-chatbot && sudo docker build -t tskb-rag ."
```

### Manual Restart Container
```bash
ssh -i D:\Projects\aipg.pem ubuntu@aipg.dudelabz.com "sudo docker stop tskb-rag && sudo docker run --rm --env-file /home/ubuntu/mb-env-ProdLike/test_env/.env --network TS_AI_network --network-alias tskb-rag -v /home/ubuntu/meetingsBotLogs:/app/logs -v /home/ubuntu/ssl:/app/ssl:ro -p 8002:8002 tskb-rag"
```

## Deployment Workflow

1. **Copy modified files** to remote server
2. **Run build_and_run.sh** script (handles stop, build, run automatically)
3. **Monitor logs** with `docker logs tskb-rag --follow`

## build_and_run.sh Script Details

The script performs:
- Stops and removes existing container
- Cleans up Docker system
- Builds new image from Dockerfile
- Runs container with:
  - Name: tskb-rag
  - Network: TS_AI_network
  - Port: 8002
  - Restart policy: unless-stopped
  - Volumes: logs, SSL certs, persistent data
  - Follows logs automatically


## Notes
- Always test connection before bulk operations
- Use `-r` flag for recursive directory copy
- Container runs on port 8002 with HTTPS
- Logs persist at /home/ubuntu/meetingsBotLogs
