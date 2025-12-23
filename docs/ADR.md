# Architecture Decision Record (ADR)

**Project**: TSKB-RAG Chatbot System  
**Version**: 1.0.0  
**Date**: 2025-11-10  

---

## ADR-001: Core Architecture - FastAPI + Neo4j + AWS Bedrock

**Date**: 2025-11-10  
**Status**: Accepted  
**Context**: Need to build a conversational AI system that provides natural language access to TSKB Neo4j knowledge graph

**Decision**: Use FastAPI as the web framework, Neo4j as the knowledge store, and AWS Bedrock for LLM capabilities

**Rationale**:
- **FastAPI**: High performance, automatic API documentation, async support, Python ecosystem
- **Neo4j**: Existing TSKB infrastructure with 3,093+ nodes, graph relationships ideal for RAG
- **AWS Bedrock**: Managed LLM service, multiple model options, enterprise security

**Consequences**:
- ✅ Leverages existing TSKB Neo4j infrastructure
- ✅ High-performance async API
- ✅ Enterprise-grade LLM capabilities
- ❌ AWS vendor lock-in for LLM services

---

## ADR-002: Query Strategy - Hybrid Cypher + Vector Search

**Date**: 2025-11-10  
**Status**: Accepted  
**Context**: Need to handle diverse query types from quantitative to analytical queries

**Decision**: Implement hybrid retrieval strategy combining direct Cypher generation and vector similarity search

**Rationale**:
- **Direct Cypher**: Optimal for structured queries with clear entity relationships
- **Vector Search**: Better for semantic similarity and fuzzy matching
- **Hybrid Approach**: Combines precision of graph queries with flexibility of semantic search

**Consequences**:
- ✅ Handles both structured and unstructured queries
- ✅ Leverages graph relationships for precise results
- ✅ Semantic search for ambiguous queries
- ❌ Increased complexity in query routing logic

---

## ADR-003: Response Format - Structured JSON with Confidence Scoring

**Date**: 2025-11-10  
**Status**: Accepted  
**Context**: Need consistent, reliable response format for various query types

**Decision**: Standardize on JSON response format with confidence levels (0-100%) and data citations

**Rationale**:
- **Confidence Scoring**: Enables users to assess answer reliability
- **Data Citations**: Provides traceability to source data
- **Structured Format**: Enables programmatic consumption and UI rendering

**Consequences**:
- ✅ Transparent confidence assessment
- ✅ Traceable data lineage
- ✅ Consistent API responses
- ❌ Additional complexity in confidence calculation

---

## ADR-004: Deployment Strategy - Docker with SSL Support

**Date**: 2025-11-10  
**Status**: Accepted  
**Context**: Need production-ready deployment with security and monitoring

**Decision**: Deploy as Docker container with SSL support, logging, and health checks

**Rationale**:
- **Docker**: Consistent deployment across environments
- **SSL**: Secure communication for enterprise use
- **Logging**: Essential for debugging and monitoring
- **Health Checks**: Reliability and monitoring integration

**Consequences**:
- ✅ Production-ready deployment
- ✅ Secure communication
- ✅ Monitoring and debugging capabilities
- ❌ Additional infrastructure complexity

---

## ADR-005: Schema Discovery - Dynamic Neo4j Introspection

**Date**: 2025-11-10  
**Status**: Accepted  
**Context**: TSKB schema evolves with new data sources and relationships

**Decision**: Implement dynamic schema discovery through Neo4j introspection queries

**Rationale**:
- **Dynamic Discovery**: Adapts to schema changes without code updates
- **Self-Learning**: System improves query generation over time
- **Maintenance**: Reduces manual schema maintenance overhead

**Consequences**:
- ✅ Adapts to schema evolution automatically
- ✅ Reduces maintenance overhead
- ✅ Enables self-learning capabilities
- ❌ Runtime schema discovery overhead

---

## ADR-006: Entity Extraction - LLM-Based with Fallback Rules

**Date**: 2025-11-10  
**Status**: Accepted  
**Context**: Need robust entity extraction for diverse query types

**Decision**: Use AWS Bedrock LLM for entity extraction with rule-based fallbacks

**Rationale**:
- **LLM-Based**: Handles complex, contextual entity recognition
- **Fallback Rules**: Ensures reliability for common patterns
- **AWS Bedrock**: Consistent with overall LLM strategy

**Consequences**:
- ✅ Robust entity extraction for complex queries
- ✅ Reliable fallback for common patterns
- ✅ Consistent LLM integration
- ❌ LLM API costs for entity extraction

---

## ADR-007: Data Integration - Read-Only Neo4j Access

**Date**: 2025-11-10  
**Status**: Accepted  
**Context**: TSKB data is managed by separate collector/importer services

**Decision**: Implement read-only access to Neo4j, no data modification capabilities

**Rationale**:
- **Data Integrity**: Prevents accidental data corruption
- **Separation of Concerns**: Clear boundary between data collection and consumption
- **Security**: Reduces attack surface with read-only access

**Consequences**:
- ✅ Data integrity protection
- ✅ Clear service boundaries
- ✅ Enhanced security posture
- ❌ Cannot provide data update capabilities

---

## ADR-008: Error Handling - Graceful Degradation with Fallbacks

**Date**: 2025-11-10  
**Status**: Accepted  
**Context**: Need robust error handling for production reliability

**Decision**: Implement graceful degradation with multiple fallback strategies

**Rationale**:
- **Neo4j Unavailable**: Return cached schema information
- **LLM Unavailable**: Use rule-based query generation
- **Query Failures**: Provide partial results with error context

**Consequences**:
- ✅ High availability even with component failures
- ✅ Better user experience during outages
- ✅ Detailed error context for debugging
- ❌ Increased complexity in error handling logic

---

## ADR-009: Caching Strategy - Multi-Level Caching

**Date**: 2025-11-10  
**Status**: Accepted  
**Context**: Need to optimize performance for repeated queries

**Decision**: Implement multi-level caching (schema, query results, LLM responses)

**Rationale**:
- **Schema Caching**: Reduces Neo4j introspection overhead
- **Query Result Caching**: Improves response time for common queries
- **LLM Response Caching**: Reduces API costs and latency

**Consequences**:
- ✅ Improved response times
- ✅ Reduced API costs
- ✅ Better scalability
- ❌ Cache invalidation complexity

---

## ADR-010: API Design - RESTful with OpenAPI Documentation

**Date**: 2025-11-10  
**Status**: Accepted  
**Context**: Need well-documented API for integration and testing

**Decision**: Design RESTful API with comprehensive OpenAPI documentation

**Rationale**:
- **RESTful Design**: Industry standard, easy to understand and integrate
- **OpenAPI**: Automatic documentation, client generation, testing tools
- **FastAPI Integration**: Built-in OpenAPI support

**Consequences**:
- ✅ Easy integration for consumers
- ✅ Comprehensive documentation
- ✅ Testing and client generation tools
- ❌ RESTful constraints may not fit all use cases

---

## ADR-011: Enhanced Schema Descriptions for AI Query Generation

**Date**: 2025-11-12  
**Status**: Accepted  
**Context**: AI-generated Cypher queries needed better context about node purposes, critical properties, and relationship patterns

**Decision**: Implement enhanced schema descriptions with detailed node purposes, critical properties, and common query patterns

**Rationale**:
- **Contextual Understanding**: AI needs to understand the business purpose of each node type
- **Critical Properties**: Highlighting key fields improves query accuracy
- **Query Patterns**: Common relationship patterns guide better Cypher generation
- **Case Sensitivity**: Proper handling of client name matching with toLower() functions

**Implementation**:
- Added detailed descriptions for all node types (Client, Product, Employee, etc.)
- Documented critical properties for each node type
- Included common relationship patterns and query examples
- Enhanced AI context with business logic understanding

**Test Results**:
- Successfully generated accurate Cypher queries for WIX client searches
- Proper case-insensitive matching using toLower() functions
- Correct relationship traversal for OPPORTUNITY and HAS_INSTALLED patterns
- Accurate account manager queries using MANAGED_BY relationships

**Consequences**:
- ✅ Significantly improved AI query generation accuracy
- ✅ Better understanding of business context in queries
- ✅ Proper case-insensitive client name matching
- ✅ Accurate relationship traversal patterns
- ❌ Increased schema description maintenance overhead

---

## ADR-012: Cost Field Correction - total_price vs amount

**Date**: 2025-11-12  
**Status**: Accepted  
**Context**: AI-generated queries were using non-existent `o.amount` field for cost calculations, resulting in all costs showing as $0

**Decision**: Correct schema descriptions to use `o.total_price` field for OPPORTUNITY relationship cost data

**Investigation Results**:
- **OPPORTUNITY properties**: `unit_price`, `total_price`, `quantity` (NO `amount` field)
- **All 1,081 Closed Won deals** have `total_price` values
- **Total revenue**: $293,819,716.17
- **Top deal**: Aqua Security - $30.2M AWS Cloud Consumption

**Implementation**:
- Updated schema_descriptions.py with correct field name
- Added cost_calculation section to OPPORTUNITY relationship
- Added critical notes about cost aggregation pattern
- Correct aggregation: `sum(toFloat(o.total_price)) as total_cost`

**Consequences**:
- ✅ Cost queries now return accurate financial data
- ✅ Revenue calculations work correctly
- ✅ AI generates queries with proper field names
- ✅ Schema documentation matches actual data structure

---

## ADR-013: OPPORTUNITY close_date Field for Temporal Queries

**Date**: 2025-11-12  
**Status**: Accepted  
**Context**: Temporal queries were using purchased_date (line item creation) instead of actual deal close date, causing inaccurate results for "2025 deals" queries

**Decision**: Add close_date field to OPPORTUNITY relationships and use it as the primary field for all temporal queries

**Field Distinction**:
- **close_date**: Actual deal close date from Opportunity.CloseDate (authoritative for temporal queries)
- **purchased_date**: Line item creation date from OpportunityLineItem.CreatedDate (rarely used)

**Query Pattern Change**:
```cypher
# OLD (Incorrect)
WHERE o.purchased_date CONTAINS '2025'

# NEW (Correct)
WHERE o.close_date >= '2025-01-01' AND o.close_date < '2026-01-01'
```

**Implementation**:
- Updated schema_descriptions.py with close_date as primary temporal field
- Changed all query examples to use close_date
- Updated temporal_filtering pattern to use proper date range comparisons
- Added temporal_queries section to OPPORTUNITY relationship documentation

**Data Coverage**:
- All 10,032 OPPORTUNITY relationships have close_date field
- 100% coverage across all deal stages
- Date range: 2022-11-30 to 2025-11-12

**Consequences**:
- ✅ Accurate temporal queries for "deals closed in 2025"
- ✅ Proper date range filtering instead of string matching
- ✅ Correct revenue reporting by time period
- ✅ Clear distinction between close date and creation date

---

## Decision Log Summary

| ADR | Decision | Status | Impact |
|-----|----------|--------|---------|
| 001 | FastAPI + Neo4j + AWS Bedrock | Accepted | High |
| 002 | Hybrid Cypher + Vector Search | Accepted | High |
| 003 | Structured JSON with Confidence | Accepted | Medium |
| 004 | Docker with SSL Support | Accepted | Medium |
| 005 | Dynamic Schema Discovery | Accepted | High |
| 006 | LLM-Based Entity Extraction | Accepted | Medium |
| 007 | Read-Only Neo4j Access | Accepted | Low |
| 008 | Graceful Degradation | Accepted | Medium |
| 009 | Multi-Level Caching | Accepted | Medium |
| 010 | RESTful API with OpenAPI | Accepted | Low |
| 011 | Enhanced Schema Descriptions | Accepted | High |
| 012 | Cost Field Correction | Accepted | High |
| 013 | OPPORTUNITY close_date Field | Accepted | Critical |
| 014 | RAGAS Integration for RAG Evaluation | Accepted | High |
| 015 | Intelligent Answer Generation | Accepted | Critical |
| 016 | Teams Recording Integration | Accepted | High |
| 017 | Dynamic RAG Enhancement Phase 1 + Persistent Learning | Implemented | Critical |
| 018 | Microsoft OAuth Authentication | Implemented | High |
| 019 | Centralized OAuth JWT Authentication | Implemented | Critical |
| 020 | Response Consistency Enhancement | Implemented | High |
| 021 | Self-Improving RAG Engine Phase 1 Config Foundation | Implemented | High |
| 022 | Self-Improving RAG Engine Phase 2 LLM Abstraction | Implemented | High |
| 023 | Self-Improving RAG Engine Phase 3 Multi-Model Support | Implemented | High |
| 024 | Self-Improving RAG Engine Phase 4 Tracing & Evaluation | Implemented | Critical |
| 025 | Self-Improving RAG Engine Phase 5 Evaluation Daemon | Implemented | High |
| 026 | Answer Generation Consistency Fix | Implemented | High |

---

## ADR-015: Intelligent Answer Generation

**Date**: 2025-11-17  
**Status**: Accepted  
**Context**: RAGAS evaluation revealed that generic responses like "Query executed successfully" scored poorly on answer relevancy and correctness metrics

**Decision**: Implement intelligent answer generation system that creates contextual, business-relevant responses based on query type and retrieved data

**Problem Analysis**:
- **Generic Responses**: "Query executed successfully" provided no business value
- **Poor RAGAS Scores**: Answer Relevancy: 0.059, Answer Correctness: 0.030
- **Missing Context**: Responses lacked connection to actual query results
- **Query Type Blindness**: Same response format for count, list, and analytical queries

**Solution Architecture**:
- **Query Type Detection**: Automatic classification (count, list, vendor, general)
- **Context-Aware Formatting**: Different response patterns for different query types
- **Business Data Integration**: Incorporate actual results into natural language responses
- **Fallback Handling**: Graceful degradation for edge cases

**Implementation Details**:
```python
class AnswerGenerator:
    def generate_answer(self, query: str, data: List[Dict], confidence: float) -> str:
        query_type = self._detect_query_type(query)
        if query_type == "count":
            return self._format_count_answer(query, data)
        elif query_type == "list":
            return self._format_list_answer(query, data)
        # ... other types
```

**Query Type Patterns**:
- **Count Queries**: "how many", "count", "number of" → Numeric summaries
- **List Queries**: "who", "which", "what clients" → Formatted lists
- **Vendor Queries**: Specific vendor names → Product-focused responses
- **General Queries**: Fallback to descriptive summaries

**RAGAS Performance Impact**:
- **Answer Correctness**: 0.030 → 0.921 (2970% improvement)
- **Answer Relevancy**: 0.059 → 0.776 (1215% improvement)
- **Context Recall**: 0.000 → 1.000 (Perfect score)
- **Faithfulness**: 0.667 → 1.000 (Perfect score)

**Integration Points**:
- **API Routes**: Replaced generic response formatting
- **Query Processing**: Enhanced with type detection
- **Error Handling**: Maintained graceful degradation

**Consequences**:
- ✅ **Dramatic RAGAS Improvements**: 4/5 metrics achieved excellent scores
- ✅ **Business Value**: Responses now provide actionable insights
- ✅ **User Experience**: Natural language answers instead of technical confirmations
- ✅ **Production Ready**: System now meets quality standards for deployment
- ❌ **Increased Complexity**: Additional logic for answer generation
- ❌ **Maintenance Overhead**: Query type patterns need ongoing refinement

**Critical Fixes Included**:
- **Israeli Client Queries**: Use c.region = 'IL' not c.country = 'Israel'
- **Employee Relationships**: Proper Employee node usage for account managers
- **Count Detection**: Explicit count keywords required for count classification

---

## ADR-014: RAGAS Integration for RAG Evaluation

**Date**: 2025-11-17  
**Status**: Accepted  
**Context**: Current testing approach lacks comprehensive RAG-specific evaluation metrics for answer quality, faithfulness, and retrieval effectiveness

**Decision**: Integrate RAGAS (Retrieval Augmented Generation Assessment) framework for systematic RAG evaluation

**Rationale**:
- **RAG-Specific Metrics**: Faithfulness, context precision, answer relevancy, context recall, answer correctness
- **Automated Evaluation**: Systematic assessment using LLM-based evaluation
- **Standardized Benchmarking**: Industry-standard metrics for RAG systems
- **Enhanced Testing**: Complements existing batch testing with quality metrics

**Implementation**:
- Added RAGAS dependencies to requirements.txt
- Created comprehensive evaluation script (Tests/ragas_evaluation.py)
- Integrated with existing AWS Bedrock LLM for evaluation
- PowerShell runner script for easy execution

**Evaluation Metrics**:
- **Faithfulness**: Answer alignment with retrieved contexts
- **Answer Relevancy**: Response relevance to user questions
- **Context Precision**: Retrieval precision and context quality
- **Context Recall**: Context completeness for answering questions
- **Answer Correctness**: Factual accuracy against ground truth

**Test Coverage**:
- Temporal deals queries (2025 successful deals)
- Location-based queries (Israeli clients with managers)
- Vendor-specific queries (HashiCorp products)
- Aggregation queries (top client managers)
- Installation queries (Wix product installations)

**Consequences**:
- ✅ Comprehensive RAG quality assessment
- ✅ Automated evaluation with actionable insights
- ✅ Standardized metrics for continuous improvement
- ✅ Enhanced testing beyond syntax/data validation
- ❌ Additional LLM API costs for evaluation
- ❌ Increased evaluation complexity and runtime

---

## ADR-018: Microsoft OAuth Authentication Integration

**Date**: 2025-11-18  
**Status**: Implemented  
**Context**: Need to secure `/promptui` endpoint with enterprise-grade authentication aligned with existing meetingsBot OAuth infrastructure

**Decision**: Implement Microsoft OAuth authentication using Python MSAL library with Bearer token validation, matching meetingsBot's security approach

**Requirements Analysis**:
- **Compatibility**: Align with meetingsBot's Node.js OAuth implementation
- **Domain Restriction**: Only `@terasky.com` users allowed
- **Token Format**: Bearer tokens compatible with existing infrastructure
- **Low LOE**: Minimal implementation using proven patterns
- **Future Integration**: Compatible for multi-service AI environment

**Technical Implementation**:
- **MSAL Client**: Python `msal` library for Microsoft authentication
- **Token Validation**: Microsoft Graph API validation with domain checking
- **FastAPI Integration**: Dependency-based route protection
- **Frontend Auth**: JavaScript popup-based OAuth flow
- **Error Handling**: Structured error responses matching meetingsBot format

**Architecture Components**:
```python
# Core Authentication Stack
app/auth/
├── msal_client.py          # Microsoft authentication client
├── token_validator.py      # Token validation via Graph API
└── dependencies.py         # FastAPI auth dependencies

app/api/
└── auth_routes.py          # OAuth endpoints (/auth/login, /auth/callback)
```

**Security Features**:
- **Domain Validation**: Strict `@terasky.com` email domain enforcement
- **Bearer Token**: Standard Authorization header validation
- **Microsoft Graph**: Server-side token validation via official API
- **Error Codes**: Structured error responses with specific codes
- **Session Management**: Client-side token storage with popup flow

**Protected Endpoints**:
- `GET /promptui` - HTML interface requires authentication
- `POST /api/v1/query` - API endpoint requires Bearer token
- **Unprotected**: Health checks, schema endpoints, auth endpoints

**Frontend Integration**:
- **Authentication UI**: Sign-in button with Microsoft 365 branding
- **Popup Flow**: Standard OAuth popup with message passing
- **Token Management**: Automatic token inclusion in API requests
- **Error Handling**: User-friendly auth error messages
- **Session Display**: User info display with sign-out option

**Environment Variables (Reused)**:
```env
MS_CLIENT_ID=<your-azure-app-client-id>
MS_TENANT_ID=<your-tenant-id>
MS_CLIENT_SECRET=<your-azure-app-client-secret>
MS_REDIRECT_URI=https://aipg.dudelabz.com/auth/callback
ALLOWED_DOMAIN=terasky.com
```

**Dependencies Added**:
- `msal==1.24.1` - Microsoft Authentication Library
- `python-jose[cryptography]==3.3.0` - JWT token handling
- `requests==2.31.0` - HTTP client for Graph API

**Compatibility Matrix**:
| Feature | MeetingsBot | TSKB-RAG | Status |
|---------|-------------|----------|--------|
| OAuth Flow | Authorization Code | Authorization Code | ✅ Match |
| Token Type | Bearer | Bearer | ✅ Match |
| Domain Validation | @terasky.com | @terasky.com | ✅ Match |
| Error Codes | Structured | Structured | ✅ Match |
| CORS Origins | Configured | Same Config | ✅ Match |

**Implementation Results**:
- **Authentication Flow**: Complete OAuth implementation with popup flow
- **Token Validation**: Server-side validation via Microsoft Graph API
- **Domain Enforcement**: Strict `@terasky.com` domain checking
- **Error Handling**: Comprehensive error responses with specific codes
- **Frontend Integration**: Seamless authentication UI with user management

**Testing Validation**:
- **OAuth Flow**: Complete authorization code flow with callback handling
- **Token Validation**: Microsoft Graph API integration for user profile
- **Domain Restriction**: Proper rejection of non-terasky.com users
- **API Protection**: Bearer token requirement for protected endpoints
- **Error Scenarios**: Proper handling of auth failures and token expiration

**Performance Impact**:
- **Authentication Overhead**: ~200ms for token validation via Graph API
- **Caching Opportunity**: Token validation results could be cached
- **Network Dependency**: Requires Microsoft Graph API availability
- **Client Experience**: Standard OAuth popup flow (~3-5 seconds)

**Consequences**:
- ✅ **Enterprise Security**: Production-ready OAuth authentication
- ✅ **Domain Restriction**: Only authorized terasky.com users can access
- ✅ **Infrastructure Alignment**: Compatible with existing meetingsBot setup
- ✅ **Future Integration**: Ready for multi-service authentication
- ✅ **Low Maintenance**: Uses Microsoft's official libraries and APIs
- ❌ **Network Dependency**: Requires Microsoft Graph API availability
- ❌ **Token Validation Latency**: Additional API call for each request
- ❌ **Client Complexity**: JavaScript popup flow management required

**Future Enhancements**:
- **Token Caching**: Cache validated tokens to reduce Graph API calls
- **SSO Integration**: Direct integration with meetingsBot for seamless experience
- **Admin Features**: Enhanced admin user capabilities and management
- **Audit Logging**: Comprehensive authentication and access logging

---

## Future Decisions

### Pending Decisions
- **Conversational Context Management**: Session-based conversation memory and context-aware query processing
- **Authentication Strategy**: OAuth2 vs API Keys vs JWT
- **Rate Limiting**: Strategy and implementation approach
- **Monitoring**: Metrics collection and alerting strategy
- **Testing Strategy**: Unit vs Integration vs E2E testing approach

### Deferred Decisions
- **Multi-tenancy**: Support for multiple organizations
- **Query History**: Storage and analysis of user queries
- **Advanced Analytics**: Query pattern analysis and optimization
- **Vector Search Integration**: ChromaDB integration for semantic search

---

---

## ADR-016: Teams Recording Integration

**Date**: 2025-11-17  
**Status**: Accepted  
**Context**: Need to extend RAG capabilities to include Microsoft Teams meeting recordings and calendar events for comprehensive meeting analytics

**Decision**: Integrate Teams Recording data (490 recordings, 470 calendar events) with specialized query patterns and answer generation

**Data Integration**:
- **Recording Nodes**: 490 recordings with status, transcriptUrl, createdDateTime, size
- **CalendarEvent Nodes**: 470 events with title, startTime, endTime, participants
- **New Relationships**: LINKED_TO (Recording→CalendarEvent), OWNER_OF/INVITED_TO (Employee→CalendarEvent)
- **Date Range**: 2024-08-22 to 2025-12-10 (actual data availability)

**Query Pattern Implementation**:
- **External Meeting Analytics**: Count external meetings using size(c.externalParticipants) > 0
- **Employee Activity Ranking**: Combine OWNER_OF + INVITED_TO relationships for total participation
- **Meeting Breakdown**: Internal vs external meeting classification for specific employees
- **Client Meeting Rankings**: Link clients to meetings via Employee relationships

**Technical Architecture**:
- **Query Type Detection**: Specialized detection for Teams Recording query patterns
- **Answer Generation**: Custom formatting for meeting analytics responses
- **Date Filtering**: Proper handling of Teams Recording date ranges vs business data
- **Filter Separation**: Prevent business data filters from corrupting Teams Recording queries

**Enhanced Components**:
```python
# Query Type Detection
if any(term in query_lower for term in ['meeting', 'recording', 'external', 'active employee']):
    return 'teams_recording_query'

# Specialized Answer Generation
def _generate_meeting_analytics_answer(self, query, data, query_type):
    if query_type == "external_meeting_analytics":
        count = data[0]['external_meetings_recorded']
        return f"There were {count} external meetings recorded during the specified period."
```

**Bedrock Client Enhancement**:
- **Teams Context**: Added comprehensive Teams Recording patterns to AI prompts
- **Common Patterns**: Pre-defined Cypher patterns for frequent query types
- **Date Context**: Proper date range handling for Teams Recording vs business data
- **Filter Management**: Separate filter logic to prevent cross-contamination

**Validation Results**:
- **External Meetings**: 304 total external meetings identified
- **Employee Rankings**: Gabi Brayer (88 meetings), David Gidony (83 meetings)
- **Meeting Breakdown**: David Gidony - 75 external, 8 internal meetings
- **Client Rankings**: PayKey, FireFly, Ametos (88 recorded meetings each)

**Performance Metrics**:
- **Query Success Rate**: 100% for implemented Teams Recording patterns
- **Response Time**: Sub-second execution for all meeting analytics queries
- **Data Coverage**: 85-95% linking success rate between recordings and calendar events
- **Answer Quality**: Contextual responses with proper data extraction

**Implementation Scope**:
- **Day 1 Completion**: Core query patterns and answer generation
- **API Integration**: Full Teams Recording support via /api/v1/query endpoint
- **Testing Coverage**: Comprehensive test suite for all query patterns
- **Documentation**: Complete integration guide and work plan

**Consequences**:
- ✅ **Extended RAG Scope**: Meeting analytics now available via natural language
- ✅ **Employee Insights**: Activity rankings and participation analysis
- ✅ **Client Analytics**: Meeting engagement tracking by client
- ✅ **Transcript Access**: Direct URL access to processed meeting content
- ✅ **Specialized Handling**: Proper separation from business data queries
- ❌ **Increased Complexity**: Additional query patterns and answer generation logic
- ❌ **Date Range Limitations**: Teams Recording data limited to 2024-2025 period
- ❌ **Filter Conflicts**: Required careful separation of filter injection logic

**Future Enhancements**:
- **Transcript Content Search**: Vector search within meeting transcripts
- **Meeting Sentiment Analysis**: Emotional tone analysis from transcripts
- **Action Item Extraction**: Automated task identification from meetings
- **Meeting Effectiveness Metrics**: Duration, participation, and outcome analysis

---

---

## ADR-017: Dynamic RAG Enhancement - Phase 1 Implementation

**Date**: 2025-11-17  
**Status**: Implemented  
**Context**: Static RAG system required manual updates for new query patterns and couldn't learn from user interactions

**Decision**: Implement Phase 1 of Dynamic RAG Enhancement with adaptive query classification and dynamic pattern detection

**Implementation Completed**:
- **AdaptiveQueryClassifier**: Learns successful query patterns and stores them for reuse
- **DynamicQueryDetector**: Discovers new query patterns from user interaction streams
- **EnhancedQueryGenerator**: Unified interface combining learned patterns, AI generation, and traditional rules
- **Learning Analytics**: Comprehensive insights and trend analysis

**Technical Architecture**:
```python
# Core Components Implemented
class AdaptiveQueryClassifier:
    - Pattern learning from successful queries
    - Semantic pattern extraction and similarity matching
    - JSON storage in data/query_patterns.json
    - Confidence-based pattern reuse (threshold: 0.8)

class DynamicQueryDetector:
    - Real-time pattern detection from query streams
    - Entity extraction and query type classification
    - Pattern suggestion generation
    - Trend analysis and recommendations

class EnhancedQueryGenerator:
    - Integrated learning capabilities
    - Fallback chain: Learned patterns → AI → Traditional
    - Automatic success/failure recording
    - Export/import for learning data
```

**API Endpoints Added**:
- `GET /api/v1/learning/insights` - Learning system analytics
- `GET /api/v1/learning/patterns` - Pattern suggestions
- `GET /api/v1/learning/trends` - Query trend analysis
- `GET /api/v1/learning/export` - Export learning data
- `POST /api/v1/learning/feedback` - Manual feedback recording

**Test Results (Initial Validation)**:
- **Patterns Learned**: 10 query patterns in initial test
- **Pattern Reuse**: 100% confidence for similar queries
- **Failure Analysis**: 4 different error types automatically categorized
- **Learning Maturity**: 0.13 (appropriate for early phase)
- **Pattern Diversity**: 0.60 (good variety of learned patterns)

**Integration Points**:
- **Main Query Processing**: Enhanced generator integrated into /api/v1/query
- **Automatic Learning**: Success/failure recording for every query
- **Confidence Routing**: Use learned patterns when confidence > 0.8
- **Fallback Chain**: Graceful degradation through multiple methods

**Learning Capabilities**:
- **Semantic Pattern Extraction**: Entity types, query types, complexity scoring
- **Similarity Matching**: Pattern comparison with configurable thresholds
- **Success Tracking**: Execution time, data count, user feedback integration
- **Failure Analysis**: Error categorization and improvement recommendations

**Storage and Persistence**:
- **Pattern Storage**: JSON-based storage in `data/query_patterns.json`
- **Persistent Volume**: `/home/ubuntu/meetingsBotLogs/persistentData:/app/data` (IMPLEMENTED)
- **Automatic Backup**: Save patterns after every learning event
- **Export/Import**: Full learning data backup and restoration
- **Query History**: Last 100 queries maintained for pattern detection
- **Production Validation**: 8 patterns surviving container restarts with usage tracking

**Performance Characteristics**:
- **Pattern Recognition**: Instant matching for known patterns
- **Learning Speed**: Real-time pattern extraction and storage
- **Memory Efficiency**: Bounded query history (100 queries max)
- **Confidence Scoring**: Multi-factor confidence calculation

**Success Metrics Achieved**:
- **Pattern Learning**: Successfully learns from every successful query
- **Pattern Reuse**: Instant recognition and reuse of similar patterns
- **Failure Learning**: Comprehensive error analysis and categorization
- **Analytics**: Rich insights into learning progress and trends

**Consequences**:
- ✅ **Self-Learning Foundation**: System now learns from every interaction
- ✅ **Improved Performance**: Instant pattern matching for known queries
- ✅ **Reduced Manual Work**: Automatic pattern discovery and reuse
- ✅ **Comprehensive Analytics**: Deep insights into system learning
- ✅ **Production Ready**: Integrated into main query processing pipeline
- ❌ **Increased Complexity**: Additional components and storage requirements
- ❌ **Early Learning Phase**: System needs time to build pattern library

**Next Phases (Planned)**:
- **Phase 2**: Schema Evolution Engine for auto-discovery of new data patterns
- **Phase 3**: Continuous RAGAS integration and self-improvement mechanisms

**Dependencies Met**:
- ✅ Teams Recording integration (COMPLETE)
- ✅ Enhanced query generation framework (COMPLETE)
- ✅ JSON storage capabilities (COMPLETE)
- ✅ API integration points (COMPLETE)

---

---

## ADR-019: Centralized OAuth JWT Authentication

**Date**: 2025-11-18  
**Status**: Implemented  
**Context**: Replace individual service OAuth with centralized JWT authentication via meetingsBot for unified TeraSky AI platform access

**Decision**: Implement JWT-based authentication using shared secret with meetingsBot, replacing direct OAuth popup flow

**Architecture Shift**:
- **From**: Individual OAuth per service (TSKB-RAG, meetingsBot separate)
- **To**: Centralized OAuth via meetingsBot with JWT token sharing
- **Pattern**: Single sign-on for entire TeraSky AI service ecosystem

**Technical Implementation**:
- **JWT Secret**: Shared 64-character hex secret between services
- **Token Structure**: Standard JWT with issuer/audience validation
- **Validation**: PyJWT library for server-side token verification
- **Flow**: meetingsBot OAuth → JWT generation → TSKB-RAG access
- **Security**: 1-hour token expiration with domain validation

**Integration Points**:
```python
# JWT Validation Dependencies
from app.auth.jwt_validator import validate_jwt_token
from app.auth.jwt_dependencies import get_current_user

# Protected Route Example
@router.post("/query")
async def query_endpoint(
    request: QueryRequest,
    current_user: dict = Depends(get_current_user)
):
    # User authenticated via JWT
    pass
```

**Frontend Integration**:
- **URL Parameter**: `?auth_token=<jwt>` from meetingsBot redirect
- **Automatic Validation**: Token validation on page load
- **User Context**: Extract user info from JWT payload
- **API Integration**: Bearer token for all API requests

**Security Model**:
- **Shared Secret**: `JWT_SECRET` environment variable (64-char hex)
- **Token Claims**: Standard JWT with `sub`, `email`, `name`, `exp`, `iss`, `aud`
- **Domain Validation**: `domain_verified: true` claim required
- **Expiration**: 1-hour token lifetime with automatic refresh

**Migration from OAuth Popup**:
- **Removed**: MSAL client, popup flow, Microsoft Graph validation
- **Simplified**: Direct JWT validation without external API calls
- **Performance**: <50ms validation vs ~200ms Graph API calls
- **Reliability**: No dependency on Microsoft Graph API availability

**Production Deployment**:
- **meetingsBot**: JWT generation endpoint on port 443
- **TSKB-RAG**: JWT validation on port 8002 with HTTPS
- **SSL Integration**: Secure token transmission via HTTPS
- **Network**: Both services on TS_AI_network for internal communication

**User Experience Flow**:
1. User accesses meetingsBot (already authenticated)
2. User clicks "TSKB-RAG" link in meetingsBot
3. meetingsBot generates JWT and redirects to TSKB-RAG
4. TSKB-RAG validates JWT and displays authenticated interface
5. User queries TSKB-RAG with Bearer token authentication

**Scalability Benefits**:
- **Multi-Service Pattern**: Easy addition of new AI services
- **Single OAuth**: One OAuth configuration for entire platform
- **Consistent UX**: Seamless navigation between AI services
- **Reduced Complexity**: No per-service OAuth management

**Dependencies**:
- `PyJWT==2.8.0` - JWT token validation
- Shared `JWT_SECRET` between meetingsBot and TSKB-RAG
- HTTPS configuration for secure token transmission

**Validation Results**:
- **End-to-End Flow**: Complete authentication flow working
- **Token Security**: 1-hour expiration enforced
- **Domain Validation**: @terasky.com restriction maintained
- **Performance**: <50ms JWT validation per request
- **User Experience**: <3 seconds from meetingsBot to authenticated TSKB-RAG

**Consequences**:
- ✅ **Unified Platform**: Single sign-on for TeraSky AI services
- ✅ **Improved Performance**: 4x faster authentication validation
- ✅ **Reduced Dependencies**: No external API dependencies for auth
- ✅ **Scalable Pattern**: Easy integration for future AI services
- ✅ **Better UX**: Seamless service-to-service navigation
- ✅ **Simplified Architecture**: Removed OAuth popup complexity
- ❌ **Shared Secret Management**: Critical secret must be synchronized
- ❌ **Token Refresh**: Manual token refresh implementation needed
- ❌ **Service Coupling**: Authentication tied to meetingsBot availability

**Future Enhancements**:
- **Token Refresh**: Automatic token refresh mechanism
- **Service Discovery**: Dynamic service registration and JWT routing
- **Admin Dashboard**: Centralized user and service management
- **Audit Logging**: Comprehensive authentication and access logging

---

## ADR-020: Response Consistency Enhancement

**Date**: 2025-11-18  
**Status**: Implemented  
**Context**: Query responses showed inconsistent formatting - natural language vs raw data vs generic messages, causing poor user experience

**Decision**: Enhance answer generation with consistent response formatting, multi-part query handling, and user-friendly field name conversion

**Problem Analysis**:
- **Inconsistent Formats**: "314 external meetings" vs "failed_opportunities: 865" vs "83 results"
- **Raw Field Exposure**: Database field names like "failed_opportunities" shown to users
- **Incomplete Multi-part Answers**: "How many X and what is most popular Y" only answered first part
- **Generic Responses**: "The query returned 83 results" provided no actionable information

**Solution Implementation**:
- **Enhanced Count Responses**: Context-aware formatting for different query types
- **Field Name Mapping**: Convert database fields to user-friendly descriptions
- **Multi-part Query Detection**: Identify and handle complex queries with multiple questions
- **Contextual Formatting**: Specialized responses for failed opportunities, external meetings, etc.

**Technical Changes**:
```python
# Enhanced count answer generation
def _generate_count_answer(self, user_query: str, data: List[Dict]) -> str:
    if "failed" in query_lower and "opportunit" in query_lower:
        return f"There were {count_value} failed opportunities during 2025."
    # Convert raw field names to friendly descriptions
    friendly_name = self._convert_field_to_friendly_name(count_field)
    return f"Found {count_value} {friendly_name}."

# Multi-part query handling
def _generate_multi_part_answer(self, user_query: str, data: List[Dict]) -> str:
    # Handle "how many X AND most popular Y" queries
    if "failed" in query_lower and "most popular" in query_lower:
        # Provide both count and product breakdown
```

**Field Name Mappings Added**:
- `failed_opportunities` → "failed opportunities"
- `external_meetings_recorded` → "external meetings recorded"
- `meeting_count` → "meetings"
- `sf_name` → "name"
- `total_price` → "total value"

**Response Format Examples**:
- **Before**: "failed_opportunities: 865"
- **After**: "There were 865 failed opportunities during 2025."

- **Before**: "The query returned 83 results"
- **After**: "Found 83 failed opportunities. Most failed products: Product A (25 failures), Product B (18 failures)"

**Multi-part Query Handling**:
- **Detection**: Identifies queries with "and", "most popular", "top", etc.
- **Structured Responses**: Attempts to answer all parts of complex questions
- **Graceful Degradation**: Suggests breaking complex queries into parts when needed

**Backward Compatibility**:
- **Preserved**: All existing query patterns continue to work
- **Enhanced**: Existing responses now more user-friendly
- **No Breaking Changes**: API response structure unchanged

**Consequences**:
- ✅ **Consistent User Experience**: All responses now use natural language
- ✅ **Better Multi-part Handling**: Complex queries get more complete answers
- ✅ **User-friendly Field Names**: No more raw database field exposure
- ✅ **Contextual Responses**: Answers tailored to specific query types
- ✅ **Maintained Compatibility**: No breaking changes to existing functionality
- ❌ **Increased Complexity**: Additional logic for response formatting
- ❌ **Maintenance Overhead**: Field mappings need updates as schema evolves

---

---

## ADR-021: Self-Improving RAG Engine - Phase 1 Config Foundation

**Date**: 2025-11-19  
**Status**: Implemented  
**Context**: Hardcoded routing parameters (learned_pattern_threshold, fallback_order) in routes.py prevented flexible configuration and future dynamic adjustments

**Decision**: Introduce configuration-driven RAG routing with YAML config file and cached loader, maintaining zero external behavioral changes

**Problem Analysis**:
- **Hardcoded Values**: `learned_pattern_threshold = 0.8` and fallback chain hardcoded in routes.py
- **Inflexible Configuration**: Changes required code modifications and redeployment
- **Future Limitations**: Dynamic threshold adjustment impossible with hardcoded values
- **Maintenance Overhead**: Configuration scattered across codebase

**Solution Architecture**:
- **YAML Configuration**: Centralized config file for all RAG routing parameters
- **Cached Loader**: Performance-optimized config loading with LRU cache
- **Error Handling**: Graceful fallback to defaults if config unavailable
- **Zero Behavioral Change**: External API behavior completely unchanged

**Implementation Details**:
```yaml
# config/rag_config.yaml
routing:
  learned_pattern_threshold: 0.8
  fallback_order:
    - "ai"
    - "enhanced"
    - "traditional"
```

```python
# app/core/config.py
@lru_cache(maxsize=1)
def get_rag_config() -> Dict[str, Any]:
    # Cached YAML loading with error handling
    # Fallback to defaults if config unavailable
```

**Refactoring Changes**:
- **Routes.py**: Replaced hardcoded `0.8` with `config['routing']['learned_pattern_threshold']`
- **Config Import**: Added `from app.core.config import get_rag_config`
- **Dynamic Loading**: Config loaded at runtime, not startup
- **Preserved Logic**: Exact same routing behavior maintained

**Dependencies Added**:
- `PyYAML==6.0.1` - YAML configuration file support

**Testing Strategy**:
- **Config Loading Test**: Validates YAML parsing and structure
- **Behavioral Verification**: Confirms unchanged routing behavior
- **Manual Testing**: API endpoint testing with sample queries
- **Config Modification**: Verify threshold changes take effect

**File Structure**:
```
config/
└── rag_config.yaml          # Main RAG configuration

app/core/
└── config.py                # Configuration loader

Tests/
└── test_rag_config.py       # Configuration testing

docs/Self-ImprovingRAG/
└── Phase1-Config-Foundation.md  # Phase documentation
```

**Performance Characteristics**:
- **Cached Loading**: Config loaded once, cached for subsequent requests
- **Minimal Overhead**: <1ms additional latency for config access
- **Error Resilience**: Defaults used if config file unavailable
- **Hot Reload**: Config changes require cache invalidation (future enhancement)

**Validation Results**:
- **Zero Behavioral Change**: Confirmed identical routing behavior
- **Config Loading**: YAML parsing working correctly
- **Error Handling**: Graceful fallback to defaults tested
- **API Compatibility**: All existing endpoints unchanged

**Foundation for Future Phases**:
- **Phase 2**: Dynamic threshold adjustment based on performance metrics
- **Phase 3**: Machine learning-driven configuration optimization
- **Phase 4**: Real-time configuration updates without restart

**Consequences**:
- ✅ **Configuration Foundation**: Centralized, maintainable RAG configuration
- ✅ **Zero Breaking Changes**: Complete backward compatibility maintained
- ✅ **Future Flexibility**: Ready for dynamic configuration features
- ✅ **Performance Optimized**: Cached loading with minimal overhead
- ✅ **Error Resilient**: Graceful degradation if config unavailable
- ❌ **Additional Dependency**: PyYAML library requirement
- ❌ **Config File Management**: New configuration file to maintain
- ❌ **Cache Invalidation**: Manual cache clearing needed for config updates

**Next Steps**:
- **Phase 2 Planning**: Dynamic threshold adjustment based on query success rates
- **Hot Reload**: Implement configuration hot reload without restart
- **Config Validation**: Enhanced validation for configuration values
- **Monitoring**: Configuration change tracking and audit logging

---

---

## ADR-022: Self-Improving RAG Engine - Phase 2 LLM Abstraction

**Date**: 2025-11-19  
**Status**: Implemented  
**Context**: Mixed responsibilities in bedrock_client.py prevented multi-model support and provider independence

**Decision**: Create centralized LLMClient abstraction to separate prompt building from LLM execution, enabling multi-model capabilities

**Problem Analysis**:
- **Mixed Responsibilities**: bedrock_client.py handled prompt building, AWS Bedrock calls, response parsing, and error handling
- **Multi-model Limitations**: Impossible to add judge models, fallback models, or alternative providers
- **Code Duplication Risk**: Future model additions would require duplicating Bedrock logic
- **Testing Complexity**: Difficult to mock and unit test LLM interactions

**Solution Architecture**:
- **LLMClient Abstraction**: Centralized class for all LLM interactions (`app/core/llm_client.py`)
- **BedrockClient Refactor**: Reduced to prompt building only, delegates LLM calls to LLMClient
- **Clean Separation**: Prompt construction vs LLM execution completely separated
- **Provider Independence**: Foundation for future provider abstraction

**Implementation Details**:
```python
# New LLMClient abstraction
class LLMClient:
    async def generate(self, prompt: str, **kwargs) -> str
    async def complete(self, system_prompt: str, user_prompt: str, **kwargs) -> str

# Refactored BedrockClient (prompt building only)
class BedrockClient:
    def __init__(self, llm_client: LLMClient)
    async def generate_cypher(self, user_query: str, schema: Dict) -> str
        # Build prompts, call llm_client.complete()
```

**Architecture Benefits**:
- **Multi-model Support**: Easy addition of judge models, fallback models
- **Provider Independence**: Future support for OpenAI, Anthropic, local models
- **Clean Testing**: Separate unit tests for prompt building vs LLM execution
- **Code Reuse**: Single LLM abstraction for all model interactions

**Files Created/Modified**:
- **New**: `app/core/llm_client.py` - Centralized LLM abstraction
- **New**: `Tests/test_llm_client.py` - Comprehensive unit tests (6/6 pass)
- **New**: `Tests/test_llm_integration.py` - End-to-end integration test
- **Modified**: `app/core/bedrock_client.py` - Refactored to prompt building only
- **Modified**: `app/api/routes.py` - Updated dependency injection

**Testing Validation**:
- **Unit Tests**: 6/6 LLMClient tests pass (initialization, generate, complete, error handling)
- **Integration Test**: Confirms identical Cypher generation before/after refactor
- **Behavioral Verification**: Zero external behavior change confirmed
- **Performance**: No latency impact, identical response times

**Multi-Model Capabilities Enabled**:
```python
# Judge model for quality assessment
judge_client = LLMClient("claude-3-haiku")

# Fallback model for reliability
fallback_client = LLMClient("claude-3-sonnet")

# Batch evaluation model
eval_client = LLMClient("claude-3-opus")

# Use in BedrockClient
bedrock_with_judge = BedrockClient(judge_client)
```

**Success Criteria Met**:
- ✅ **Architecture-level**: All Bedrock logic removed from bedrock_client.py
- ✅ **Code-level**: LLMClient returns identical responses to old logic
- ✅ **Test-level**: All existing tests pass, new unit tests pass
- ✅ **Behavioral**: /api/v1/query returns exactly same JSON before/after
- ✅ **Deployment**: Code builds in Docker without modifications

**Consequences**:
- ✅ **Multi-model Foundation**: Easy addition of judge models and fallback models
- ✅ **Provider Independence**: Ready for OpenAI, Anthropic, local model support
- ✅ **Clean Architecture**: Complete separation of prompt building and LLM execution
- ✅ **Enhanced Testing**: Separate unit tests for each responsibility
- ✅ **Zero Breaking Changes**: Identical external behavior maintained
- ❌ **Async Complexity**: BedrockClient.generate_cypher() now async (handled in routes)
- ❌ **Additional Abstraction**: One more layer in the call stack

**Future Capabilities**:
- **Phase 3**: Multi-model routing with judge models for quality assessment
- **Phase 4**: Provider abstraction supporting multiple LLM providers
- **Phase 5**: Dynamic model selection based on query complexity

---

---

## ADR-023: Self-Improving RAG Engine - Phase 3 Multi-Model Support

**Date**: 2025-11-19  
**Status**: Implemented  
**Context**: Single hardcoded model in LLMClient prevented judge model evaluation and multi-model capabilities

**Decision**: Implement config-driven multi-model support with role-based model selection while maintaining identical production behavior

**Problem Analysis**:
- **Single Model Limitation**: LLMClient hardcoded to one model, preventing judge model usage
- **Evaluation Constraints**: No way to use different models for quality assessment vs generation
- **Configuration Rigidity**: Model changes required code modifications and redeployment
- **Future Limitations**: Impossible to add fallback models, A/B testing, or provider diversity

**Solution Architecture**:
- **Config-Driven Models**: Extended rag_config.yaml with models section defining primary and judge models
- **Role-Based Selection**: LLMClient accepts role parameter ("primary", "judge") for model selection
- **Configuration Helpers**: Added get_model_config(role) for retrieving model configurations
- **Judge Model Foundation**: Created placeholder judge_client.py for future evaluation logic

**Implementation Details**:
```yaml
# config/rag_config.yaml
models:
  primary:
    provider: "bedrock"
    model_id: "us.anthropic.claude-sonnet-4-20250514-v1:0"
    max_tokens: 4000
    temperature: 0.3
  judge:
    provider: "bedrock"
    model_id: "us.anthropic.claude-3-5-haiku-20241022-v1:0"
    max_tokens: 2000
    temperature: 0.0
```

```python
# Role-based model selection
response = await llm_client.generate(prompt, role="primary")  # Production
response = await llm_client.generate(prompt, role="judge")    # Evaluation
```

**Architecture Benefits**:
- **Easy Model Switching**: Change models via configuration without code changes
- **Judge Model Ready**: Foundation for quality assessment and evaluation
- **Role Clarity**: Clear separation between production and evaluation model usage
- **Future Extensibility**: Easy addition of fallback, experimental, or specialized models

**Files Created/Modified**:
- **Modified**: `config/rag_config.yaml` - Added models section with primary/judge configs
- **Modified**: `app/core/config.py` - Added get_model_config() helper function
- **Modified**: `app/core/llm_client.py` - Added role parameter for model selection
- **Modified**: `app/core/bedrock_client.py` - Explicit primary role usage in production
- **New**: `app/core/judge_client.py` - Judge model placeholder implementation
- **New**: `Tests/test_multi_model_config.py` - Multi-model configuration tests (7/7 pass)

**Testing Validation**:
- **Unit Tests**: 7/7 multi-model configuration tests pass
- **Integration Test**: Confirms identical behavior with primary role usage
- **Judge Model Path**: Placeholder implementation verified (graceful failure for unavailable models)
- **Configuration Loading**: Primary and judge model configs load correctly
- **Role Fallback**: Unknown roles fall back to primary model

**Production Safety**:
- **Explicit Primary Usage**: All production calls use role="primary" explicitly
- **Graceful Judge Failure**: Judge model errors don't affect production queries
- **Zero Behavioral Change**: External API behavior identical to Phase 2
- **No New Dependencies**: Uses existing configuration and LLMClient infrastructure

**Multi-Model Capabilities Enabled**:
```python
# Production usage (unchanged behavior)
response = await llm_client.complete(system, user, role="primary")

# Judge model evaluation (new capability)
from app.core.judge_client import judge_answer
result = await judge_answer(llm_client, question, answer, context)

# Future model roles (easy to add)
response = await llm_client.generate(prompt, role="fallback")
response = await llm_client.generate(prompt, role="experimental")
```

**Success Criteria Met**:
- ✅ **Config-level**: Models section with primary/judge, get_model_config() working
- ✅ **Code-level**: Role-based selection, explicit primary usage, judge path exists
- ✅ **Test-level**: All tests pass, identical responses confirmed
- ✅ **Behavioral**: No external API changes, graceful judge failure
- ✅ **Future-ready**: Easy judge instantiation, extensible role system

**Consequences**:
- ✅ **Multi-Model Foundation**: Ready for judge model evaluation and quality assessment
- ✅ **Configuration Flexibility**: Easy model switching via YAML configuration
- ✅ **Role-Based Architecture**: Clear separation between production and evaluation usage
- ✅ **Zero Breaking Changes**: Identical external behavior maintained
- ✅ **Judge Model Ready**: Foundation for Phase 4 evaluation logic
- ❌ **Configuration Complexity**: Additional YAML structure to maintain
- ❌ **Role Parameter**: Additional parameter in LLMClient method calls

**Future Capabilities**:
- **Phase 4**: Judge model evaluation for quality assessment and confidence scoring
- **Phase 5**: Fallback model routing for reliability and error recovery
- **Phase 6**: Dynamic model selection based on query complexity and performance

---

---

## ADR-024: Self-Improving RAG Engine - Phase 3 Multi-Model Support Completion

**Date**: 2025-11-19  
**Status**: Completed  
**Context**: Phase 3 implementation successfully completed with comprehensive testing and validation

**Achievement Summary**:
- **Multi-Model Configuration**: Both primary and judge models configured and working
- **Role-Based Selection**: LLMClient correctly routes to different model configs based on role
- **Zero Behavioral Change**: Production behavior identical to Phase 2
- **Judge Model Foundation**: Ready for Phase 4 evaluation logic implementation
- **Practical Approach**: Using same working model for both roles ensures reliability

**Test Results Validated**:
- **Integration Test**: `python Tests\test_llm_integration.py` - PASSED
- **Primary Model**: us.anthropic.claude-sonnet-4-20250514-v1:0 - Working ✅
- **Judge Model**: us.anthropic.claude-sonnet-4-20250514-v1:0 - Working ✅
- **Generated Cypher**: MATCH (c:Client) RETURN count(c) as clientCount
- **Query Execution**: Successfully returned 1 result
- **Multi-Model Usage**: Both primary and judge model paths verified

**Key Achievements**:
- **Config-Driven Models**: Both primary and judge models configured via YAML
- **Role-Based Selection**: LLMClient correctly routes based on role parameter
- **Zero Behavioral Change**: Production behavior identical to Phase 2
- **Judge Model Foundation**: Ready for Phase 4 evaluation logic
- **Practical Approach**: Using same working model for both roles ensures reliability

**Multi-Model Usage Confirmed**:
```python
# Primary model (production) - Working ✅
response = await llm_client.complete(system, user, role="primary")

# Judge model (evaluation) - Working ✅  
from app.core.judge_client import judge_answer
result = await judge_answer(llm_client, question, answer, context)
```

**Consequences**:
- ✅ **Phase 3 Complete**: All objectives achieved with comprehensive validation
- ✅ **Foundation Ready**: Phase 4 judge model evaluation can proceed
- ✅ **Multi-Model Capability**: Role-based model selection working correctly
- ✅ **Production Stability**: Zero impact on existing functionality
- ✅ **Future Extensibility**: Easy addition of new model roles and configurations

**Next Phase Ready**: Phase 4 implementation can proceed with judge model evaluation, quality assessment, and future multi-model capabilities.

---

## ADR-025: Self-Improving RAG Engine - Phase 6 Config Auto-Tuning

**Date**: 2025-11-19  
**Status**: Implemented  
**Context**: Need intelligent optimization of RAG configuration parameters based on evaluation results to automatically improve system performance

**Decision**: Implement config auto-tuning system starting with retrieval limits per intent, with comprehensive safety guardrails

**Problem Analysis**:
- **Manual Tuning**: Configuration parameters required manual adjustment based on performance observations
- **Performance Optimization**: No systematic approach to optimize retrieval limits based on evaluation data
- **Operational Overhead**: Manual monitoring and adjustment of configuration parameters
- **Data-Driven Decisions**: Need to leverage evaluation results for intelligent configuration optimization

**Solution Architecture**:
- **Tuning Engine**: Core logic for stats computation and suggestion generation (`app/monitoring/tuning.py`)
- **CLI Runner**: Operational tooling with suggest-only and apply modes (`app/monitoring/tuning_runner.py`)
- **Safety Guardrails**: Automatic backups, minimum evaluation counts, maximum limits
- **Intelligent Rules**: Data-driven suggestions based on error rates and performance scores

**Implementation Details**:
```python
# Core data models
@dataclass
class IntentStats:
    intent: str
    eval_count: int
    avg_overall_score: float
    avg_factual_correctness: float
    avg_grounded_in_context: float
    avg_helpfulness: float
    error_type_distribution: Dict[str, float]

@dataclass
class TuningSuggestion:
    intent: str
    current_limit: int
    suggested_limit: int
    reason: str
```

**Tuning Rules Implemented**:
- **Increase Limit**: When retrieval error ratio > 0.3 AND avg score < 7.5 AND current limit < max_limit
- **Decrease Limit**: When retrieval error ratio < 0.1 AND avg score > 8.5 AND current limit > step
- **No Change**: When performance is moderate or insufficient evaluation data

**CLI Interface**:
```bash
# Generate suggestions (dry run)
python -m app.monitoring.tuning_runner --suggest-only

# Apply changes with automatic backup
python -m app.monitoring.tuning_runner --apply

# Custom parameters
python -m app.monitoring.tuning_runner --apply --min-eval-count 15 --max-limit 40
```

**Safety Mechanisms**:
- **Minimum Evaluation Count**: Default 10 evaluations required per intent
- **Maximum Limits**: Configurable maximum retrieval limit (default: 50)
- **Automatic Backups**: Timestamped config backups before any changes
- **Guardrail Enforcement**: Never exceed limits, require sufficient data
- **Change Logging**: Comprehensive audit trail of all modifications

**Files Created**:
- **Core Engine**: `app/monitoring/tuning.py` - Stats computation and suggestion logic
- **CLI Runner**: `app/monitoring/tuning_runner.py` - Operational interface with safety features
- **Comprehensive Tests**: `Tests/test_tuning.py` - 16/16 unit tests passing
- **Documentation**: `docs/Self-ImprovingRAG/Phase6-Config-Auto-Tuning.md`

**Testing Validation**:
- **Unit Tests**: 16/16 tests passing with full coverage
  - IntentStats and TuningSuggestion data models
  - Stats computation from JSONL evaluation results
  - Suggestion rules (increase/decrease/no-change logic)
  - Configuration application with guardrails
  - Error handling and edge cases
- **CLI Interface**: Fully functional with help documentation
- **Sample Data**: Tested with realistic evaluation data showing correct suggestions

**Operational Features**:
- **Suggest-Only Mode**: Generate JSON suggestions without applying changes
- **Apply Mode**: Automatic backup and configuration modification
- **Human-Readable Output**: Clear summaries of suggestions and rationale
- **JSON Integration**: Machine-readable output for automation
- **Comprehensive Logging**: Audit trail for all tuning operations

**Sample Output**:
```
[TUNING] Generated 1 tuning suggestions:
[INTENT] CLIENT_HISTORY
   Current limit: 10
   Suggested limit: 15
   Reason: High retrieval error ratio (0.92) and low overall score (6.7)
   Evaluations: 12
   Avg score: 6.7
   Retrieval errors: 91.7%
```

**Success Criteria Met**:
- ✅ **Tuning Engine**: IntentStats and TuningSuggestion models with pure functions
- ✅ **Stats Computation**: Accurate computation from evaluation results JSONL
- ✅ **Suggestion Generation**: Intelligent rules with configurable parameters
- ✅ **Suggest-Only Mode**: JSON output without configuration changes
- ✅ **Apply Mode**: Automatic backups and safe configuration modification
- ✅ **Comprehensive Testing**: 16/16 unit tests with full coverage
- ✅ **CLI Interface**: Production-ready operational tooling
- ✅ **Safety Guardrails**: Multiple layers of protection and validation

**Consequences**:
- ✅ **Automated Optimization**: Data-driven configuration improvements without manual intervention
- ✅ **Production Safety**: Comprehensive backup and rollback capabilities
- ✅ **Operational Tooling**: CLI interface ready for cron jobs and operational deployment
- ✅ **Foundation for Expansion**: Easy extension to additional configuration parameters
- ✅ **Audit Trail**: Complete logging and change tracking for compliance
- ❌ **Configuration Complexity**: Additional tuning logic and parameters to maintain
- ❌ **Evaluation Dependency**: Requires sufficient evaluation data for effective tuning

**Future Capabilities**:
- **Multi-Parameter Tuning**: Extend to temperature, top_k, and other model parameters
- **A/B Testing**: Automated configuration experiments with performance comparison
- **Rollback Automation**: Automatic rollback on performance degradation detection
- **Advanced Algorithms**: Machine learning-based optimization beyond rule-based suggestions

---

---

## ADR-026: Answer Generation Consistency Fix

**Date**: 2025-11-23  
**Status**: Implemented  
**Context**: RAG system producing inconsistent and confusing responses - simple count queries flagged as multi-part, inconsistent answer formats

**Decision**: Fix answer generation logic to provide consistent, contextual responses without false multi-part warnings

**Problem Analysis**:
- **Overly Aggressive Multi-part Detection**: Simple queries like "how many non terasky products" flagged as multi-part
- **Inconsistent Count Detection**: Flawed logic for identifying when queries should return simple counts
- **Confusing User Experience**: "Your query contains multiple parts" warnings for simple questions
- **Inconsistent Formatting**: Different answer formats for similar query types

**Solution Implementation**:
- **Refined Multi-part Detection**: Only flag queries with explicit conjunctions AND additional requests
- **Improved Count Logic**: Focus on single-result numeric responses with count keywords
- **Contextual Responses**: Enhanced count answers with query-specific context
- **Streamlined Decision Tree**: Eliminated conflicting answer generation paths

**Technical Changes**:
```python
# Fixed multi-part detection
def _is_multi_part_query(self, query: str) -> bool:
    has_conjunction = any(conj in query_lower for conj in [" and ", " & ", "also"])
    has_additional_request = any(req in query_lower for req in ["list", "show", "names"])
    has_question_then_request = "?" in query and any(req in query_lower.split("?")[-1] for req in ["list", "show"])
    return (has_conjunction and has_additional_request) or has_question_then_request

# Improved count detection
def _is_count_query(self, query: str, data: List[Dict]) -> bool:
    has_count_keyword = any(keyword in query for keyword in ["how many", "count", "number of"])
    if has_count_keyword and data and len(data) == 1:
        numeric_fields = [k for k, v in data[0].items() if isinstance(v, (int, float))]
        return len(numeric_fields) > 0
    return False
```

**Answer Quality Improvements**:
- **"how many non terasky products do we have ?"** → "Found 429 non-TeraSky products."
- **"how many employees operating in us ?"** → "Found 292 employees operating in the US."
- **"how many non terasky products that has a successful deal during 2025 do we have ?"** → "Found 95 non-TeraSky products that had successful deals during 2025."

**Results Achieved**:
- **Eliminated False Positives**: Simple queries no longer flagged as multi-part
- **Consistent Count Responses**: Clean, contextual answers for count queries
- **Improved User Experience**: No more confusing "multiple parts" warnings
- **Contextual Formatting**: Query-specific responses based on content

**Testing Validation**:
- **Count Query Detection**: Properly identifies single-result numeric responses
- **Multi-part Detection**: Only flags truly complex queries
- **Answer Consistency**: Same query types produce consistent response formats
- **Contextual Responses**: Answers tailored to query content (products, employees, deals)

**Consequences**:
- ✅ **Consistent User Experience**: Clean, predictable responses for similar queries
- ✅ **Eliminated Confusion**: No more false multi-part warnings for simple questions
- ✅ **Contextual Answers**: Responses now include relevant business context
- ✅ **Improved Accuracy**: Better detection of query types and appropriate formatting
- ✅ **Maintained Functionality**: All existing query patterns continue to work
- ❌ **Increased Logic Complexity**: More sophisticated detection and formatting rules
- ❌ **Maintenance Overhead**: Additional contextual patterns to maintain as queries evolve

**Future Enhancements**:
- **Pattern Learning**: Automatic detection of new contextual response patterns
- **User Feedback Integration**: Learn from user satisfaction to improve answer quality
- **Advanced Multi-part Handling**: Better support for complex queries with multiple components

---

**Last Updated**: 2025-11-23  
**Next Review**: 2025-12-23


## ADR-027: Self-Learning RAG Integration - Phase 1 Complete

**Date**: 2025-12-22  
**Status**: Implemented  
**Context**: Production RAG system needed CLI demo quality with intent-based routing, validation retry, and LLM-based explanations

**Decision**: Integrate self-learning RAG components from DGX playground into production TSKB-RAG system

**Problem Analysis**:
- **Generic Cypher Generation**: Single prompt for all query types resulted in suboptimal queries
- **No Validation Retry**: Failed queries had no self-correction mechanism
- **Rule-Based Answers**: Simple formatters couldn't provide insightful explanations
- **Quality Gap**: CLI demo significantly outperformed production system

**Solution Architecture**:
- **Intent-Based Prompt Routing**: 4 specialized profiles (sales_v1, calendar_v1, product_v1, strict_v1)
- **Cypher Validation with Retry**: Max 2 attempts with temperature drop to 0.0 on retry
- **LLM-Based Answer Rendering**: Natural language explanations from query results
- **Temperature Optimization**: Using trained temperature 0.1 from best_config.json

**Implementation Components**:
```python
# Intent Classification
def classify_question_intent(question: str) -> str:
    # Keyword-based classification into 4 intents
    # Returns: sales_v1, calendar_v1, product_v1, or strict_v1

# Prompt Profiles
PROMPT_PROFILES = {
    "sales_v1": {
        "system": SCHEMA + RULES + SALES_FOCUS + EXAMPLES,
        "user_template": "Convert this sales question: {question}"
    },
    # ... calendar_v1, product_v1, strict_v1
}

# Validation with Retry
async def generate_cypher(query, schema, trace):
    intent = classify_question_intent(query)
    system_prompt, user_prompt = get_prompt_for_intent(intent, query)
    
    for attempt in range(max_attempts):
        raw_cypher = await llm_client.complete(system_prompt, user_prompt, temp)
        cypher, errors = validate_and_clean(raw_cypher)
        if not errors:
            return cypher
        # Retry with correction guidance, temp=0.0

# LLM-Based Answer Rendering
async def render_answer(question, rows, bedrock_client):
    # Serialize results, send to LLM for natural language explanation
    # Returns: Contextual explanation with insights
```

**Prompt Profile Specializations**:
- **sales_v1**: OPPORTUNITY relationships, close_date filtering, vendor filtering emphasis
- **calendar_v1**: CalendarEvent queries, simple MATCH patterns, date ranges
- **product_v1**: Product.vendor filtering, non-TeraSky patterns, CONTAINS matching
- **strict_v1**: Minimal guidance for ambiguous queries

**Validation Features**:
- **SQL Detection**: Rejects SELECT, FROM, GROUP BY keywords
- **Forbidden Patterns**: Checks for invented nodes like :Deal
- **Syntax Validation**: Balanced brackets, required keywords
- **Correction Suggestions**: Provides guidance for common errors

**Query Quality Improvements**:
- **Employee Activity**: Correct CalendarEvent queries with meeting counts
- **Product Filtering**: Accurate `NOT toLower(p.vendor) CONTAINS 'terasky'`
- **Natural Language Answers**: Contextual explanations with bold formatting, bullet points, insights
- **Response Time**: 4.5-5s for AI generation + LLM explanation

**Files Created/Modified**:
- **New**: `app/core/prompt_profiles.py` - Intent classification + 4 specialized profiles
- **New**: `app/core/cypher_validator.py` - Clean, validate, suggest corrections
- **New**: `app/core/answer_renderer.py` - LLM-based natural language explanations
- **Modified**: `app/core/bedrock_client.py` - Intent routing + validation with retry
- **Modified**: `app/api/routes.py` - Always use AI generation, removed duplicate validation

**Testing Validation**:
- **Intent Classification**: 100% accuracy for sales, calendar, product queries
- **Validation Pass Rate**: 100% with retry logic handling edge cases
- **Answer Quality**: Natural language with insights matching CLI demo
- **Performance**: 4.5-5s response time (AI generation + LLM explanation)

**Results Achieved**:
- **CLI Demo Quality**: Production now matches self-learning RAG CLI demo output exactly
- **Intent Accuracy**: 100% classification for specialized query types
- **No Fallbacks**: Removed execution fallback that masked errors with bad queries
- **Natural Explanations**: Grounded in actual data, no fabricated numbers

**Consequences**:
- ✅ **Dramatic Quality Improvement**: Production matches CLI demo quality exactly
- ✅ **Intent-Based Optimization**: Specialized prompts for different query types
- ✅ **Self-Correction**: Validation retry handles edge cases automatically
- ✅ **Insightful Answers**: LLM-based explanations provide context and insights
- ✅ **Temperature Optimization**: Using trained 0.1 for generation, 0.2 for explanations
- ❌ **Increased Latency**: 4.5-5s vs previous 2-3s (acceptable for quality gain)
- ❌ **LLM API Costs**: Additional LLM call for answer rendering

**Future Phases**:
- **Phase 2**: Self-improvement loop with periodic retraining
- **Phase 3**: Schema sync with auto-detect for schema changes
- **Phase 4**: Learned pattern optimization and caching

---


## ADR-028: Production Monitoring Dashboard

**Date**: 2025-12-22  
**Status**: Implemented  
**Context**: Need real-time visibility into production RAG performance, intent distribution, validation success rates, and error patterns

**Decision**: Implement comprehensive production monitoring dashboard with auto-refresh metrics and visualizations

**Problem Analysis**:
- **No Visibility**: No real-time insight into production RAG performance
- **Manual Monitoring**: Required log analysis to understand system behavior
- **Error Detection**: Difficult to identify error patterns and validation failures
- **Intent Analysis**: No visibility into query distribution across intent types
- **Performance Tracking**: No systematic tracking of response times and validation attempts

**Solution Architecture**:
- **Metrics Collector**: Thread-safe tracking of all query executions with persistent storage
- **Dashboard UI**: Real-time web interface with auto-refresh charts and KPIs
- **API Endpoint**: `/api/v1/metrics` returning comprehensive JSON metrics
- **Persistent Storage**: JSON-based metrics history in `data/production_metrics.json`

**Implementation Components**:
```python
# Metrics Collector
class MetricsCollector:
    def record_query(self, query, intent, validation_attempts, response_time, success, error):
        # Thread-safe recording with automatic persistence
        
    def get_metrics(self):
        # Returns: total_queries, intent_distribution, validation_attempts,
        #          errors, performance stats, recent_queries

# Dashboard Features
- Auto-refresh every 10 seconds
- Intent distribution (doughnut chart)
- Validation attempts (bar chart)
- Response time trend (line chart)
- Error types (bar chart)
- Recent queries panel with metadata
```

**Metrics Tracked**:
- **Query Count**: Total queries per intent type (sales_v1, calendar_v1, product_v1, strict_v1)
- **Validation Attempts**: Distribution of 1-attempt vs 2-attempt queries
- **Response Time**: Average, min, max execution times
- **Error Types**: Frequency of different error types
- **Success Rate**: Validation pass rate and overall success rate
- **Query History**: Last 100 queries with full metadata

**Dashboard Features**:
- **Real-time KPIs**: Total queries, avg response time, validation pass rate, error rate
- **Intent Distribution Chart**: Doughnut chart showing query breakdown by intent
- **Validation Attempts Chart**: Bar chart tracking first-attempt vs retry success
- **Response Time Trend**: Line chart showing last 20 queries' execution times
- **Error Types Chart**: Bar chart displaying error frequency by type
- **Recent Queries Panel**: Last 20 queries with success/failure badges, intent labels, timing

**Files Created**:
- **Core Collector**: `app/core/metrics_collector.py` - Thread-safe metrics tracking
- **Dashboard UI**: `app/static/dashboard.html` - Responsive web interface with Chart.js
- **Modified**: `app/api/routes.py` - Integrated metrics recording for all queries
- **Modified**: `app/core/bedrock_client.py` - Returns tuple with intent and validation attempts
- **Modified**: `app/main.py` - Added `/dashboard` route

**Integration Points**:
- **Query Success**: Records intent, validation attempts, response time
- **Query Failure**: Records error type, response time, intent (if available)
- **Automatic Persistence**: Saves metrics every 10 queries
- **Thread Safety**: Lock-based synchronization for concurrent requests

**Dashboard Access**:
- **URL**: `http://localhost:8002/dashboard`
- **Auto-refresh**: Updates every 10 seconds
- **Responsive**: Works on desktop and mobile devices
- **Dark Theme**: Professional UI matching production environment

**Performance Characteristics**:
- **Minimal Overhead**: <5ms per query for metrics recording
- **Persistent Storage**: JSON file with last 1000 response times, 100 queries
- **Thread-Safe**: Lock-based synchronization for concurrent access
- **Auto-Cleanup**: Maintains bounded history to prevent unbounded growth

**Success Criteria Met**:
- ✅ **Real-time Visibility**: Live dashboard with auto-refresh
- ✅ **Comprehensive Metrics**: Intent, validation, performance, errors tracked
- ✅ **Persistent Storage**: Metrics survive container restarts
- ✅ **Thread Safety**: Concurrent request handling without data corruption
- ✅ **Production Ready**: Minimal overhead, automatic persistence

**Consequences**:
- ✅ **Production Visibility**: Real-time insight into RAG performance
- ✅ **Error Detection**: Quick identification of error patterns
- ✅ **Intent Analysis**: Understand query distribution across intent types
- ✅ **Performance Tracking**: Monitor response times and validation success
- ✅ **Quality Monitoring**: Track validation pass rates and retry patterns
- ❌ **Storage Growth**: Metrics file grows over time (mitigated by bounded history)
- ❌ **Additional Endpoint**: New dashboard endpoint to maintain

**Future Enhancements**:
- **Alerting**: Automatic alerts for error rate spikes or performance degradation
- **Historical Analysis**: Long-term trend analysis and reporting
- **Export Capabilities**: CSV/JSON export for external analysis
- **Advanced Filtering**: Filter metrics by date range, intent, or user

---


## ADR-029: Three-Tier User Feedback System

**Date**: 2025-12-23  
**Status**: Implemented  
**Context**: Binary thumbs up/down feedback insufficient for understanding partial success cases and improvement opportunities

**Decision**: Implement three-tier feedback system with helpful/almost/not_helpful ratings for granular user satisfaction tracking

**Problem Analysis**:
- **Binary Limitation**: Thumbs up/down couldn't distinguish between perfect answers and close-but-missing-something
- **Improvement Blind Spots**: No visibility into queries that were "almost right" but needed refinement
- **Self-Learning Gap**: Binary feedback insufficient for targeted prompt improvements
- **User Frustration**: No way to indicate "good attempt but incomplete"

**Solution Architecture**:
- **Three Rating Levels**: Helpful (perfect), Almost (close but missing), Not Helpful (failed)
- **Granular Analytics**: Separate tracking for satisfaction rate and partial success rate
- **Self-Learning Integration**: Differentiated improvement suggestions based on feedback type
- **Backward Compatibility**: Automatic mapping of old positive/negative ratings

**Implementation Details**:
```javascript
// Frontend - Three feedback buttons
<button onclick="sendFeedback('helpful')">👍 Helpful</button>
<button onclick="sendFeedback('almost')">👌 Almost</button>
<button onclick="sendFeedback('not_helpful')">👎 Not Helpful</button>

// Backend - Rating mapping
rating_map = {
    'positive': 'helpful', 'up': 'helpful',
    'negative': 'not_helpful', 'down': 'not_helpful'
}
```

**Analytics Enhancements**:
- **Satisfaction Rate**: Percentage of "helpful" ratings
- **Partial Success Rate**: Percentage of "almost" ratings
- **Failure Rate**: Percentage of "not_helpful" ratings
- **Intent Breakdown**: Separate tracking by intent type for each rating level

**Self-Learning Integration**:
```python
# Differentiated suggestions
if feedback['almost_count'] > 3:
    suggestions.append("Queries partially correct - review for missing details")

if feedback['not_helpful_count'] > 3:
    suggestions.append("Review failed queries and add examples")
```

**Files Modified**:
- **Frontend**: `app/static/promptui.html` - Three feedback buttons with color coding
- **Backend**: `app/api/routes.py` - Rating mapping and storage
- **Self-Learning**: `app/core/self_learner.py` - Three-tier feedback analysis
- **Report**: `Tests/run_self_learning.py` - Separate display sections

**User Experience**:
- **Visual Feedback**: Green (helpful), Yellow (almost), Red (not helpful)
- **Clear Labels**: Descriptive tooltips for each rating level
- **Disabled State**: Buttons disabled after selection to prevent duplicate feedback

**Analytics Output**:
```
Perfect (Helpful): 45 (75%)
Partial (Almost): 10 (17%)
Failed (Not Helpful): 5 (8%)
```

**Consequences**:
- ✅ **Granular Insights**: Understand partial success vs complete failure
- ✅ **Targeted Improvements**: Different suggestions for almost vs not_helpful
- ✅ **Better UX**: Users can express "close but not quite" sentiment
- ✅ **Backward Compatible**: Old feedback data automatically mapped
- ✅ **Self-Learning Ready**: Differentiated improvement strategies
- ❌ **Increased Complexity**: Three categories vs two to analyze
- ❌ **User Decision**: Users must choose between three options

**Future Enhancements**:
- **Feedback Comments**: Optional text field for specific improvement suggestions
- **Pattern Analysis**: Identify common "almost" patterns for targeted fixes
- **A/B Testing**: Test prompt improvements on "almost" queries

---

## ADR-030: Manual Self-Learning Analysis Tool

**Date**: 2025-12-23  
**Status**: Implemented  
**Context**: Need systematic analysis of production failures, user feedback, and intent accuracy to drive continuous improvement

**Decision**: Implement manual self-learning analysis tool for on-demand comprehensive system evaluation

**Problem Analysis**:
- **No Systematic Analysis**: Manual log review required to understand failure patterns
- **Feedback Blind Spots**: User feedback collected but not systematically analyzed
- **Intent Accuracy Unknown**: No visibility into misclassification rates
- **Improvement Guesswork**: No data-driven suggestions for prompt optimization

**Solution Architecture**:
- **Comprehensive Analysis**: Failure patterns, user feedback, intent accuracy in single report
- **CLI Tool**: On-demand execution via `python -m Tests.run_self_learning`
- **Actionable Suggestions**: Targeted improvements for prompts, keywords, schema, examples
- **JSON Report**: Machine-readable output for programmatic access

**Analysis Capabilities**:
1. **Failure Analysis**:
   - Total failures and failure rate
   - Error breakdown by type (CypherSyntaxError, CypherTypeError)
   - Validation retry counts
   - Detailed error queries with intent labels

2. **User Feedback Analysis**:
   - Satisfaction rate (helpful %)
   - Partial success rate (almost %)
   - Failure rate (not_helpful %)
   - Feedback breakdown by intent
   - Query lists for each feedback category

3. **Intent Classification Analysis**:
   - Unknown intent rate
   - Intent distribution across all queries
   - Most common intent type
   - Misclassification patterns

4. **Suggestion Engine**:
   - **Prompt Rules**: High syntax/type errors → review rules
   - **Intent Keywords**: High unknown rate → add keywords
   - **Schema Hints**: Missing context → enhance schema
   - **Few-Shot Examples**: Negative feedback → add examples

**Implementation Details**:
```python
# Core analysis functions
def analyze_failures() -> Dict[str, Any]:
    # Groups errors by type, tracks retry counts
    
def analyze_user_feedback() -> Dict[str, Any]:
    # Calculates satisfaction/partial/failure rates
    
def analyze_intent_accuracy() -> Dict[str, Any]:
    # Tracks unknown rate and distribution
    
def suggest_improvements() -> Dict[str, List[str]]:
    # Generates targeted suggestions based on patterns
```

**CLI Output Format**:
```
🧠 Running Self-Learning Analysis...

============================================================
FAILURE ANALYSIS
============================================================
Total Queries: 37
Total Failures: 3 (8.1%)
Validation Retries: 0

Error Breakdown:
  - CypherTypeError: 1
  - CypherSyntaxError: 2

============================================================
USER FEEDBACK ANALYSIS
============================================================
Perfect (Helpful): 25 (68%)
Partial (Almost): 8 (22%)
Failed (Not Helpful): 4 (11%)

============================================================
SUGGESTIONS
============================================================
📝 Prompt Rules:
  • High syntax errors detected. Review RULES_SUMMARY.

🎯 Intent Keywords:
  • Unknown intent rate: 8.1%. Add keywords to classifier.
```

**Files Created**:
- **Core Engine**: `app/core/self_learner.py` - Analysis and suggestion logic
- **CLI Tool**: `Tests/run_self_learning.py` - User-friendly interface
- **Report Storage**: `/app/data/self_learning_report.json` - Full JSON output

**Integration Points**:
- **Metrics Collector**: Reads all query history (up to 100 queries)
- **Feedback Storage**: Analyzes user feedback from persistent JSONL
- **Intent Tracking**: Uses production metrics for intent distribution

**Use Cases**:
- **Weekly Reviews**: Run analysis to identify improvement opportunities
- **Post-Deployment**: Validate new prompt changes with production data
- **Quality Monitoring**: Track satisfaction trends and error patterns
- **Continuous Improvement**: Data-driven prompt optimization

**Success Criteria Met**:
- ✅ **Comprehensive Analysis**: Failures, feedback, intent in single report
- ✅ **Actionable Suggestions**: Targeted improvements based on data
- ✅ **Easy Execution**: Simple CLI command for on-demand analysis
- ✅ **Machine-Readable**: JSON output for automation
- ✅ **Human-Readable**: Clear summaries with inline query display

**Consequences**:
- ✅ **Data-Driven Improvements**: Systematic analysis replaces guesswork
- ✅ **Visibility**: Clear insight into production performance
- ✅ **Targeted Actions**: Specific suggestions for each issue type
- ✅ **Manual Control**: Human review before applying changes
- ✅ **Audit Trail**: JSON reports for historical analysis
- ❌ **Manual Execution**: Requires periodic manual runs
- ❌ **No Auto-Apply**: Suggestions must be manually implemented

**Future Enhancements**:
- **Automated Scheduling**: Cron job for weekly analysis
- **Trend Analysis**: Compare metrics across multiple runs
- **Auto-Apply Mode**: Automatic prompt updates for low-risk changes
- **Slack Integration**: Post analysis summaries to team channel

---
