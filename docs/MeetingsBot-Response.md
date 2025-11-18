# meetingsBot Team Implementation Response

**Date**: 2025-11-18  
**From**: meetingsBot Team  
**To**: TSKB-RAG Team  
**Status**: ✅ APPROVED - Ready for Implementation

---

## Executive Summary

The meetingsBot team has **approved the centralized OAuth architecture** and provided complete implementation details. All technical requirements are confirmed and ready for immediate implementation.

### Key Approvals:
- ✅ **Architecture**: Centralized JWT approach approved
- ✅ **Non-Breaking**: All changes are additive only
- ✅ **Timeline**: 1-2 days for meetingsBot implementation
- ✅ **Security**: Domain validation and JWT security confirmed
- ✅ **Complete Code**: Full implementation provided

---

## Technical Specifications Confirmed

### 1. JWT Payload Structure
```json
{
  "sub": "user_azure_id",
  "email": "user@terasky.com", 
  "name": "User Display Name",
  "authMode": "global",
  "iss": "meetingsBot",
  "aud": "tskb-rag",
  "exp": 1234567890,
  "iat": 1234567890,
  "domain_verified": true
}
```

### 2. User Object Mapping
```javascript
req.user = {
  id: "azure_user_id_string",           // → JWT sub field
  displayName: "User Display Name",     // → JWT name field  
  email: "user@terasky.com",           // → JWT email field
  authenticatedAt: "2025-01-15T10:30:00.000Z"
}

req.authMode = "global"                 // → JWT authMode field
```

### 3. Environment Variables
```env
JWT_SECRET=<64-char-hex-string>  # Generated via crypto.randomBytes(32).toString('hex')
JWT_EXPIRY=3600  # 1 hour
TSKB_RAG_URL=https://aipg.dudelabz.com:8002/promptui
```

**JWT Secret Generation:**
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

---

## Complete Implementation Code

### 1. AuthenticationMiddleware Enhancement
```javascript
const jwt = require('jsonwebtoken');

class AuthenticationMiddleware {
  // ... existing methods ...

  /**
   * Generate JWT token for authenticated users
   * Uses existing user context from authenticateUser middleware
   */
  generateJWT = (req, res) => {
    try {
      // Validate JWT configuration
      if (!process.env.JWT_SECRET) {
        return res.status(500).json({
          error: 'JWT not configured',
          message: 'JWT_SECRET environment variable is required'
        });
      }

      // User should already be authenticated by authenticateUser middleware
      if (!req.user) {
        return res.status(401).json({
          error: 'Authentication required',
          message: 'User must be authenticated to generate JWT'
        });
      }

      const payload = {
        sub: req.user.id,                    // Azure user ID
        email: req.user.email,               // User email
        name: req.user.displayName,          // Display name
        authMode: req.authMode || 'global',  // Auth mode (always global)
        iss: 'meetingsBot',
        aud: 'tskb-rag',
        exp: Math.floor(Date.now() / 1000) + parseInt(process.env.JWT_EXPIRY || '3600'),
        iat: Math.floor(Date.now() / 1000),
        domain_verified: req.user.email.endsWith('@terasky.com')
      };

      const token = jwt.sign(payload, process.env.JWT_SECRET);
      
      // Log JWT generation
      const logger = req.app?.get('logger');
      if (logger) {
        logger.logUserAction('jwt_generated', {
          userId: req.user.id,
          userEmail: req.user.email,
          targetService: 'tskb-rag',
          clientIp: req.ip
        });
      }

      res.json({
        token,
        expires_in: parseInt(process.env.JWT_EXPIRY || '3600'),
        service_url: process.env.TSKB_RAG_URL || 'https://aipg.dudelabz.com:8002/promptui'
      });
    } catch (error) {
      console.error('JWT generation error:', error);
      res.status(500).json({
        error: 'Token generation failed',
        message: error.message
      });
    }
  };
}
```

### 2. Server Route Integration
```javascript
// Add JWT dependency
const jwt = require('jsonwebtoken');

// JWT token generation endpoint
app.get('/api/generate-token', auth.authenticateUser, (req, res) => {
  // Use the new generateJWT method from middleware
  const authInstance = new (require('./middleware/auth').constructor)();
  authInstance.generateJWT(req, res);
});
```

### 3. UI Integration (Vue.js)
```html
<!-- Add TSKB RAG button after existing nav items -->
<div class="nav-section" v-if="msUser">
    <button class="btn btn-primary" @click="openTSKBRAG" style="margin: 10px;">
        💬 TSKB RAG Chat
    </button>
</div>
```

```javascript
// Add to existing Vue.js methods
methods: {
  // ... existing methods ...
  
  async openTSKBRAG() {
    try {
      console.log('🔗 Opening TSKB RAG Chat...');
      
      const response = await fetch('/api/generate-token', {
        headers: {
          'Authorization': `Bearer ${this.msAccessToken}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate access token');
      }
      
      const { token, service_url } = await response.json();
      
      // Open TSKB-RAG with JWT token
      const url = `${service_url}?auth_token=${token}`;
      window.open(url, '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
      
      console.log('✅ TSKB RAG Chat opened successfully');
      
    } catch (error) {
      console.error('❌ Failed to open TSKB RAG:', error);
      alert('Unable to access TSKB RAG Chat. Please ensure you are logged in.');
    }
  }
}
```

### 4. Dependencies
```json
{
  "dependencies": {
    "jsonwebtoken": "^9.0.0"
  }
}
```

```bash
npm install jsonwebtoken@^9.0.0
```

---

## Testing Strategy

### Phase 1a: JWT Generation Testing
```bash
# Dev Environment
GET https://dev.aipg.dudelabz.com/api/generate-token
Authorization: Bearer <existing_ms365_token>

# Expected Response
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600,
  "service_url": "https://aipg.dudelabz.com:8002/promptui"
}
```

### Testing Process
1. **Phase 1a**: Implement JWT generation endpoint
2. **Phase 1b**: Test with Postman/curl using existing MS365 tokens
3. **Phase 1c**: Validate JWT payload structure
4. **Phase 2**: TSKB-RAG implements JWT validation
5. **Phase 3**: End-to-end testing

---

## Security Considerations

### Token Security
- **Transmission**: HTTPS only
- **Storage**: Temporary (URL params → memory → cleared)
- **Expiration**: 1 hour maximum
- **Validation**: Domain + issuer + audience checks

### Error Handling
```javascript
// Standard error responses
{
  error: 'JWT not configured',
  message: 'JWT_SECRET environment variable is required'
}

{
  error: 'Token generation failed', 
  message: 'Specific error details'
}
```

---

## Implementation Checklist

### meetingsBot Tasks ✅ READY
- [ ] Add `jsonwebtoken` dependency
- [ ] Add JWT environment variables
- [ ] Implement `generateJWT` method in auth middleware
- [ ] Add `/api/generate-token` route
- [ ] Add UI button for TSKB RAG access
- [ ] Test JWT generation endpoint
- [ ] Validate JWT payload structure

### TSKB-RAG Tasks (Next Phase)
- [ ] Implement JWT validation module
- [ ] Replace OAuth dependencies with JWT validation
- [ ] Update frontend to handle JWT tokens from URL params
- [ ] Test token validation and user context
- [ ] Update route protection

### Coordination Tasks
- [ ] Generate and share JWT_SECRET securely
- [ ] Coordinate testing timeline
- [ ] Test end-to-end flow
- [ ] Monitor authentication logs
- [ ] Document any issues/resolutions

---

## Implementation Timeline

### Immediate Actions
1. **Today**: Generate JWT_SECRET and share securely
2. **Day 1**: meetingsBot implements JWT generation
3. **Day 2**: Test JWT endpoint with existing auth
4. **Day 3**: TSKB-RAG implements JWT validation
5. **Day 4**: End-to-end testing
6. **Day 5**: UI integration and go-live

### Success Criteria
- ✅ JWT generation endpoint working
- ✅ Valid JWT tokens with correct payload
- ✅ Domain validation enforced
- ✅ UI integration seamless
- ✅ End-to-end authentication flow working

---

## Next Steps

**Ready to proceed immediately with:**

1. **Generate JWT_SECRET** using provided crypto method
2. **Share secret securely** between teams
3. **Begin meetingsBot implementation** (1-2 days)
4. **Prepare TSKB-RAG JWT validation** (parallel development)
5. **Coordinate testing** once both sides ready

**Contact**: meetingsBot team ready to start implementation upon JWT_SECRET confirmation.

---

**Document Status**: ✅ Complete - All implementation details confirmed  
**Next Action**: Generate JWT_SECRET and begin implementation  
**Timeline**: 5 days to full production deployment