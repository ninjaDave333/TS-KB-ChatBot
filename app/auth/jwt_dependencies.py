from fastapi import HTTPException, Depends, status, Request
from .jwt_validator import JWTValidator
from typing import Dict, Any

jwt_validator = JWTValidator()

async def get_jwt_user(request: Request) -> Dict[str, Any]:
    # Check for token in query params (from meetingsBot redirect)
    token = request.query_params.get("auth_token")
    
    # Check for token in Authorization header (for API calls)
    if not token:
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Authentication required", "code": "MISSING_TOKEN"}
        )
    
    user = jwt_validator.validate_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid or expired token", "code": "INVALID_TOKEN"}
        )
    
    return user