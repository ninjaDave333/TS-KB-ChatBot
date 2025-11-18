from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os

# Load environment variables first
load_dotenv()

from app.api.routes import router
from app.api.auth_routes import router as auth_router
from app.auth.dependencies import get_current_user

app = FastAPI(
    title="TSKB-RAG Chatbot",
    description="Natural language interface to TSKB Neo4j knowledge graph",
    version="0.1.0"
)

# Include API routes
app.include_router(router, prefix="/api/v1")
app.include_router(auth_router)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def root():
    return {"message": "TSKB-RAG Chatbot API", "version": "0.1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.1.0"}

@app.get("/promptui")
async def prompt_ui(user: dict = Depends(get_current_user)):
    return FileResponse("app/static/promptui.html")

if __name__ == "__main__":
    import uvicorn
    import os
    
    # SSL configuration for OAuth (required for HTTPS)
    ssl_cert = os.getenv("SSL_CERT_PATH", "/app/ssl/cert.pem")
    ssl_key = os.getenv("SSL_KEY_PATH", "/app/ssl/key.pem")
    https_port = int(os.getenv("HTTPS_PORT", "8002"))
    
    print(f"Checking SSL certificates: {ssl_cert}, {ssl_key}")
    print(f"SSL cert exists: {os.path.exists(ssl_cert)}")
    print(f"SSL key exists: {os.path.exists(ssl_key)}")
    
    if os.path.exists(ssl_cert) and os.path.exists(ssl_key):
        print(f"Starting HTTPS server on port {https_port} with SSL certificates")
        uvicorn.run(app, host="0.0.0.0", port=https_port, 
                   ssl_certfile=ssl_cert, ssl_keyfile=ssl_key)
    else:
        print(f"SSL certificates not found at {ssl_cert} and {ssl_key}")
        print("Starting HTTP server - OAuth will not work without HTTPS")
        uvicorn.run(app, host="0.0.0.0", port=https_port)