# Centralized OAuth Architecture for TeraSky AI Services

**Date**: 2025-11-18  
**Status**: Design Phase  
**Goal**: Implement shared JWT authentication between meetingsBot and TSKB-RAG for seamless single sign-on

---

## Architecture Overview

### Current State
- **meetingsBot**: Handles OAuth on port 443 (`https://aipg.dudelabz.com`)
- **TSKB-RAG**: Separate OAuth on port 8002 (`https://aipg.dudelabz.com:8002`)
- **Problem**: Users need to authenticate twice

### Target Architecture
```
User → meetingsBot (OAuth) → JWT Token → TSKB-RAG (JWT Validation)
```

**Benefits:**
- ✅ Single sign-on experience
- ✅ Centralized authentication management
- ✅ Scalable for future AI services
- ✅ No duplicate OAuth configurations

---

## Implementation Plan

### Phase 1: meetingsBot Integration
**Responsibility**: meetingsBot team  
**Timeline**: TBD

### Phase 2: TSKB-RAG JWT Validation
**Responsibility**: TSKB-RAG team  
**Timeline**: After Phase 1 completion

### Phase 3: UI Integration & Testing
**Responsibility**: Both teams  
**Timeline**: After Phase 1 & 2

---

## meetingsBot Requirements

### 1. JWT Token Generation

**New Environment Variables:**
```env
JWT_SECRET=<shared-secret-key-32-chars>
JWT_EXPIRY=3600  # 1 hour
```

**JWT Payload Structure:**
```json
{
  "sub": "user_azure_id",
  "email": "user@terasky.com", 
  "name": "User Display Name",
  "iss": "meetingsBot",
  "aud": "tskb-rag",
  "exp": 1234567890,
  "iat": 1234567890,
  "domain_verified": true
}
```

### 2. New API Endpoint

**Endpoint**: `GET /api/generate-token`  
**Authentication**: Required (existing OAuth)  
**Purpose**: Generate JWT for authenticated users

```javascript
// NEW ENDPOINT - Does not modify existing auth flow
app.get('/api/generate-token', authenticateUser, (req, res) => {
    try {
        const payload = {
            sub: req.user.azure_id,
            email: req.user.email,
            name: req.user.displayName,
            iss: 'meetingsBot',
            aud: 'tskb-rag',
            exp: Math.floor(Date.now() / 1000) + parseInt(process.env.JWT_EXPIRY || '3600'),
            iat: Math.floor(Date.now() / 1000),
            domain_verified: req.user.email.endsWith('@terasky.com')
        };
        
        const token = jwt.sign(payload, process.env.JWT_SECRET);
        res.json({ 
            token, 
            expires_in: parseInt(process.env.JWT_EXPIRY || '3600'),
            service_url: 'https://aipg.dudelabz.com:8002/promptui'
        });
    } catch (error) {
        res.status(500).json({ error: 'Token generation failed' });
    }
});
```

### 3. UI Integration

**Add to main dashboard after login:**

```html
<!-- TSKB RAG Chat Button -->
<div class="nav-item">
    <a href="#" onclick="openTSKBRAG()" class="nav-link">
        <i class="fas fa-comments"></i>
        <span>TSKB RAG Chat</span>
    </a>
</div>
```

```javascript
async function openTSKBRAG() {
    try {
        const response = await fetch('/api/generate-token', {
            headers: {
                'Authorization': `Bearer ${getCurrentUserToken()}` // Your existing token method
            }
        });
        
        if (!response.ok) {
            throw new Error('Authentication required');
        }
        
        const { token, service_url } = await response.json();
        
        // Open TSKB-RAG with JWT token
        const url = `${service_url}?auth_token=${token}`;
        window.open(url, '_blank', 'width=1200,height=800');
        
    } catch (error) {
        console.error('Failed to access TSKB RAG:', error);
        alert('Unable to access TSKB RAG Chat. Please ensure you are logged in.');
    }
}
```

### 4. Dependencies

**Add to package.json:**
```json
{
  "jsonwebtoken": "^9.0.0"
}
```

**Import in auth module:**
```javascript
const jwt = require('jsonwebtoken');
```

---

## TSKB-RAG Implementation

### 1. JWT Validation Module

**File**: `app/auth/jwt_validator.py`

```python
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
                "authenticated": True
            }
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
```

### 2. FastAPI Dependency

**File**: `app/auth/jwt_dependencies.py`

```python
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
```

### 3. Updated Frontend

**File**: `app/static/promptui.html` (modifications)

```javascript
// Check for JWT token in URL params
const urlParams = new URLSearchParams(window.location.search);
const authToken = urlParams.get('auth_token');

if (authToken) {
    // Store token and remove from URL
    accessToken = authToken;
    currentUser = { displayName: "Authenticated User" }; // Will be populated by API call
    
    // Clean URL
    window.history.replaceState({}, document.title, window.location.pathname);
    
    // Validate token by making a test API call
    validateTokenAndUpdateUI();
} else {
    // Show authentication screen
    updateUI();
}

async function validateTokenAndUpdateUI() {
    try {
        const response = await fetch('/api/v1/health', {
            headers: { 'Authorization': `Bearer ${accessToken}` }
        });
        
        if (response.ok) {
            updateUI(); // Show authenticated interface
        } else {
            // Token invalid, show auth screen
            accessToken = null;
            currentUser = null;
            updateUI();
        }
    } catch (error) {
        // Token validation failed
        accessToken = null;
        currentUser = null;
        updateUI();
    }
}
```

### 4. Environment Variables

**Add to `.env`:**
```env
# JWT Configuration (shared with meetingsBot)
JWT_SECRET=<same-secret-as-meetingsbot>

# Remove old OAuth vars (no longer needed)
# MS_CLIENT_ID=...
# MS_CLIENT_SECRET=...
# MS_TENANT_ID=...
# MS_REDIRECT_URI=...
```

### 5. Route Updates

**File**: `app/main.py`

```python
from app.auth.jwt_dependencies import get_jwt_user

# Remove old OAuth imports
# from app.auth.dependencies import get_current_user

# Update protected routes
@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, user: dict = Depends(get_jwt_user)):
    # Existing logic unchanged
    pass
```

---

## Security Considerations

### JWT Security
- **Secret Key**: 32+ character random string, shared securely
- **Expiration**: 1 hour maximum (configurable)
- **Domain Validation**: Only `@terasky.com` users
- **Audience**: Specific to `tskb-rag` service

### Token Transmission
- **HTTPS Only**: All token transmission over encrypted connections
- **URL Params**: Tokens in URL are immediately moved to memory/storage
- **No Logging**: Tokens excluded from access logs

### Error Handling
- **Expired Tokens**: Redirect to meetingsBot for re-authentication
- **Invalid Tokens**: Clear error messages, no sensitive data exposure
- **Rate Limiting**: Prevent token brute force attacks

---

## Testing Plan

### Phase 1: meetingsBot Testing
1. **Token Generation**: Verify `/api/generate-token` endpoint
2. **JWT Structure**: Validate payload format and signing
3. **Expiration**: Test token expiry behavior
4. **Domain Validation**: Ensure only `@terasky.com` users get tokens

### Phase 2: TSKB-RAG Testing
1. **Token Validation**: Test JWT validation logic
2. **API Protection**: Verify protected endpoints require valid tokens
3. **Frontend Integration**: Test URL token handling
4. **Error Scenarios**: Invalid/expired token handling

### Phase 3: Integration Testing
1. **End-to-End Flow**: meetingsBot → JWT → TSKB-RAG access
2. **Cross-Browser**: Test popup/redirect behavior
3. **Token Refresh**: Test re-authentication flow
4. **Performance**: Measure authentication overhead

---

## Rollback Plan

### If Issues Arise
1. **meetingsBot**: Remove `/api/generate-token` endpoint and UI button
2. **TSKB-RAG**: Revert to original OAuth implementation
3. **Environment**: Restore original OAuth environment variables
4. **DNS**: No changes required (services remain on same ports)

### Rollback Triggers
- Authentication failures > 5%
- Performance degradation > 200ms
- User complaints about login experience
- Security concerns identified

---

## Migration Timeline

### Week 1: meetingsBot Implementation
- [ ] Add JWT dependencies
- [ ] Implement `/api/generate-token` endpoint
- [ ] Add UI integration
- [ ] Internal testing

### Week 2: TSKB-RAG Implementation  
- [ ] Implement JWT validation
- [ ] Update route protection
- [ ] Modify frontend for token handling
- [ ] Internal testing

### Week 3: Integration & Testing
- [ ] End-to-end testing
- [ ] User acceptance testing
- [ ] Performance validation
- [ ] Security review

### Week 4: Production Deployment
- [ ] Deploy meetingsBot changes
- [ ] Deploy TSKB-RAG changes
- [ ] Monitor authentication metrics
- [ ] User feedback collection

---

## Success Metrics

### User Experience
- **Single Sign-On**: 100% of users authenticate once
- **Access Time**: < 3 seconds from meetingsBot to TSKB-RAG
- **Error Rate**: < 1% authentication failures

### Technical Metrics
- **Token Generation**: < 100ms response time
- **Token Validation**: < 50ms response time
- **Uptime**: 99.9% availability maintained

### Security Metrics
- **Domain Compliance**: 100% `@terasky.com` validation
- **Token Expiry**: No expired tokens accepted
- **Audit Trail**: All authentication events logged

---

## Future Enhancements

### Additional Services
- Easy integration pattern for new AI services
- Centralized user management
- Service discovery and routing

### Advanced Features
- Token refresh without re-authentication
- Role-based access control (RBAC)
- Service-specific permissions
- Audit logging and monitoring

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-18  
**Next Review**: After Phase 1 completion

---

## Prompt for meetingsBot Team

**Subject**: TSKB-RAG Integration - Shared JWT Authentication Implementation

Hi meetingsBot team,

We need to integrate our TSKB-RAG chatbot with your OAuth system using shared JWT tokens. This will provide seamless single sign-on for users accessing both services.

### Critical Requirements
- **NO BREAKING CHANGES**: All existing meetingsBot functionality must remain unchanged
- **Additive Only**: We're adding new features, not modifying existing auth flows
- **Backward Compatible**: Current users experience no disruption

### Implementation Request

#### 1. Add JWT Token Generation
**New endpoint**: `GET /api/generate-token`
- Requires existing authentication (your current OAuth)
- Generates JWT token for TSKB-RAG access
- 1-hour expiration, `@terasky.com` domain validation

#### 2. Dependencies
```bash
npm install jsonwebtoken@^9.0.0
```

#### 3. Environment Variables
```env
JWT_SECRET=<32-char-random-string>  # We'll provide this
JWT_EXPIRY=3600
```

#### 4. Code Implementation
Please see the detailed code examples in sections above:
- JWT payload structure (section 1)
- API endpoint implementation (section 2)  
- UI integration (section 3)

#### 5. UI Enhancement (Optional)
Add "TSKB RAG Chat" button to main dashboard that:
- Generates JWT token via new endpoint
- Opens TSKB-RAG in new tab with token
- Provides seamless user experience

### What We Handle
- JWT validation on TSKB-RAG side
- Token security and expiration
- Error handling for invalid tokens
- User session management in TSKB-RAG

### Testing & Rollback
- We'll test thoroughly before production
- Easy rollback: just remove the new endpoint
- No impact on existing meetingsBot functionality

### Timeline
- **Week 1**: meetingsBot implementation
- **Week 2**: TSKB-RAG integration  
- **Week 3**: Testing and validation

### Questions
1. Can you implement the `/api/generate-token` endpoint?
2. What's your `req.user` object structure for JWT payload?
3. When can we schedule implementation?
4. Any concerns about this approach?

This integration will create a unified AI platform experience while maintaining all existing functionality and security standards.

Please let us know your thoughts and availability for this integration.

Best regards,  
TSKB-RAG Team