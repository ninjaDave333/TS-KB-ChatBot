#!/usr/bin/env python3
import os
import uvicorn

def main():
    # SSL configuration
    ssl_cert = "/app/ssl/cert.pem"
    ssl_key = "/app/ssl/key.pem"
    port = 8002
    
    print(f"\n🔍 Checking SSL certificates...")
    print(f"Cert: {ssl_cert} - Exists: {os.path.exists(ssl_cert)}")
    print(f"Key: {ssl_key} - Exists: {os.path.exists(ssl_key)}")
    
    if os.path.exists(ssl_cert) and os.path.exists(ssl_key):
        print(f"✅ SSL certificates found - Starting HTTPS server on port {port}")
        print(f"🔐 OAuth ready at https://localhost:{port}/promptui")
        uvicorn.run("app.main:app", host="0.0.0.0", port=port, 
                   ssl_certfile=ssl_cert, ssl_keyfile=ssl_key)
    else:
        print(f"❌ SSL certificates not found - Starting HTTP server")
        print(f"⚠️  OAuth will NOT work without HTTPS")
        uvicorn.run("app.main:app", host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()