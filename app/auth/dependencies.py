from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .token_validator import TokenValidator
from typing import Dict, Any

security = HTTPBearer()
token_validator = TokenValidator()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    user = await token_validator.validate_token_and_get_user(credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Token validation failed",
                "code": "TOKEN_VALIDATION_FAILED"
            }
        )
    return user