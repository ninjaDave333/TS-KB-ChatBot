# Changelog

All notable changes to the TSKB-RAG Chatbot System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Docker deployment configuration
- API documentation and testing

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