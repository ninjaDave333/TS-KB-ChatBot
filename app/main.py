from fastapi import FastAPI
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from app.api.routes import router

app = FastAPI(
    title="TSKB-RAG Chatbot",
    description="Natural language interface to TSKB Neo4j knowledge graph",
    version="0.1.0"
)

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "TSKB-RAG Chatbot API", "version": "0.1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)