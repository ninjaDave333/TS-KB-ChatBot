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

---

## Future Decisions

### Pending Decisions
- **Authentication Strategy**: OAuth2 vs API Keys vs JWT
- **Rate Limiting**: Strategy and implementation approach
- **Monitoring**: Metrics collection and alerting strategy
- **Testing Strategy**: Unit vs Integration vs E2E testing approach

### Deferred Decisions
- **Multi-tenancy**: Support for multiple organizations
- **Query History**: Storage and analysis of user queries
- **Advanced Analytics**: Query pattern analysis and optimization

---

**Last Updated**: 2025-11-10  
**Next Review**: 2025-12-10