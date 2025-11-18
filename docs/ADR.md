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
| 017 | Dynamic RAG Enhancement | Planned | Critical |

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
- **Automatic Backup**: Save patterns after every learning event
- **Export/Import**: Full learning data backup and restoration
- **Query History**: Last 100 queries maintained for pattern detection

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

**Last Updated**: 2025-11-17  
**Next Review**: 2025-12-17