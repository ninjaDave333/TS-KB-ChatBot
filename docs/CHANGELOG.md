# Changelog

All notable changes to the TSKB-RAG Chatbot System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Docker deployment configuration
- API documentation and testing
- RAGAS Phase 2: Advanced metrics and automated CI/CD integration
- Query result caching integration
- Automated performance alerting

## [0.7.0] - 2025-11-17

### Added
- **Performance Monitoring**: Comprehensive metrics tracking for query execution
- **Cache Manager**: In-memory caching system for query results and schema data
- **Health Monitoring**: Detailed health status with performance indicators
- **Metrics Endpoints**: `/metrics` and `/health/detailed` for system monitoring
- **Query Type Analytics**: Performance breakdown by query type (count, list, vendor)
- **Error Tracking**: Automatic error logging and performance impact analysis

### Changed
- **API Routes**: Integrated performance monitoring into all query endpoints
- **Response Tracking**: All queries now tracked with execution time and confidence
- **Health Checks**: Enhanced with performance-based status indicators

### Performance
- **Monitoring Coverage**: 100% query tracking with detailed metrics
- **Cache Ready**: Infrastructure for 5-minute query result caching
- **Health Thresholds**: Automated status based on success rate and response time
- **Error Analysis**: Comprehensive error tracking and categorization

### Documentation
- Added performance monitoring test script
- Enhanced system monitoring capabilities
- Production readiness checklist items completed

## [0.6.0] - 2025-11-17

### Added
- **Intelligent Answer Generator**: Context-aware response formatting with query-type detection
- **RAGAS Phase 1 Completion**: Achieved breakthrough RAG performance improvements
- **Query-Type Detection**: Automatic classification of count, list, and vendor queries
- **Contextual Response Formatting**: Business-relevant answers replacing generic responses
- **Israeli Client Query Fixes**: Proper region-based filtering (c.region = 'IL')
- **Enhanced Query Generation**: Improved Cypher generation with better context rules

### Changed
- **Answer Quality**: Generic "Query executed successfully" → Specific contextual answers
- **API Response Format**: Integrated intelligent answer generator in routes
- **Query Generation Rules**: Enhanced schema descriptions with Israeli client patterns
- **Context Enhancement**: Business data prioritized over technical metadata

### Fixed
- **Israeli Client Searches**: Now use c.region = 'IL' instead of c.country = 'Israel'
- **Employee Node Usage**: Corrected to use Employee node for account managers
- **Count Query Detection**: Proper classification with explicit count keywords
- **Query Type Misclassification**: List queries no longer misclassified as count queries

### Performance
- **Context Recall**: 0.000 → 1.000 (PERFECT - 100% improvement)
- **Answer Correctness**: 0.030 → 0.921 (EXCELLENT - 2970% improvement)
- **Faithfulness**: 0.667 → 1.000 (PERFECT - 50% improvement)
- **Answer Relevancy**: 0.059 → 0.776 (EXCELLENT - 1215% improvement)
- **Context Precision**: 0.333 → 0.546 (64% improvement)

### Documentation
- Updated ADR.md with ADR-015: Intelligent Answer Generation
- Added RAGAS Phase 1 results summary
- Enhanced schema documentation with Israeli client patterns

## [0.5.0] - 2025-11-17

### Added
- RAGAS (Retrieval Augmented Generation Assessment) integration for comprehensive RAG evaluation
- Five RAG-specific evaluation metrics: faithfulness, answer relevancy, context precision, context recall, answer correctness
- Automated evaluation script (Tests/ragas_evaluation.py) with AWS Bedrock LLM integration
- PowerShell runner script (Tests/run_ragas_evaluation.ps1) for easy execution
- Comprehensive evaluation dataset with ground truth references
- Detailed evaluation reporting with actionable insights and recommendations

### Changed
- Enhanced requirements.txt with RAGAS dependencies (ragas, langchain-aws, datasets, pandas)
- Extended testing capabilities beyond syntax validation to include answer quality assessment
- Added systematic benchmarking against industry-standard RAG metrics

### Documentation
- Updated ADR.md with ADR-014: RAGAS Integration decision
- Added comprehensive evaluation methodology documentation
- Enhanced testing strategy with RAG-specific quality metrics

## [0.4.0] - 2025-11-12

### Added
- OPPORTUNITY.close_date field for accurate temporal queries
- Distinction between close_date (actual deal close) and purchased_date (line item creation)
- Updated query patterns for 2025 deal tracking

### Changed
- Schema descriptions now use close_date for all temporal queries
- Year filtering changed from CONTAINS to proper date range comparisons
- Query examples updated to use close_date >= '2025-01-01' AND close_date < '2026-01-01'

### Fixed
- Temporal queries now use correct close_date field instead of purchased_date
- 2025 deal tracking now accurately reflects actual close dates

## [0.3.1] - 2025-11-12

### Fixed
- Cost field mapping: Changed from non-existent `o.amount` to correct `o.total_price` field
- Schema descriptions updated with correct cost aggregation pattern
- All 1,081 Closed Won deals now properly calculate total revenue ($293.8M)

## [0.3.0] - 2025-11-12

### Added
- Query validation layer with auto-fix for common syntax errors
- Automatic filter injection for year and vendor queries
- Model comparison framework for testing different LLMs
- Batch testing suite with 10 diverse query patterns
- Configurable model selection via AWS_BEDROCK_MODEL_ID env var

### Changed
- Switched to Claude Sonnet 4 for superior query generation
- Simplified prompts to prevent token truncation
- Increased max_tokens to 4096 for complete query generation
- Multi-level fallback chain (AI → Validation → Rules → Execution)

### Fixed
- Token truncation causing incomplete queries (200 → 4096 tokens)
- Missing year filters now auto-injected via regex extraction
- Missing vendor filters now auto-injected programmatically
- Trailing comma syntax errors caught and fixed by validator
- Wrong date field (close_date → purchased_date) auto-corrected

### Performance
- Query success rate: 10% → 70% (7x improvement)
- Syntax error rate: 70% → 0% (eliminated)
- Average response time: <6 seconds

## [0.2.0] - 2025-11-12

### Added
- Enhanced schema descriptions for improved AI query generation
- Comprehensive node and relationship descriptions in schema discovery
- AI-powered Cypher query generation with contextual understanding
- Test suite for WIX client queries demonstrating enhanced capabilities

### Changed
- Schema discovery now includes detailed descriptions and usage patterns
- Improved AI context with critical properties and common query patterns
- Enhanced relationship descriptions for better query understanding

### Fixed
- AI query generation accuracy for client-specific searches
- Better handling of case-insensitive client name matching

## [0.1.0] - 2025-11-10

### Added
- Initial project structure and documentation
- Architecture Decision Record (ADR.md) with 10 key decisions
- Product Requirements Document (PRD.md) with comprehensive specifications
- Schema synchronization guide (SchemaSync.md) updated to v2.3.0
- Client schema example documentation
- Project rules and validation guidelines
- Environment configuration templates

### Documentation
- Complete system architecture design in tskgRAG.md
- Detailed Neo4j schema with 9 node types and 9 relationship types
- Query strategy documentation for hybrid Cypher + Vector search
- User persona definitions and use cases
- Technical requirements and success criteria
- Development timeline and milestone planning

### Infrastructure
- Docker network configuration (TS_AI_network)
- Environment variable templates
- Git repository initialization with proper .gitignore
- Amazon Q development rules and guidelines

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 0.7.0 | 2025-11-17 | Production readiness: Performance monitoring and caching |
| 0.6.0 | 2025-11-17 | RAGAS Phase 1 completion and intelligent answer generation |
| 0.5.0 | 2025-11-17 | RAGAS integration for comprehensive RAG evaluation |
| 0.4.0 | 2025-11-12 | Added close_date field for temporal queries |
| 0.3.1 | 2025-11-12 | Fixed cost field mapping (amount → total_price) |
| 0.3.0 | 2025-11-12 | Query validation and filter injection |
| 0.2.0 | 2025-11-12 | Enhanced schema descriptions for AI query generation |
| 0.1.0 | 2025-11-10 | Initial project setup and documentation |

---

## Release Notes Format

### Added
- New features and capabilities

### Changed
- Changes to existing functionality

### Deprecated
- Features that will be removed in future versions

### Removed
- Features that have been removed

### Fixed
- Bug fixes and corrections

### Security
- Security-related changes and improvements

---

**Changelog Maintained By**: TeraSky AI Team  
**Last Updated**: 2025-11-10