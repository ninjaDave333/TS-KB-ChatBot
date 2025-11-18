# TSKB-RAG Schema Synchronization Guide

**Version**: 2.6.0  
**Last Updated**: 2025-11-18  
**Purpose**: Complete schema reference for services consuming TSKB-RAG Neo4j knowledge graph

---

## Overview

This document provides a comprehensive schema definition for all node types and relationships in the TSKB-RAG knowledge graph. Use this as the authoritative source for integrating with TSKB data.

**Total Node Types**: 12 (Region, Skill, BU, Employee, Product, Vendor, Client, Compliance, SyncMetadata, Recording, CalendarEvent, ScanMetadata)  
**Total Relationship Types**: 12 (LOCATED_IN, HAS_SKILL, BELONGS_TO, MAKES, MANAGED_BY, SUPPORTS, REQUIRES_SKILL, OPPORTUNITY, HAS_INSTALLED, LINKED_TO, OWNER_OF, INVITED_TO)

---

## Node Schemas

### 1. Region Node

**Label**: `Region`  
**Source**: CSV (Human-editable)  
**Count**: 3 nodes

**Properties**:
```json
{
  "name": "string (UNIQUE)",
  "description": "string",
  "source": "tskb-csv",
  "created_at": "datetime"
}
```

**Example**:
```json
{
  "name": "IL",
  "description": "Israel",
  "source": "tskb-csv",
  "created_at": "2025-11-04T10:00:00Z"
}
```

**Valid Values**: `IL`, `US`, `UK`

**Relationships**:
- `(Employee)-[:LOCATED_IN]->(Region)`
- `(Client)-[:LOCATED_IN]->(Region)`

---

### 2. Skill Node

**Label**: `Skill`  
**Source**: CSV (Human-editable)  
**Count**: 19 nodes

**Properties**:
```json
{
  "name": "string (UNIQUE)",
  "description": "string",
  "category": "string",
  "source": "tskb-csv",
  "created_at": "datetime"
}
```

**Example**:
```json
{
  "name": "kubernetes",
  "description": "Container orchestration",
  "category": "DevOps",
  "source": "tskb-csv",
  "created_at": "2025-11-04T10:00:00Z"
}
```

**Categories**: `DevOps`, `Cloud`, `Security`, `Data`, `Infrastructure`

**Relationships**:
- `(Employee)-[:HAS_SKILL]->(Skill)`
- `(Product)-[:REQUIRES_SKILL]->(Skill)`

---

### 3. BU (Business Unit) Node

**Label**: `BU`  
**Source**: Salesforce API (Groups/Teams)  
**Count**: 19 nodes

**Properties**:
```json
{
  "name": "string (UNIQUE)",
  "source": "tskb-sf_api",
  "sf_source": "string (group|team)",
  "created_at": "datetime"
}
```

**Example**:
```json
{
  "name": "Cloud Native",
  "source": "tskb-sf_api",
  "sf_source": "team",
  "created_at": "2025-11-04T10:00:00Z"
}
```

**SF Source Types**:
- `group`: Salesforce Group (primary BU)
- `team`: Salesforce Team (secondary BU)

**Relationships**:
- `(Employee)-[:BELONGS_TO]->(BU)`
- `(Product)-[:BELONGS_TO]->(BU)`

---

### 4. Employee Node

**Label**: `Employee`  
**Source**: MS Graph API + Salesforce API  
**Count**: 285 nodes

**Core Properties**:
```json
{
  "azure_id": "string (PRIMARY KEY)",
  "name": "string",
  "email": "string",
  "title": "string",
  "source": "tskb-ms_api",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Microsoft Graph Properties** (prefix: `ms_`):
```json
{
  "ms_id": "string",
  "ms_display_name": "string",
  "ms_mail": "string",
  "ms_user_principal_name": "string",
  "ms_job_title": "string",
  "ms_department": "string",
  "ms_office_location": "string",
  "ms_mobile_phone": "string",
  "ms_business_phones": ["string"],
  "ms_preferred_language": "string",
  "ms_account_enabled": "boolean"
}
```

**Salesforce Properties** (prefix: `sf_`):
```json
{
  "sf_id": "string",
  "sf_username": "string",
  "sf_is_active": "boolean",
  "sf_team": "string",
  "sf_group": "string",
  "sf_tech_area": "string",
  "sf_seniority_level": "string",
  "sf_location": "string",
  "sf_default_geo": "string",
  "sf_manager_id": "string",
  "sf_phone": "string",
  "sf_mobile_phone": "string"
}
```

**Complete Example**:
```json
{
  "azure_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "John Doe",
  "email": "john.doe@terasky.com",
  "title": "Senior DevOps Engineer",
  "source": "tskb-ms_api",
  "ms_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "ms_display_name": "John Doe",
  "ms_account_enabled": true,
  "ms_department": "Cloud Native",
  "ms_office_location": "IL",
  "sf_id": "0051234567890ABC",
  "sf_team": "DevSecOps",
  "sf_group": "Cloud",
  "sf_tech_area": "Kubernetes",
  "sf_seniority_level": "Senior",
  "sf_location": "IL",
  "created_at": "2025-11-04T10:00:00Z",
  "updated_at": "2025-11-04T10:00:00Z"
}
```

**Relationships**:
- `(Employee)-[:LOCATED_IN]->(Region)` - via `sf_location`, `sf_default_geo`, or `ms_office_location`
- `(Employee)-[:BELONGS_TO]->(BU)` - via `sf_team`, `sf_group`, or `ms_department`
- `(Employee)-[:HAS_SKILL]->(Skill)` - legacy/manual
- `(Client)-[:MANAGED_BY]->(Employee)` - via `sf_id` or `email`

---

### 5. Product Node

**Label**: `Product`  
**Source**: Salesforce API (Product2 + OpportunityLineItem + Asset)  
**Count**: 425+ nodes (396 SF API + 29+ opportunity/asset-derived)

**Core Properties**:
```json
{
  "name": "string (UNIQUE)",
  "vendor": "string",
  "source": "tskb-sf_api",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Salesforce Properties** (prefix: `sf_`):
```json
{
  "sf_id": "string",
  "sf_name": "string",
  "sf_product_code": "string",
  "sf_description": "string",
  "sf_is_active": "boolean",
  "sf_family": "string",
  "sf_vendor": "string",
  "sf_type": "string",
  "sf_sub_types": "string",
  "sf_deal_components": "string",
  "sf_line_of_business": "string",
  "sf_vendor_account": "string",
  "sf_license_type_required": "string",
  "sf_business_unit": "string",
  "sf_delivery_team": "string",
  "sf_strategic_vendor": "boolean",
  "sf_product_bucket": "string",
  "sf_created_date": "string (ISO)",
  "sf_last_modified_date": "string (ISO)",
  "previous_sf_ids": ["string"]
}
```

**Version Tracking**:
- `previous_sf_ids`: Array of old Salesforce IDs when product is re-created
- Product MERGE by `name` (stable), SF ID updated to latest version

**Complete Example**:
```json
{
  "name": "Terraform Enterprise",
  "vendor": "HashiCorp",
  "source": "tskb-sf_api",
  "sf_id": "01t1234567890ABC",
  "sf_name": "Terraform Enterprise",
  "sf_product_code": "TF-ENT",
  "sf_description": "Infrastructure as Code platform",
  "sf_is_active": true,
  "sf_family": "Cloud Automation",
  "sf_vendor": "HashiCorp",
  "sf_type": "Software",
  "sf_business_unit": "Cloud Platform",
  "sf_delivery_team": "DevSecOps",
  "sf_strategic_vendor": true,
  "sf_product_bucket": "IaC",
  "created_at": "2025-11-04T10:00:00Z",
  "updated_at": "2025-11-04T10:00:00Z"
}
```

**Relationships**:
- `(Vendor)-[:MAKES]->(Product)` - via `vendor` or `sf_vendor`
- `(Product)-[:BELONGS_TO]->(BU)` - via `sf_business_unit`
- `(Product)-[:REQUIRES_SKILL]->(Skill)` - via `sf_delivery_team`
- `(Product)-[:SUPPORTS]->(Compliance)` - legacy/manual
- `(Client)-[:PURCHASED]->(Product)` - via OpportunityLineItem
- `(Client)-[:HAS_INSTALLED]->(Product)` - via Asset

---

### 6. Vendor Node

**Label**: `Vendor`  
**Source**: Auto-created from Products  
**Count**: 69 nodes

**Properties**:
```json
{
  "name": "string (UNIQUE)",
  "source": "tskb-sf_api",
  "created_at": "datetime"
}
```

**Example**:
```json
{
  "name": "HashiCorp",
  "source": "tskb-sf_api",
  "created_at": "2025-11-04T10:00:00Z"
}
```

**Relationships**:
- `(Vendor)-[:MAKES]->(Product)`

---

### 7. Client Node

**Label**: `Client`  
**Source**: Salesforce API (Accounts + OpportunityLineItem + Asset)  
**Count**: 549+ nodes (115 SF API + 432+ opportunity/asset-derived + 2 legacy)

**Core Properties**:
```json
{
  "name": "string",
  "source": "tskb-sf_api",
  "region": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Standard Salesforce Properties** (prefix: `sf_`):
```json
{
  "sf_id": "string (UNIQUE)",
  "sf_name": "string",
  "sf_type": "string",
  "sf_billing_country": "string",
  "sf_is_partner": "boolean",
  "sf_owner_id": "string",
  "sf_owner_email": "string (cleaned)",
  "sf_last_activity_date": "string (ISO)",
  "sf_last_modified_date": "string (ISO)"
}
```

**Custom Salesforce Properties**:
```json
{
  "sf_industry": "string",
  "sf_company_size": "string",
  "sf_named_account": "string",
  "sf_account_status": "string",
  "sf_active_contract": "boolean",
  "sf_account_source": "string",
  "sf_domain_names": "string",
  "sf_website": "string",
  "sf_account_manager_cloud_id": "string"
}
```

**Complete Example**:
```json
{
  "name": "Wix.com",
  "source": "tskb-sf_api",
  "region": "IL",
  "sf_id": "0011234567890ABC",
  "sf_name": "Wix.com",
  "sf_type": "Customer",
  "sf_billing_country": "Israel",
  "sf_is_partner": false,
  "sf_owner_id": "0051234567890DEF",
  "sf_owner_email": "john.doe@terasky.com",
  "sf_industry": "Technology",
  "sf_company_size": "Enterprise (1000+ employees)",
  "sf_named_account": "Yes",
  "sf_account_status": "Active",
  "sf_active_contract": true,
  "sf_website": "https://www.wix.com",
  "created_at": "2025-11-09T10:00:00Z",
  "updated_at": "2025-11-09T10:00:00Z"
}
```

**Country-to-Region Mapping**:
- `Israel` → `IL`
- `United States`, `USA` → `US`
- `Germany`, `United Kingdom`, `UK` → `UK`
- Default: `US`

**Relationships**:
- `(Client)-[:LOCATED_IN]->(Region)` - via country mapping
- `(Client)-[:MANAGED_BY]->(Employee)` - via `sf_owner_id` or `sf_owner_email`
- `(Client)-[:PURCHASED]->(Product)` - via OpportunityLineItem
- `(Client)-[:HAS_INSTALLED]->(Product)` - via Asset

---

### 8. Compliance Node

**Label**: `Compliance`  
**Source**: CSV (Human-editable) - Legacy  
**Count**: Variable (legacy data)

**Properties**:
```json
{
  "name": "string (UNIQUE)",
  "description": "string",
  "source": "tskb-csv",
  "created_at": "datetime"
}
```

**Example**:
```json
{
  "name": "SOC2",
  "description": "Service Organization Control 2",
  "source": "tskb-csv",
  "created_at": "2025-11-09T10:00:00Z"
}
```

**Relationships**:
- `(Product)-[:SUPPORTS]->(Compliance)`

---

### 9. SyncMetadata Node

**Label**: `SyncMetadata`  
**Source**: System-generated  
**Count**: Variable (per import type)

**Properties**:
```json
{
  "type": "string (UNIQUE)",
  "last_run": "datetime",
  "status": "string",
  "processed": "integer",
  "created": "integer",
  "updated": "integer",
  "skipped": "integer",
  "errors": "integer",
  "error_details": "string"
}
```

**Import Types**:
- `employee_import`
- `product_import`
- `client_import`
- `bu_import`

**Status Values**: `success`, `completed_with_errors`, `failed`

**Example**:
```json
{
  "type": "employee_import",
  "last_run": "2025-11-09T10:00:00Z",
  "status": "success",
  "processed": 285,
  "created": 285,
  "updated": 0,
  "skipped": 0,
  "errors": 0
}
```

---

## Relationship Types

### 1. LOCATED_IN
**Pattern**: `(Employee|Client)-[:LOCATED_IN]->(Region)`  
**Count**: 285 Employee + 549+ Client relationships

**Employee Sources**:
- `sf_location` (primary)
- `sf_default_geo` (secondary)
- `ms_office_location` (fallback)

**Client Sources**:
- `sf_billing_country` (mapped to region)

### 2. HAS_SKILL
**Pattern**: `(Employee)-[:HAS_SKILL]->(Skill)`  
**Count**: Variable (legacy/manual)

**Source**: Manual assignment or legacy data

### 3. BELONGS_TO
**Pattern**: `(Employee|Product)-[:BELONGS_TO]->(BU)`  
**Count**: 285 Employee + 396+ Product relationships

**Employee Sources**:
- `sf_team` (primary)
- `sf_group` (secondary)
- `ms_department` (fallback)

**Product Sources**:
- `sf_business_unit`

### 4. MAKES
**Pattern**: `(Vendor)-[:MAKES]->(Product)`  
**Count**: 396+ relationships

**Source**: `vendor` or `sf_vendor` property

### 5. MANAGED_BY
**Pattern**: `(Client)-[:MANAGED_BY]->(Employee)`  
**Count**: 549+ relationships

**Matching Logic**:
1. `sf_owner_id` → `sf_id` (primary)
2. `sf_owner_email` → `email` (secondary)
3. `sf_account_manager_cloud_id` → `azure_id` (tertiary)

### 6. SUPPORTS
**Pattern**: `(Product)-[:SUPPORTS]->(Compliance)`  
**Count**: Variable (legacy)

**Source**: Legacy/manual assignment

### 7. REQUIRES_SKILL
**Pattern**: `(Product)-[:REQUIRES_SKILL]->(Skill)`  
**Count**: 42+ relationships

**Source**: `sf_delivery_team` mapped to skills

### 8. PURCHASED
**Pattern**: `(Client)-[:PURCHASED]->(Product)`  
**Count**: Variable (OpportunityLineItem-derived)

**Source**: Salesforce OpportunityLineItem records

### 9. HAS_INSTALLED
**Pattern**: `(Client)-[:HAS_INSTALLED]->(Product)`  
**Count**: Variable (Asset-derived)

**Source**: Salesforce Asset records

---

## Data Sources Summary

### Primary APIs
1. **Microsoft Graph API** - Employee identity data
2. **Salesforce API** - Business data (Users, Products, Accounts, OpportunityLineItems, Assets)

### Human-Editable CSV
1. **regions.csv** - Geographic regions
2. **skills.csv** - Technical skills with categories

### Legacy Sources
1. **CoreNodeSchemas.xlsx** - Deprecated Excel import
2. **Manual relationships** - Compliance, legacy skills

---

## Learned Query Patterns (Production Data)

### Pattern Learning System
The TSKB-RAG system automatically learns successful query patterns and stores them for reuse. As of 2025-11-17, the system has learned **6 high-performance patterns** with 96.7% average success rate.

### Top Performing Patterns

#### 1. Israeli Client Management (90% success, 1.7s avg)
```cypher
MATCH (c:Client)-[:MANAGED_BY]->(e:Employee) 
WHERE c.region = "IL" 
AND e.name IS NOT NULL 
AND toLower(e.name) <> "unknown" 
RETURN c.sf_name as client_name, e.name as manager_name
```
**Usage**: Regional account management, territory planning

#### 2. External Meeting Analytics (100% success, 1.5s avg)
```cypher
MATCH (r:Recording)-[:LINKED_TO]->(c:CalendarEvent) 
WHERE size(c.externalParticipants) > 0 
RETURN count(r) as external_meetings_recorded
```
**Usage**: Client engagement tracking, external collaboration metrics

#### 3. Top Active Clients 2025 (100% success, 1.6s avg)
```cypher
MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product) 
WHERE o.opportunity_stage = 'Closed Won' 
AND o.close_date >= '2025-01-01' 
AND o.close_date < '2026-01-01' 
WITH c, count(o) as deal_count 
ORDER BY deal_count DESC 
LIMIT 10 
RETURN c.sf_name as client_name, deal_count
```
**Usage**: Strategic account identification, revenue opportunity analysis

#### 4. Vendor Portfolio Analytics (100% success, 2.2s avg)
```cypher
MATCH (p:Product) 
RETURN count(DISTINCT p.vendor) as vendor_count
```
**Usage**: Vendor portfolio management, strategic sourcing insights

**Complete Pattern Analysis**: See `docs/QueryPatterns-Analysis.md` for detailed performance metrics and business impact analysis.

---

## Query Examples for Integration

### Employee Queries

```cypher
-- Get all employees with their regions and BUs
MATCH (e:Employee)-[:LOCATED_IN]->(r:Region)
MATCH (e)-[:BELONGS_TO]->(bu:BU)
RETURN e.name, e.email, e.title, r.name as region, bu.name as business_unit
ORDER BY e.name

-- Find employees by skill
MATCH (e:Employee)-[:HAS_SKILL]->(s:Skill {name: 'kubernetes'})
RETURN e.name, e.title, e.email

-- Get employee's full profile
MATCH (e:Employee {azure_id: 'target-id'})
OPTIONAL MATCH (e)-[:LOCATED_IN]->(r:Region)
OPTIONAL MATCH (e)-[:BELONGS_TO]->(bu:BU)
OPTIONAL MATCH (e)-[:HAS_SKILL]->(s:Skill)
RETURN e, r, bu, collect(s) as skills
```

### Product Queries

```cypher
-- Get products with vendor and BU
MATCH (v:Vendor)-[:MAKES]->(p:Product)-[:BELONGS_TO]->(bu:BU)
RETURN p.name, v.name as vendor, bu.name as business_unit, p.sf_strategic_vendor
ORDER BY p.name

-- Find strategic vendor products
MATCH (p:Product)
WHERE p.sf_strategic_vendor = true
RETURN p.name, p.sf_vendor, p.sf_family

-- Get product relationships
MATCH (p:Product {name: 'target-product'})
OPTIONAL MATCH (v:Vendor)-[:MAKES]->(p)
OPTIONAL MATCH (p)-[:BELONGS_TO]->(bu:BU)
OPTIONAL MATCH (p)-[:REQUIRES_SKILL]->(s:Skill)
RETURN p, v, bu, collect(s) as required_skills
```

### Client Queries

```cypher
-- Get clients with account managers
MATCH (c:Client)-[:MANAGED_BY]->(e:Employee)
MATCH (c)-[:LOCATED_IN]->(r:Region)
RETURN c.name, e.name as account_manager, r.name as region
ORDER BY c.name

-- Find client product usage
MATCH (c:Client)-[rel:PURCHASED|HAS_INSTALLED]->(p:Product)
RETURN c.name, type(rel) as relationship_type, p.name as product
ORDER BY c.name, p.name

-- Get client full profile
MATCH (c:Client {sf_id: 'target-id'})
OPTIONAL MATCH (c)-[:MANAGED_BY]->(e:Employee)
OPTIONAL MATCH (c)-[:LOCATED_IN]->(r:Region)
OPTIONAL MATCH (c)-[rel:PURCHASED|HAS_INSTALLED]->(p:Product)
RETURN c, e, r, collect({product: p, relationship: type(rel)}) as products
```

### Sync Status Queries

```cypher
-- Check last import status
MATCH (s:SyncMetadata)
RETURN s.type, s.last_run, s.status, s.processed, s.errors
ORDER BY s.last_run DESC

-- Find failed imports
MATCH (s:SyncMetadata)
WHERE s.status <> 'success'
RETURN s.type, s.status, s.error_details
```

---

## Teams Recording Integration (NEW)

### Node Counts (Validated 2025-11-17)
- **Recording**: 490 nodes (Teams meeting recordings)
- **CalendarEvent**: 470 nodes (Meeting events)
- **ScanMetadata**: 2 nodes (Scan tracking)

### Key Relationships
- **LINKED_TO**: 490 (Recording → CalendarEvent)
- **OWNER_OF**: 468 (Employee → CalendarEvent)
- **INVITED_TO**: 1353 (Employee → CalendarEvent)

### Integration Status
- ✅ **Schema Validated**: All nodes and relationships confirmed
- ✅ **Employee Integration**: Uses existing Employee nodes (143 linked)
- ✅ **RAG Ready**: Query patterns and examples implemented
- ✅ **Documentation**: Complete integration guide available

### Query Examples
```cypher
-- Find processed recordings with transcripts
MATCH (r:Recording {status: 'processed'})
WHERE r.transcriptUrl <> '' AND r.transcriptUrl IS NOT NULL
RETURN r.name, r.title, r.transcriptUrl

-- Find employee's organized meetings
MATCH (e:Employee)-[:OWNER_OF]->(c:CalendarEvent)
WHERE toLower(e.name) CONTAINS 'john'
RETURN e.name, c.title, c.startTime
ORDER BY c.startTime DESC

-- Find meetings by participant
MATCH (c:CalendarEvent)
WHERE ANY(email IN c.internalParticipants WHERE email CONTAINS 'smith')
RETURN c.title, c.internalParticipants, c.startTime
```

## Authentication & Security

### OAuth Authentication (NEW - v1.1.0)
The TSKB-RAG system now requires Microsoft OAuth authentication for all access:

**Authentication Requirements**:
- **Domain Restriction**: Only `@terasky.com` users can access the system
- **Bearer Tokens**: All API requests must include `Authorization: Bearer <token>` header
- **Token Validation**: Server-side validation via Microsoft Graph API
- **Session Management**: Client-side token storage with automatic inclusion

**Protected Endpoints**:
- `GET /promptui` - Web interface requires authentication
- `POST /api/v1/query` - Main RAG API requires Bearer token
- **Unprotected**: `/health`, `/schema`, `/auth/*` endpoints

**Integration Impact**:
- **API Clients**: Must implement OAuth flow to obtain Bearer tokens
- **Service Integration**: Compatible with meetingsBot OAuth infrastructure
- **Multi-Service**: Same tokens work across TeraSky AI service ecosystem

**Authentication Flow**:
1. Redirect to `/auth/login` to get Microsoft OAuth URL
2. Complete OAuth flow via popup or redirect
3. Receive Bearer token from `/auth/callback`
4. Include token in all API requests: `Authorization: Bearer <token>`

**Error Handling**:
```json
// Missing token
{
  "error": "Authentication required",
  "code": "MISSING_TOKEN"
}

// Invalid/expired token
{
  "error": "Token validation failed", 
  "code": "TOKEN_VALIDATION_FAILED"
}
```

**Environment Variables**:
```env
MS_CLIENT_ID=<your-azure-app-client-id>
MS_TENANT_ID=<your-tenant-id>
MS_CLIENT_SECRET=<your-azure-app-client-secret>
MS_REDIRECT_URI=https://aipg.dudelabz.com/auth/callback
ALLOWED_DOMAIN=terasky.com
```

## Integration Guidelines

### Data Freshness
- **Employee Data**: Updated via MS Graph + Salesforce APIs
- **Product Data**: Updated via Salesforce API
- **Client Data**: Updated via Salesforce API
- **Recording Data**: Updated via Teams Recording Scanner
- **Reference Data**: Manual CSV updates

### Primary Keys
- **Employee**: `azure_id` (stable across updates)
- **Product**: `name` (stable, SF ID may change)
- **Client**: `sf_id` (Salesforce Account ID)
- **Region/Skill/BU**: `name`

### Data Lineage
- **MS Graph fields**: `ms_` prefix
- **Salesforce fields**: `sf_` prefix
- **Core TSKB fields**: No prefix

### Error Handling
- Check `SyncMetadata` nodes for import status
- Failed imports logged in `error_details`
- Partial failures marked as `completed_with_errors`

---

**Document Version**: 2.2.0  
**Last Updated**: 2025-11-09  
**Next Review**: 2025-12-09
  "sf_active_contract": true,
  "sf_account_source": "Referral",
  "sf_domain_names": "wix.com",
  "sf_website": "https://www.wix.com",
  "sf_account_manager_cloud_id": "0051234567890GHI",
  "created_at": "2025-11-04T10:00:00Z",
  "updated_at": "2025-11-04T10:00:00Z"
}
```

**Email Cleaning Logic**:
- Salesforce Owner emails may have `.invalid` suffix
- Cleaned format: `username@terasky.com` (trim `.invalid`)

**Country-Region Mapping**:
- `Israel` → `IL`
- `United States`, `USA` → `US`
- `Germany`, `United Kingdom`, `UK` → `UK`

**Relationships**:
- `(Client)-[:LOCATED_IN]->(Region)` - via `region` (derived from `sf_billing_country`)
- `(Client)-[:MANAGED_BY]->(Employee)` - via `sf_owner_email`, `sf_owner_id`, or `sf_account_manager_cloud_id`
- `(Client)-[:PURCHASED]->(Product)` - via OpportunityLineItem
- `(Client)-[:HAS_INSTALLED]->(Product)` - via Asset

---

### 8. Compliance Node

**Label**: `Compliance`  
**Source**: Legacy/Manual  
**Count**: Variable

**Properties**:
```json
{
  "id": "string (UNIQUE)",
  "name": "string",
  "description": "string",
  "created_at": "datetime"
}
```

**Example**:
```json
{
  "id": "soc2",
  "name": "SOC 2",
  "description": "Service Organization Control 2",
  "created_at": "2025-11-04T10:00:00Z"
}
```

**Relationships**:
- `(Product)-[:SUPPORTS]->(Compliance)`

---

### 9. SyncMetadata Node

**Label**: `SyncMetadata`  
**Source**: System-generated  
**Count**: 3 nodes (one per importer type)

**Properties**:
```json
{
  "type": "string (UNIQUE)",
  "last_run": "datetime",
  "status": "string (success|completed_with_errors)",
  "processed": "integer",
  "created": "integer",
  "updated": "integer",
  "skipped": "integer",
  "errors": "integer"
}
```

**Example**:
```json
{
  "type": "client_import",
  "last_run": "2025-11-04T10:00:00Z",
  "status": "success",
  "processed": 115,
  "skipped": 0,
  "errors": 0
}
```

**Valid Types**:
- `employee_import` - MS Graph + Salesforce user sync
- `product_import` - Salesforce product sync
- `client_import` - Salesforce account/client sync
- `opportunity_product_import` - OpportunityLineItem → PURCHASED relationships
- `asset_import` - Asset → HAS_INSTALLED relationships

**Purpose**: Track last import execution status without updating individual nodes

---

## Relationship Schemas

### 1. LOCATED_IN

**Pattern**: `(Employee|Client)-[:LOCATED_IN]->(Region)`

**Employee → Region**:
- **Match Logic**: `e.sf_location = r.name OR e.sf_default_geo = r.name OR e.ms_office_location = r.name`
- **Priority**: SF Location > SF Default Geo > MS Office Location
- **Cardinality**: Many-to-One (multiple employees per region)

**Client → Region**:
- **Match Logic**: `c.region = r.name` (derived from `sf_billing_country`)
- **Cardinality**: Many-to-One (multiple clients per region)

**Cypher Query**:
```cypher
// Employee to Region
MATCH (e:Employee), (r:Region)
WHERE e.sf_location = r.name OR e.sf_default_geo = r.name
AND NOT EXISTS((e)-[:LOCATED_IN]->(r))
CREATE (e)-[:LOCATED_IN]->(r)

// Client to Region
MATCH (c:Client), (r:Region)
WHERE c.region = r.name
AND NOT EXISTS((c)-[:LOCATED_IN]->(r))
CREATE (c)-[:LOCATED_IN]->(r)
```

---

### 2. HAS_SKILL

**Pattern**: `(Employee)-[:HAS_SKILL]->(Skill)`

**Match Logic**: Legacy/Manual assignment
**Cardinality**: Many-to-Many (employees can have multiple skills)

**Cypher Query**:
```cypher
MATCH (e:Employee), (s:Skill)
WHERE s.name IN e.skills  // Legacy array property
AND NOT EXISTS((e)-[:HAS_SKILL]->(s))
CREATE (e)-[:HAS_SKILL]->(s)
```

---

### 3. BELONGS_TO

**Pattern**: `(Employee|Product)-[:BELONGS_TO]->(BU)`

**Employee → BU**:
- **Match Logic**: `e.sf_team = b.name OR e.sf_group = b.name OR e.ms_department = b.name`
- **Priority**: SF Team > SF Group > MS Department
- **Cardinality**: Many-to-One

**Product → BU**:
- **Match Logic**: `p.sf_business_unit = b.name`
- **Cardinality**: Many-to-One

**Cypher Query**:
```cypher
// Employee to BU (SF Team)
MATCH (e:Employee), (b:BU)
WHERE e.sf_team = b.name
AND NOT EXISTS((e)-[:BELONGS_TO]->(b))
CREATE (e)-[:BELONGS_TO]->(b)

// Product to BU
MATCH (p:Product), (b:BU)
WHERE p.sf_business_unit = b.name
AND NOT EXISTS((p)-[:BELONGS_TO]->(b))
CREATE (p)-[:BELONGS_TO]->(b)
```

---

### 4. MAKES

**Pattern**: `(Vendor)-[:MAKES]->(Product)`

**Match Logic**: `v.name = p.vendor OR v.name = p.sf_vendor`
**Cardinality**: One-to-Many (vendor makes multiple products)
**Auto-Creation**: Vendor nodes auto-created if not exist

**Cypher Query**:
```cypher
MATCH (v:Vendor), (p:Product)
WHERE v.name = p.vendor OR v.name = p.sf_vendor
AND NOT EXISTS((v)-[:MAKES]->(p))
CREATE (v)-[:MAKES]->(p)
```

---

### 5. MANAGED_BY

**Pattern**: `(Client)-[:MANAGED_BY]->(Employee)`

**Match Logic** (3 variants, priority order):
1. **Email Match**: `c.sf_owner_email = e.email`
2. **SF ID Match**: `c.sf_owner_id = e.sf_id`
3. **Cloud AM Match**: `c.sf_account_manager_cloud_id = e.sf_id`

**Cardinality**: Many-to-One (multiple clients per account manager)

**Cypher Query**:
```cypher
// Variant 1: Email match
MATCH (c:Client), (e:Employee)
WHERE c.sf_owner_email = e.email
AND NOT EXISTS((c)-[:MANAGED_BY]->(e))
CREATE (c)-[:MANAGED_BY]->(e)

// Variant 2: SF ID match
MATCH (c:Client), (e:Employee)
WHERE c.sf_owner_id = e.sf_id
AND NOT EXISTS((c)-[:MANAGED_BY]->(e))
CREATE (c)-[:MANAGED_BY]->(e)

// Variant 3: Cloud AM match
MATCH (c:Client), (e:Employee)
WHERE c.sf_account_manager_cloud_id = e.sf_id
AND NOT EXISTS((c)-[:MANAGED_BY]->(e))
CREATE (c)-[:MANAGED_BY]->(e)
```

---

### 6. SUPPORTS

**Pattern**: `(Product)-[:SUPPORTS]->(Compliance)`

**Match Logic**: Legacy/Manual assignment
**Cardinality**: Many-to-Many (products support multiple compliance standards)

**Cypher Query**:
```cypher
MATCH (p:Product), (c:Compliance)
WHERE c.id IN p.compliance  // Legacy array property
AND NOT EXISTS((p)-[:SUPPORTS]->(c))
CREATE (p)-[:SUPPORTS]->(c)
```

---

### 7. REQUIRES_SKILL

**Pattern**: `(Product)-[:REQUIRES_SKILL]->(Skill)`

**Match Logic**: `p.sf_delivery_team = s.name`
**Cardinality**: Many-to-Many (products require multiple skills)

**Cypher Query**:
```cypher
MATCH (p:Product), (s:Skill)
WHERE p.sf_delivery_team = s.name
AND NOT EXISTS((p)-[:REQUIRES_SKILL]->(s))
CREATE (p)-[:REQUIRES_SKILL]->(s)
```

---

### 8. OPPORTUNITY

**Pattern**: `(Client)-[:OPPORTUNITY]->(Product)`

**Source**: Salesforce OpportunityLineItem (10,030+ records)  
**Match Logic**: `OpportunityLineItem.Product2Id → Product`, `OpportunityLineItem.Opportunity.AccountId → Client`  
**Cardinality**: Many-to-Many (clients have multiple opportunities, products in multiple opportunities)

**Relationship Properties**:
```json
{
  "sf_opportunity_line_item_id": "string (UNIQUE)",
  "opportunity_name": "string",
  "opportunity_stage": "string (Closed Won|Closed Lost|Qualification|etc.)",
  "close_date": "string (ISO) - Actual deal close date (USE THIS for temporal queries)",
  "quantity": "number",
  "unit_price": "number",
  "total_price": "number (USE THIS for cost calculations, NOT 'amount')",
  "description": "string",
  "purchased_date": "string (ISO) - Line item creation date (rarely used)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**CRITICAL**: 
- No `amount` field exists. Always use `total_price` for cost/revenue calculations.
- Use `close_date` for temporal queries (actual deal close), NOT `purchased_date` (line item creation)

**Cost Aggregation Pattern**:
```cypher
// Calculate total revenue
MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
WHERE o.opportunity_stage = 'Closed Won'
RETURN sum(toFloat(o.total_price)) as total_revenue
```

**Temporal Query Pattern**:
```cypher
// Find deals closed in 2025
MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
WHERE o.opportunity_stage = 'Closed Won'
AND o.close_date >= '2025-01-01' AND o.close_date < '2026-01-01'
RETURN c.sf_name, p.name, o.close_date, o.total_price
ORDER BY o.close_date DESC
```

**Example**:
```json
{
  "sf_opportunity_line_item_id": "00k1234567890ABC",
  "opportunity_name": "Wix - Terraform Enterprise",
  "opportunity_stage": "Closed Won",
  "quantity": 10,
  "unit_price": 5000.00,
  "total_price": 50000.00,
  "description": "Annual subscription",
  "purchased_date": "2024-06-15T00:00:00Z",
  "created_at": "2025-11-10T10:00:00Z"
}
```

**Cypher Query**:
```cypher
MATCH (c:Client {sf_id: $account_id})
MATCH (p:Product {name: $product_name})
MERGE (c)-[r:OPPORTUNITY {sf_opportunity_line_item_id: $sf_id}]->(p)
ON CREATE SET r += $props, r.created_at = datetime()
ON MATCH SET r += $props, r.updated_at = datetime()
```

**Common Stage Values**:
- `"Closed Won"` - Successfully closed deals
- `"Closed Lost"` - Lost opportunities
- `"Qualification"` - Pipeline opportunities
- `"Quote Preparation"` - Preparing quotes
- `"Commercial Negotiation"` - In negotiation

**Stage-Filtered Queries**:
```cypher
-- Only successful deals
MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
WHERE o.opportunity_stage = 'Closed Won'
RETURN count(o) as won_deals

-- Pipeline value
MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
WHERE o.opportunity_stage = 'Qualification'
RETURN sum(o.total_price) as pipeline_value
```

**Incremental Sync**:
- First run: Full scan (10,030+ records)
- Subsequent runs: 3-day lookback (LastModifiedDate >= last_sync - 3 days)
- Performance: 99.89% reduction (10,030+ → ~11 records)

---

### 9. HAS_INSTALLED

**Pattern**: `(Client)-[:HAS_INSTALLED]->(Product)`

**Source**: Salesforce Asset (2,241 records)  
**Match Logic**: `Asset.Product2Id → Product`, `Asset.AccountId → Client`  
**Cardinality**: Many-to-Many (clients install multiple products, products installed at multiple clients)

**Relationship Properties**:
```json
{
  "sf_asset_id": "string (UNIQUE)",
  "asset_name": "string",
  "status": "string (Installed|Shipped|Registered)",
  "quantity": "number",
  "install_date": "string (ISO)",
  "purchase_date": "string (ISO)",
  "usage_end_date": "string (ISO)",
  "installed_date": "string (ISO)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Example**:
```json
{
  "sf_asset_id": "02i1234567890ABC",
  "asset_name": "Terraform Enterprise - Production",
  "status": "Installed",
  "quantity": 10,
  "install_date": "2024-07-01T00:00:00Z",
  "purchase_date": "2024-06-15T00:00:00Z",
  "usage_end_date": "2025-06-15T00:00:00Z",
  "installed_date": "2024-07-01T00:00:00Z",
  "created_at": "2025-11-09T10:00:00Z"
}
```

**Cypher Query**:
```cypher
MATCH (c:Client {sf_id: $account_id})
MATCH (p:Product {name: $product_name})
MERGE (c)-[r:HAS_INSTALLED {sf_asset_id: $sf_id}]->(p)
ON CREATE SET r += $props, r.created_at = datetime()
ON MATCH SET r += $props, r.updated_at = datetime()
```

**Incremental Sync**:
- First run: Full scan (2,241 records)
- Subsequent runs: 3-day lookback (LastModifiedDate >= last_sync - 3 days)
- Performance: 99.78% reduction (2,241 → ~5 records)

---

## Data Source Tags

All nodes include a `source` property to track data origin:

| Source Tag | Description | Node Types |
|------------|-------------|------------|
| `tskb-csv` | Human-editable CSV files | Region, Skill |
| `tskb-sf_api` | Salesforce API (Product2, Account) | BU, Product, Vendor, Client |
| `tskb-ms_api` | Microsoft Graph API | Employee |
| `opportunity_derived` | Auto-created from OpportunityLineItem | Client, Product |
| `asset_derived` | Auto-created from Asset | Client, Product |

**Query by Source**:
```cypher
// Get all Salesforce-sourced nodes
MATCH (n)
WHERE n.source = 'tskb-sf_api'
RETURN labels(n)[0] as type, count(n) as count
```

---

## Field Prefixes

To maintain data lineage and prevent field name conflicts:

| Prefix | Source | Example Fields |
|--------|--------|----------------|
| `ms_` | Microsoft Graph | `ms_id`, `ms_display_name`, `ms_account_enabled` |
| `sf_` | Salesforce | `sf_id`, `sf_name`, `sf_team`, `sf_owner_email` |
| (none) | Core TSKB | `name`, `email`, `title`, `source` |

---

## Common Query Patterns

### Get Employee with Full Context
```cypher
MATCH (e:Employee {email: 'john.doe@terasky.com'})
OPTIONAL MATCH (e)-[:LOCATED_IN]->(r:Region)
OPTIONAL MATCH (e)-[:BELONGS_TO]->(b:BU)
OPTIONAL MATCH (e)-[:HAS_SKILL]->(s:Skill)
OPTIONAL MATCH (c:Client)-[:MANAGED_BY]->(e)
RETURN e, r, b, collect(DISTINCT s.name) as skills, collect(DISTINCT c.name) as clients
```

### Get Client with Account Manager and Products
```cypher
MATCH (c:Client {name: 'Wix.com'})
OPTIONAL MATCH (c)-[:MANAGED_BY]->(e:Employee)
OPTIONAL MATCH (c)-[:LOCATED_IN]->(r:Region)
OPTIONAL MATCH (c)-[purchased:PURCHASED]->(p_purchased:Product)
OPTIONAL MATCH (c)-[installed:HAS_INSTALLED]->(p_installed:Product)
RETURN c, e, r, 
       collect(DISTINCT {product: p_purchased.name, purchased_date: purchased.purchased_date}) as purchased_products,
       collect(DISTINCT {product: p_installed.name, status: installed.status}) as installed_products
```

### Get Product with Vendor and BU
```cypher
MATCH (p:Product {name: 'Terraform Enterprise'})
OPTIONAL MATCH (v:Vendor)-[:MAKES]->(p)
OPTIONAL MATCH (p)-[:BELONGS_TO]->(b:BU)
OPTIONAL MATCH (p)-[:REQUIRES_SKILL]->(s:Skill)
RETURN p, v, b, collect(s.name) as required_skills
```

### Get All Nodes by Type
```cypher
MATCH (n)
RETURN labels(n)[0] as type, count(n) as count
ORDER BY type
```

### Get Sync Status
```cypher
MATCH (s:SyncMetadata)
RETURN s.type, s.last_run, s.status, s.processed, s.errors
ORDER BY s.last_run DESC
```

---

## Integration Checklist

When integrating with TSKB-RAG data:

- [ ] **Use `source` tags** to filter data by origin
- [ ] **Check field prefixes** (`ms_`, `sf_`) for data lineage
- [ ] **Handle NULL values** - not all fields are populated for all nodes
- [ ] **Use relationship queries** instead of property arrays where possible
- [ ] **Check SyncMetadata** to verify data freshness
- [ ] **Match on unique identifiers**: `azure_id` (Employee), `sf_id` (Client/Product), `name` (Region/Skill/BU/Vendor)
- [ ] **Handle email cleaning** - Client `sf_owner_email` is cleaned to `@terasky.com`
- [ ] **Map regions correctly** - Use country-region mapping for Client data

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.6.0 | 2025-11-18 | Added OAuth authentication requirements and security documentation |
| 2.5.0 | 2025-11-17 | Added learned query patterns documentation and production analytics |
| 2.4.0 | 2025-11-12 | Added close_date field to OPPORTUNITY for accurate temporal queries |
| 2.3.0 | 2025-11-10 | Updated cost field documentation (total_price) |
| 2.2.0 | 2025-11-09 | Added PURCHASED/HAS_INSTALLED relationships, incremental sync, product version tracking |
| 2.1.0 | 2025-11-04 | Added Client node schema, MANAGED_BY relationships, SyncMetadata system |
| 2.0.1 | 2025-01-15 | Added source tag standardization, notification system |
| 2.0.0 | 2025-01-05 | Initial production release with API integration |

---

## Support

For schema questions or integration support:
- **Documentation**: See `README.md`, `CHANGELOG.md`, `ADR.md`
- **Source Code**: `importers/` directory
- **Test Queries**: `Tests/` directory

---

**End of Schema Synchronization Guide**
