import os
import requests
from typing import Optional, Dict, Any

class TokenValidator:
    def __init__(self):
        self.graph_url = "https://graph.microsoft.com/v1.0/me"
        self.allowed_domain = os.getenv("ALLOWED_DOMAIN", "terasky.com")
    
    async def validate_token_and_get_user(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(self.graph_url, headers=headers)
            
            if response.status_code != 200:
                return None
            
            user_data = response.json()
            email = user_data.get("mail") or user_data.get("userPrincipalName")
            
            if not email or not email.endswith(f"@{self.allowed_domain}"):
                return None
            
            return {
                "id": user_data.get("id"),
                "displayName": user_data.get("displayName"),
                "email": email
            }
        except Exception:
            return None