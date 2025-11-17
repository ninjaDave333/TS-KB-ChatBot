from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os

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

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def root():
    return {"message": "TSKB-RAG Chatbot API", "version": "0.1.0"}

@app.get("/promptui")
async def prompt_ui():
    return FileResponse("app/static/promptui.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)