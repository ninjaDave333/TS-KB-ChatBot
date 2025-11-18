import os
import msal
from typing import Optional, Dict, Any

class MSALClient:
    def __init__(self):
        self.client_id = os.getenv("MS_CLIENT_ID")
        self.client_secret = os.getenv("MS_CLIENT_SECRET")
        self.tenant_id = os.getenv("MS_TENANT_ID")
        self.redirect_uri = os.getenv("MS_REDIRECT_URI")
        
        if not all([self.client_id, self.client_secret, self.tenant_id]):
            raise ValueError("Missing required OAuth environment variables")
        
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret
        )
    
    def get_auth_url(self) -> str:
        return self.app.get_authorization_request_url(
            scopes=["User.Read"],
            redirect_uri=self.redirect_uri
        )
    
    def acquire_token_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        return self.app.acquire_token_by_authorization_code(
            code,
            scopes=["User.Read"],
            redirect_uri=self.redirect_uri
        )
    
    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret and self.tenant_id)