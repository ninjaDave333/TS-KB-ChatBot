# TSKB-RAG Chatbot System

Natural language interface to TeraSky's Technical Solution Knowledge Base using Neo4j and AWS Bedrock.

## Quick Start

### Prerequisites
- Python 3.9+
- Neo4j 5.15+
- AWS Bedrock access

### Installation

```bash
# Clone and navigate
cd TS-KB-ChatBot

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your credentials
```

### Run

```bash
# Activate venv
venv\Scripts\activate

# Start server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API available at: `http://localhost:8000`  
Web UI available at: `http://localhost:8000/promptui`

## Usage

### Web Interface

Access the interactive chat interface at `http://localhost:8000/promptui` for:
- Real-time query testing
- Chat-style interaction
- Query history (session-based)
- Response metadata display

### Query Endpoint

```bash
POST /api/v1/query
Content-Type: application/json

{
  "query": "How many clients purchased HashiCorp products in 2025?"
}
```

### Response Format

```json
{
  "query": "...",
  "answer": "...",
  "confidence": 95,
  "data": [...],
  "execution_time": 1.2
}
```

## Architecture

- **API**: FastAPI with async support
- **Database**: Neo4j (read-only)
- **LLM**: AWS Bedrock (Claude)
- **Deployment**: Docker

## Project Structure

```
TS-KB-ChatBot/
├── app/
│   ├── api/          # API routes
│   ├── core/         # Business logic
│   ├── database/     # Neo4j client
│   └── main.py       # Application entry
├── docs/             # Documentation
├── Tests/            # Test scripts
└── requirements.txt
```

## Configuration

Edit `.env`:

```env
# For TS_AI_network deployment
NEO4J_URI=bolt://Neo4jSrv:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0

# For local development
# NEO4J_URI=bolt://localhost:7687
```

## Documentation

- [PRD](docs/PRD.md) - Product requirements
- [ADR](docs/ADR.md) - Architecture decisions
- [CHANGELOG](docs/CHANGELOG.md) - Version history
- [SchemaSync](docs/SchemaSync.md) - Data schema

## Docker Deployment

### Local Development
```bash
docker build -t tskb-rag .
docker run -p 8000:8000 --env-file .env tskb-rag
```

### Production-like Environment (TS_AI_network)
```bash
# Build image
sudo docker build -t tskb-rag .

# Run in TS_AI_network with logs and SSL volumes
sudo docker run --rm \
  --env-file /home/ubuntu/mb-env-ProdLike/test_env/.env \
  --network TS_AI_network \
  --network-alias tskb-rag \
  -v /home/ubuntu/meetingsBotLogs:/app/logs \
  -v /home/ubuntu/ssl:/app/ssl:ro \
  -p 8000:8000 \
  tskb-rag

# Or use the provided script
./build-and-run.sh
```

### Docker Compose
```bash
docker-compose up -d
```

After deployment, access:
- API: `http://localhost:8000`
- Web UI: `http://localhost:8000/promptui`

### Network Configuration
The application is configured to work with the TS_AI_network containing:
- **Neo4jSrv**: Main Neo4j database (bolt://Neo4jSrv:7687)
- **ChromaDB**: Vector database for future embeddings (ChromaDB:8000)
- **my-postgres**: PostgreSQL for future relational data (my-postgres:5432)
- **meetingsBot-main-new**: Meeting processor service
- **rag-api**: Previous RAG implementation (unused)

## Web UI Features

- **Simple Chat Interface**: Clean, responsive design
- **Real-time Queries**: Direct integration with RAG API
- **Session History**: Maintains chat history during session
- **Response Metadata**: Shows query method, data count, execution time
- **Example Queries**: Built-in suggestions for Teams Recording and business data
- **Accessibility**: Keyboard navigation and screen reader friendly

## Health Check

```bash
GET /health
```

## License

Internal TeraSky project
