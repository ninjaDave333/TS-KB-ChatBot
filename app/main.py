from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os
import logging

# Load environment variables first
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.api.routes import router
from app.api.auth_routes import router as auth_router
from app.auth.dependencies import get_current_user

app = FastAPI(
    title="TSKB-RAG Chatbot",
    description="Natural language interface to TSKB Neo4j knowledge graph",
    version="0.1.0"
)

@app.on_event("startup")
async def startup_event():
    ssl_cert = os.getenv("SSL_CERT_PATH", "/app/ssl/cert.pem")
    ssl_key = os.getenv("SSL_KEY_PATH", "/app/ssl/key.pem")
    
    print(f"\n=== SSL Certificate Check ===")
    print(f"Cert path: {ssl_cert}")
    print(f"Key path: {ssl_key}")
    print(f"Cert exists: {os.path.exists(ssl_cert)}")
    print(f"Key exists: {os.path.exists(ssl_key)}")
    
    if os.path.exists(ssl_cert) and os.path.exists(ssl_key):
        print("✅ SSL certificates loaded successfully")
        print("✅ SSL OK - HTTPS ready for OAuth compatibility")
        logger.info("SSL certificates loaded successfully - OAuth ready")
    else:
        print("❌ SSL certificates not found")
        print("❌ OAuth will not work without HTTPS certificates")
        logger.error(f"SSL certificates missing - OAuth disabled")
    print(f"==============================\n")

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
    return {"status": "healthy", "version": "1.1.0", "ssl": "enabled" if os.path.exists("/app/ssl/cert.pem") else "disabled"}

@app.get("/promptui")
async def prompt_ui():
    return FileResponse("app/static/promptui.html")

if __name__ == "__main__":
    import uvicorn
    import os
    
    # SSL configuration for OAuth (required for HTTPS)
    ssl_cert = "/app/ssl/cert.pem"
    ssl_key = "/app/ssl/key.pem"
    port = 8002
    
    print(f"\n🔍 Checking SSL certificates...")
    print(f"Cert: {ssl_cert} - Exists: {os.path.exists(ssl_cert)}")
    print(f"Key: {ssl_key} - Exists: {os.path.exists(ssl_key)}")
    
    if os.path.exists(ssl_cert) and os.path.exists(ssl_key):
        print(f"✅ SSL certificates found - Starting HTTPS server on port {port}")
        print(f"🔐 OAuth ready at https://localhost:{port}/promptui")
        uvicorn.run(app, host="0.0.0.0", port=port, 
                   ssl_certfile=ssl_cert, ssl_keyfile=ssl_key)
    else:
        print(f"❌ SSL certificates not found - Starting HTTP server")
        print(f"⚠️  OAuth will NOT work without HTTPS")
        uvicorn.run(app, host="0.0.0.0", port=port)