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

## Usage

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
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0
```

## Documentation

- [PRD](docs/PRD.md) - Product requirements
- [ADR](docs/ADR.md) - Architecture decisions
- [CHANGELOG](docs/CHANGELOG.md) - Version history
- [SchemaSync](docs/SchemaSync.md) - Data schema

## Docker Deployment

```bash
docker build -t tskb-rag .
docker run -p 8000:8000 --env-file .env tskb-rag
```

## Health Check

```bash
GET /health
```

## License

Internal TeraSky project
