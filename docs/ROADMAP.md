# TSKB-RAG Roadmap

## Current Version: 0.9.0
**Status**: Production Ready with Teams Recording Integration

---

## 🚀 Immediate Priorities (Next Release)

### Conversational Context Management
**Priority**: High  
**Estimated Effort**: 2-3 days  
**Target Version**: 1.0.0

**Problem**: Current web UI tracks visual chat history but doesn't maintain conversational context. Each query is processed independently.

**Requirements**:
- Session-based conversation memory
- Context-aware query processing
- Reference resolution (pronouns, "them", "those", etc.)
- Multi-turn conversation support

**Technical Implementation**:
- Add session management to API (`/api/v1/chat/{session_id}`)
- Conversation memory storage (in-memory or Redis)
- Context injection in query processing pipeline
- Enhanced prompt engineering for context awareness

**API Changes**:
```json
POST /api/v1/chat/{session_id}
{
  "query": "Who organized them?",
  "context_window": 3
}
```

**Web UI Changes**:
- Session ID generation and management
- Context-aware query submission
- Conversation thread display

**Success Criteria**:
- Users can ask follow-up questions referencing previous queries
- System maintains context for 5+ conversation turns
- Graceful context window management

---

## 🔮 Future Enhancements

### Vector Search Integration
**Priority**: Medium  
**Target**: v1.1.0
- ChromaDB integration for semantic search
- Hybrid Cypher + Vector retrieval
- Meeting transcript content search

### Advanced Analytics
**Priority**: Medium  
**Target**: v1.2.0
- Meeting sentiment analysis
- Action item extraction
- Meeting effectiveness metrics

### Multi-tenancy Support
**Priority**: Low  
**Target**: v2.0.0
- Organization-based data isolation
- User authentication and authorization
- Role-based access control

---

**Last Updated**: 2025-11-17  
**Next Review**: 2025-12-01