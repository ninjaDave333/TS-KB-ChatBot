import jwt
import os
from datetime import datetime
from typing import Optional, Dict, Any

class JWTValidator:
    def __init__(self):
        self.secret = os.getenv("JWT_SECRET")
        self.issuer = "meetingsBot"
        self.audience = "tskb-rag"
        
        if not self.secret:
            raise ValueError("JWT_SECRET environment variable required")
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(
                token, 
                self.secret, 
                algorithms=["HS256"],
                issuer=self.issuer,
                audience=self.audience
            )
            
            # Verify domain
            if not payload.get("domain_verified"):
                return None
                
            if not payload.get("email", "").endswith("@terasky.com"):
                return None
            
            return {
                "id": payload.get("sub"),
                "email": payload.get("email"),
                "displayName": payload.get("name"),
                "authMode": payload.get("authMode", "global"),
                "authenticated": True
            }
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None