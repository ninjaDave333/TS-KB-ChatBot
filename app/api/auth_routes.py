from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from ..auth.msal_client import MSALClient

router = APIRouter()
msal_client = MSALClient()

@router.get("/auth/login")
async def login():
    if not msal_client.is_configured():
        raise HTTPException(status_code=400, detail={"error": "MSAL not configured"})
    
    auth_url = msal_client.get_auth_url()
    return {"authUrl": auth_url}

@router.get("/auth/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    error = request.query_params.get("error")
    
    if error:
        return HTMLResponse(f"""
            <html><body>
                <h2>Authentication Error</h2>
                <p>Error: {error}</p>
                <script>
                    if (window.opener) {{
                        window.opener.postMessage({{ error: '{error}' }}, '*');
                        window.close();
                    }}
                </script>
            </body></html>
        """)
    
    if code:
        try:
            token_response = msal_client.acquire_token_by_code(code)
            if token_response and "access_token" in token_response:
                return HTMLResponse(f"""
                    <html><body>
                        <h2>Authentication Successful</h2>
                        <script>
                            if (window.opener) {{
                                window.opener.postMessage({{ 
                                    success: true, 
                                    accessToken: '{token_response["access_token"]}',
                                    account: {{ 
                                        name: '{token_response.get("id_token_claims", {}).get("name", "")}',
                                        username: '{token_response.get("id_token_claims", {}).get("preferred_username", "")}'
                                    }}
                                }}, '*');
                                window.close();
                            }}
                        </script>
                    </body></html>
                """)
        except Exception as e:
            return HTMLResponse(f"""
                <html><body>
                    <h2>Authentication Error</h2>
                    <p>Error: {str(e)}</p>
                    <script>
                        if (window.opener) {{
                            window.opener.postMessage({{ error: 'token_processing_failed' }}, '*');
                            window.close();
                        }}
                    </script>
                </body></html>
            """)
    
    return HTMLResponse("<html><body><h2>Invalid request</h2></body></html>")