# TSKB-RAG Chatbot System Design

**Version**: 1.1.0  
**Date**: 2025-11-10  
**Purpose**: Comprehensive design document for building a conversational AI chatbot with access to TSKB Neo4j knowledge graph

---

## Executive Summary

This document outlines the architecture, implementation strategy, and technical specifications for building **tskgRAG** - a Retrieval-Augmented Generation (RAG) chatbot system that provides natural language access to TeraSky's Technical Solution Knowledge Base (TSKB).

### Prerequisites
- **Existing TSKB-RAG Pipeline**: Fully operational Neo4j knowledge graph with 3,093+ nodes
- **Data Sources**: Live Salesforce API + Microsoft Graph integration
- **Infrastructure**: Neo4j 5.15+, Python 3.11+, Docker support
- **AWS Bedrock**: Access to AWS Bedrock AI and LLM services
- **Network**: TS_AI_network Docker network for service communication

### Project Scope
- **Input**: Any natural language query (unlimited question types)
- **Output**: Structured answers with confidence levels and data citations
- **Core Technology**: FastAPI + Neo4j + AWS Bedrock LLM
- **Deployment**: Docker container with SSL support and logging
- **Intelligence**: Self-learning system with schema discovery and query optimization

### Key Capabilities
- **Universal Query Support**: Handle any question type through dynamic schema understanding
- **Confidence Scoring**: Every response includes confidence level (0-100%)
- **Self-Learning**: Continuously improves query generation and response accuracy
- **Schema Discovery**: Automatically understands available data and relationships
- **AWS Bedrock Integration**: Leverages AWS AI services for advanced language understanding
- **Real-time Data Access**: Direct Neo4j integration with live Salesforce/MS Graph data

---

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Query    │───▶│   tskgRAG API   │───▶│   Neo4j Graph   │
│  Natural Lang   │    │   (FastAPI)     │    │   Knowledge     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                         │
                              ▼                         │
                       ┌─────────────────┐              │
                       │  AWS Bedrock    │              │
                       │   LLM Service   │              │
                       └─────────────────┘              │
                              │                         │
                              ▼                         │
                       ┌─────────────────┐              │
                       │ Query Generator │◀─────────────┘
                       │ (Cypher/Vector) │
                       └─────────────────┘
```

### Core Components

1. **Query Understanding Layer**
   - Intent classification
   - Entity extraction
   - Query type detection

2. **Knowledge Retrieval Layer**
   - Cypher query generation
   - Vector similarity search
   - Hybrid retrieval strategies

3. **Response Generation Layer**
   - Context assembly
   - LLM-powered response generation
   - Answer validation

4. **Data Integration Layer**
   - Real-time Neo4j access
   - Schema-aware querying
   - Relationship traversal

---

## Knowledge Graph Schema

### Node Types (9 Total)

| Node Type | Count | Primary Key | Source | Description |
|-----------|-------|-------------|---------|-------------|
| **Employee** | 289 | `azure_id` | MS Graph + SF | Staff with skills, regions, BUs |
| **Client** | 1,288 | `sf_id` | Salesforce | Accounts with managers, regions |
| **Product** | 511 | `name` | Salesforce | Products with vendors, BUs |
| **Vendor** | 69 | `name` | Auto-created | Product manufacturers |
| **Region** | 3 | `name` | SF API | Geographic locations (IL, US, UK) |
| **Skill** | 19 | `name` | CSV | Technical capabilities |
| **BU** | 19 | `name` | Salesforce | Business units/teams |
| **Compliance** | Variable | `name` | Legacy | Standards (SOC2, GDPR) |
| **SyncMetadata** | 5 | `type` | System | Import tracking |

### Relationship Types (9 Total)

| Relationship | Pattern | Count | Description |
|--------------|---------|-------|-------------|
| **LOCATED_IN** | `(Employee\|Client)-[:LOCATED_IN]->(Region)` | 1,577+ | Geographic assignment |
| **BELONGS_TO** | `(Employee\|Product)-[:BELONGS_TO]->(BU)` | 681+ | Organizational structure |
| **MANAGED_BY** | `(Client)-[:MANAGED_BY]->(Employee)` | 1,288+ | Account management |
| **MAKES** | `(Vendor)-[:MAKES]->(Product)` | 511+ | Product ownership |
| **OPPORTUNITY** | `(Client)-[:OPPORTUNITY]->(Product)` | 10,030+ | Business opportunities (all stages) |
| **HAS_INSTALLED** | `(Client)-[:HAS_INSTALLED]->(Product)` | 2,241+ | Product deployments |
| **REQUIRES_SKILL** | `(Product)-[:REQUIRES_SKILL]->(Skill)` | 42+ | Delivery requirements |
| **HAS_SKILL** | `(Employee)-[:HAS_SKILL]->(Skill)` | Variable | Employee capabilities |
| **SUPPORTS** | `(Product)-[:SUPPORTS]->(Compliance)` | Variable | Compliance standards |

### Key Schema Features

#### Rich Salesforce Integration
- **Employee**: MS Graph identity + Salesforce business data
- **Client**: 21-field schema with custom SF fields
- **Product**: 19 SF fields including strategic vendor flags
- **Relationships**: Auto-created from OpportunityLineItem + Asset data

#### Temporal Data
- **OPPORTUNITY relationships**: Include `purchased_date`, `total_price`, `quantity`, `opportunity_stage` (Closed Won, Closed Lost, Pipeline)
- **HAS_INSTALLED relationships**: Include `install_date`, `status`, `usage_end_date`
- **All nodes**: `created_at`, `updated_at` timestamps

#### Business Intelligence Features
- **Deal Stage Filtering**: OPPORTUNITY relationships include `opportunity_stage` for accurate revenue analysis
- **Won vs Lost Deals**: Filter by `opportunity_stage = 'Closed Won'` for actual revenue
- **Pipeline Analysis**: Include all stages for comprehensive deal analysis
- **Progress Tracking**: Import pipeline shows real-time processing status every 50 items

#### Data Lineage
- **Field prefixes**: `ms_` (Microsoft), `sf_` (Salesforce)
- **Source tags**: Track data origin (`tskb-sf_api`, `tskb-ms_api`, etc.)
- **Sync metadata**: Track import status and freshness

---

## Query Understanding & Intent Classification

### Query Categories

#### 1. **Quantitative Queries**
- **Pattern**: "How many X..."
- **Examples**: 
  - "How many clients purchased HashiCorp products in 2025?"
  - "How many employees are in the DevOps team?"
- **Strategy**: COUNT aggregation with filters

#### 2. **List/Discovery Queries**
- **Pattern**: "List all X where Y..."
- **Examples**:
  - "List all deals closed for Wix in the past 3 years"
  - "Show me all employees managing clients in Israel"
- **Strategy**: MATCH with COLLECT, ordered results

#### 3. **Relationship Queries**
- **Pattern**: "Which X are connected to Y..."
- **Examples**:
  - "Which employees manage clients using Terraform?"
  - "What products does Wix have installed?"
- **Strategy**: Multi-hop relationship traversal

#### 4. **Analytical Queries**
- **Pattern**: "What is the trend/pattern..."
- **Examples**:
  - "What's our top-selling product by region?"
  - "Which vendors have the most strategic products?"
  - "What's our win rate by product?"
- **Strategy**: Aggregation with grouping and ranking

#### 5. **Temporal Queries**
- **Pattern**: Time-based filters
- **Examples**:
  - "Products purchased in 2025"
  - "Deals closed in the past 3 years"
- **Strategy**: Date range filtering on relationship properties

### Entity Extraction

#### Named Entities
- **Clients**: "Wix", "Microsoft", "Google" → Match `Client.name`
- **Products**: "Terraform", "Vault", "Kubernetes" → Match `Product.name`
- **Vendors**: "HashiCorp", "AWS", "Microsoft" → Match `Vendor.name`
- **Employees**: "John Doe", "jane.smith@terasky.com" → Match `Employee.name` or `Employee.email`
- **Regions**: "Israel", "US", "UK" → Match `Region.name`
- **Skills**: "DevOps", "Cloud", "Security" → Match `Skill.name`

#### Temporal Entities
- **Years**: "2025", "2024" → Date range filters
- **Relative Time**: "past 3 years", "last month" → Dynamic date calculations
- **Specific Dates**: "January 2024" → Precise date ranges

#### Quantitative Entities
- **Numbers**: "top 5", "more than 10" → LIMIT and WHERE clauses
- **Comparatives**: "most", "least", "highest" → ORDER BY DESC/ASC

---

## Retrieval Strategies

### 1. **Direct Cypher Generation**

**Best For**: Structured queries with clear entity relationships

**Process**:
1. Parse query for entities and relationships
2. Generate Cypher query template
3. Execute against Neo4j
4. Return structured results

**Example**:
```
Query: "How many clients purchased HashiCorp products in 2025?"

Generated Cypher:
MATCH (c:Client)-[o:OPPORTUNITY]->(prod:Product)<-[:MAKES]-(v:Vendor {name: 'HashiCorp'})
WHERE o.opportunity_stage = 'Closed Won' 
  AND o.purchased_date >= '2025-01-01' AND o.purchased_date < '2026-01-01'
RETURN count(DISTINCT c) as client_count
```

### 2. **Semantic Vector Search**

**Best For**: Fuzzy matching, concept-based queries

**Implementation**:
- **Node Embeddings**: Generate embeddings for node descriptions
- **Query Embeddings**: Embed user query
- **Similarity Search**: Find most relevant nodes
- **Relationship Expansion**: Traverse from relevant nodes

**Example**:
```
Query: "Infrastructure automation tools"
→ Vector search finds: Terraform, Ansible, Puppet
→ Expand to related clients, employees, deals
```

### 3. **Hybrid Retrieval**

**Best For**: Complex queries requiring both precision and recall

**Process**:
1. **Keyword Extraction**: Identify exact entity matches
2. **Vector Expansion**: Find semantically similar entities
3. **Relationship Traversal**: Follow graph connections
4. **Result Fusion**: Combine and rank results

### 4. **Template-Based Queries**

**Best For**: Common business intelligence patterns

**Pre-defined Templates**:
```cypher
// Client Product Usage
MATCH (c:Client {name: $client_name})-[rel:PURCHASED|HAS_INSTALLED]->(p:Product)
RETURN p.name, type(rel), rel.purchased_date, rel.total_price

// Employee Client Portfolio
MATCH (e:Employee {email: $email})<-[:MANAGED_BY]-(c:Client)
RETURN c.name, c.sf_industry, c.sf_company_size

// Product Revenue by Vendor
MATCH (v:Vendor)-[:MAKES]->(p:Product)<-[pur:PURCHASED]-(c:Client)
RETURN v.name, sum(pur.total_price) as total_revenue
ORDER BY total_revenue DESC
```

---

## Response Generation

### Context Assembly

#### 1. **Query Results Processing**
```python
def process_query_results(cypher_results, query_context):
    """Convert Cypher results to structured context"""
    context = {
        "query_type": query_context.intent,
        "entities_found": extract_entities(cypher_results),
        "relationships": extract_relationships(cypher_results),
        "aggregations": extract_aggregations(cypher_results),
        "temporal_data": extract_temporal_data(cypher_results)
    }
    return context
```

#### 2. **Context Enrichment**
- **Related Entities**: Add connected nodes for context
- **Metadata**: Include data freshness, source information
- **Business Context**: Add industry knowledge, definitions

#### 3. **Response Templates**

**Quantitative Response**:
```
Based on the TSKB knowledge graph:

**Answer**: {count} clients purchased HashiCorp products in 2025.

**Details**:
- Products: {product_list}
- Total Revenue: ${total_revenue:,.2f}
- Top Client: {top_client} (${top_amount:,.2f})

**Data Source**: Salesforce OpportunityLineItem records
**Last Updated**: {sync_timestamp}
```

**List Response**:
```
Here are all deals closed for {client_name} in the past 3 years:

{deal_list}

**Summary**:
- Total Deals: {deal_count}
- Total Value: ${total_value:,.2f}
- Account Manager: {account_manager}
- Primary Products: {top_products}
```

### LLM Integration

#### System Prompt Template
```
You are tskgRAG, an AI assistant with access to TeraSky's Technical Solution Knowledge Base.

KNOWLEDGE GRAPH SCHEMA:
- Employees (289): Staff with skills, regions, business units
- Clients (1,288): Accounts with managers, products, regions  
- Products (511): Solutions with vendors, business units
- Relationships: PURCHASED, HAS_INSTALLED, MANAGED_BY, etc.

RESPONSE GUIDELINES:
1. Always cite data sources (Salesforce, MS Graph)
2. Include data freshness information
3. Provide specific numbers and details
4. Suggest follow-up questions
5. Acknowledge limitations or missing data

CURRENT CONTEXT:
{context}

USER QUERY: {query}
```

#### Response Validation
```python
def validate_response(response, query_results):
    """Validate LLM response against actual data"""
    checks = [
        verify_numbers_match(response, query_results),
        verify_entities_exist(response, query_results),
        verify_relationships_correct(response, query_results),
        verify_temporal_accuracy(response, query_results)
    ]
    return all(checks)
```

---

## Technical Implementation

### API Architecture (FastAPI)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from neo4j import GraphDatabase
import openai

app = FastAPI(title="tskgRAG API", version="1.0.0")

class QueryRequest(BaseModel):
    query: str
    context: Optional[dict] = None
    max_results: int = 100

class QueryResponse(BaseModel):
    answer: str
    cypher_query: str
    results_count: int
    data_sources: List[str]
    confidence: float
    suggestions: List[str]

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process natural language query against TSKB knowledge graph"""
    
    # 1. Query Understanding
    intent = classify_intent(request.query)
    entities = extract_entities(request.query)
    
    # 2. Query Generation
    cypher_query = generate_cypher(intent, entities)
    
    # 3. Knowledge Retrieval
    results = execute_cypher(cypher_query)
    
    # 4. Response Generation
    context = assemble_context(results, intent, entities)
    answer = generate_response(context, request.query)
    
    # 5. Validation
    if not validate_response(answer, results):
        raise HTTPException(status_code=500, detail="Response validation failed")
    
    return QueryResponse(
        answer=answer,
        cypher_query=cypher_query,
        results_count=len(results),
        data_sources=extract_sources(results),
        confidence=calculate_confidence(intent, entities, results),
        suggestions=generate_suggestions(intent, entities)
    )
```

### Neo4j Integration

```python
class TSKBGraphDB:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def execute_query(self, cypher, parameters=None):
        """Execute Cypher query with error handling"""
        with self.driver.session() as session:
            try:
                result = session.run(cypher, parameters or {})
                return [record.data() for record in result]
            except Exception as e:
                logger.error(f"Cypher execution failed: {e}")
                raise
    
    def get_schema_info(self):
        """Get current schema information"""
        schema_query = """
        CALL db.schema.visualization()
        YIELD nodes, relationships
        RETURN nodes, relationships
        """
        return self.execute_query(schema_query)
    
    def validate_entities(self, entities):
        """Validate that entities exist in the graph"""
        validation_queries = {
            'Client': "MATCH (c:Client) WHERE c.name CONTAINS $name RETURN c.name LIMIT 5",
            'Product': "MATCH (p:Product) WHERE p.name CONTAINS $name RETURN p.name LIMIT 5",
            'Employee': "MATCH (e:Employee) WHERE e.name CONTAINS $name OR e.email CONTAINS $name RETURN e.name, e.email LIMIT 5"
        }
        
        validated = {}
        for entity_type, query in validation_queries.items():
            for entity in entities.get(entity_type, []):
                results = self.execute_query(query, {"name": entity})
                validated[entity] = results
        
        return validated
```

### Query Generation Engine

```python
class CypherGenerator:
    def __init__(self, schema):
        self.schema = schema
        self.templates = self._load_templates()
    
    def generate(self, intent, entities, temporal_filters=None):
        """Generate Cypher query from intent and entities"""
        
        if intent == "count_clients_by_product_vendor":
            return self._generate_count_query(entities, temporal_filters)
        elif intent == "list_deals_by_client":
            return self._generate_deals_query(entities, temporal_filters)
        elif intent == "find_relationships":
            return self._generate_relationship_query(entities)
        else:
            return self._generate_generic_query(intent, entities, temporal_filters)
    
    def _generate_count_query(self, entities, temporal_filters):
        """Generate COUNT aggregation query"""
        vendor = entities.get('vendor', [None])[0]
        year = temporal_filters.get('year') if temporal_filters else None
        
        cypher = """
        MATCH (c:Client)-[p:PURCHASED]->(prod:Product)<-[:MAKES]-(v:Vendor {name: $vendor})
        """
        
        if year:
            cypher += "WHERE p.purchased_date >= $start_date AND p.purchased_date < $end_date "
        
        cypher += "RETURN count(DISTINCT c) as client_count"
        
        parameters = {"vendor": vendor}
        if year:
            parameters.update({
                "start_date": f"{year}-01-01",
                "end_date": f"{year + 1}-01-01"
            })
        
        return cypher, parameters
```

### Intent Classification

```python
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

class IntentClassifier:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.vectorizer = TfidfVectorizer()
        self.classifier = MultinomialNB()
        self.intents = [
            "count_clients_by_product",
            "count_clients_by_vendor", 
            "list_deals_by_client",
            "list_products_by_client",
            "find_account_manager",
            "find_client_relationships",
            "analyze_revenue_by_vendor",
            "analyze_products_by_region"
        ]
        self._train_classifier()
    
    def classify(self, query):
        """Classify user query intent"""
        features = self.vectorizer.transform([query])
        intent = self.classifier.predict(features)[0]
        confidence = max(self.classifier.predict_proba(features)[0])
        
        return {
            "intent": intent,
            "confidence": confidence,
            "entities": self._extract_entities(query)
        }
    
    def _extract_entities(self, query):
        """Extract named entities from query"""
        doc = self.nlp(query)
        entities = {
            "clients": [],
            "products": [],
            "vendors": [],
            "employees": [],
            "years": [],
            "numbers": []
        }
        
        for ent in doc.ents:
            if ent.label_ == "ORG":
                # Could be client, vendor, or product
                entities["clients"].append(ent.text)
                entities["vendors"].append(ent.text)
            elif ent.label_ == "PERSON":
                entities["employees"].append(ent.text)
            elif ent.label_ == "DATE":
                # Extract year from date
                year_match = re.search(r'\b(20\d{2})\b', ent.text)
                if year_match:
                    entities["years"].append(int(year_match.group(1)))
            elif ent.label_ == "CARDINAL":
                entities["numbers"].append(int(ent.text))
        
        return entities
```

---

## Example Query Implementations

### Query 1: "How many clients purchased HashiCorp products in 2025?"

**Intent Classification**: `count_clients_by_vendor`
**Entities**: `vendor: "HashiCorp"`, `year: 2025`

**Generated Cypher**:
```cypher
MATCH (c:Client)-[o:OPPORTUNITY]->(prod:Product)<-[:MAKES]-(v:Vendor {name: 'HashiCorp'})
WHERE o.opportunity_stage = 'Closed Won'
  AND o.purchased_date >= '2025-01-01' AND o.purchased_date < '2026-01-01'
RETURN count(DISTINCT c) as client_count,
       collect(DISTINCT c.name) as client_names,
       collect(DISTINCT prod.name) as products,
       sum(o.total_price) as total_revenue
```

**Response Template**:
```
Based on the TSKB knowledge graph, **{client_count} clients** purchased HashiCorp products in 2025.

**Details**:
- **Products**: {products}
- **Total Revenue**: ${total_revenue:,.2f}
- **Clients**: {client_names}

**Data Source**: Salesforce OpportunityLineItem records
**Last Updated**: {last_sync_date}

**Follow-up Questions**:
- Which HashiCorp product was most popular?
- How does this compare to 2024?
- Which account managers closed these deals?
```

### Query 2: "List all deals closed for Wix in the past 3 years"

**Intent Classification**: `list_deals_by_client`
**Entities**: `client: "Wix"`, `time_range: "past 3 years"`

**Generated Cypher**:
```cypher
MATCH (c:Client {name: 'Wix.com'})-[o:OPPORTUNITY]->(prod:Product)<-[:MAKES]-(v:Vendor)
WHERE o.opportunity_stage = 'Closed Won'
  AND o.purchased_date >= date() - duration({years: 3})
OPTIONAL MATCH (c)-[:MANAGED_BY]->(am:Employee)
RETURN o.sf_opportunity_line_item_id as deal_id,
       o.opportunity_name as deal_title,
       o.opportunity_stage as stage,
       prod.name as product,
       v.name as vendor,
       o.total_price as deal_value,
       o.purchased_date as close_date,
       am.name as account_manager
ORDER BY o.purchased_date DESC
```

**Response Template**:
```
Here are all deals closed for **Wix** in the past 3 years:

{deal_list_formatted}

**Summary**:
- **Total Deals**: {deal_count}
- **Total Value**: ${total_value:,.2f}
- **Account Manager**: {account_manager}
- **Top Vendors**: {top_vendors}
- **Date Range**: {start_date} to {end_date}

**Data Source**: Salesforce OpportunityLineItem records
**Last Updated**: {last_sync_date}
```

### Query 3: "Which employees manage clients using Terraform?"

**Intent Classification**: `find_client_relationships`
**Entities**: `product: "Terraform"`

**Generated Cypher**:
```cypher
MATCH (e:Employee)<-[:MANAGED_BY]-(c:Client)-[rel:OPPORTUNITY|HAS_INSTALLED]->(p:Product)
WHERE p.name CONTAINS 'Terraform'
  AND (type(rel) = 'HAS_INSTALLED' OR rel.opportunity_stage = 'Closed Won')
OPTIONAL MATCH (e)-[:LOCATED_IN]->(r:Region)
OPTIONAL MATCH (e)-[:BELONGS_TO]->(bu:BU)
RETURN DISTINCT e.name as employee,
       e.email as email,
       e.title as title,
       r.name as region,
       bu.name as business_unit,
       collect(DISTINCT c.name) as clients,
       collect(DISTINCT p.name) as terraform_products,
       count(DISTINCT c) as client_count
ORDER BY client_count DESC
```

**Response Template**:
```
Here are the employees who manage clients using Terraform:

{employee_list_formatted}

**Summary**:
- **Total Account Managers**: {manager_count}
- **Total Clients with Terraform**: {client_count}
- **Terraform Products**: {terraform_products}
- **Regions Covered**: {regions}

**Top Account Manager**: {top_manager} manages {top_client_count} clients with Terraform

**Data Sources**: 
- Employee data: Microsoft Graph + Salesforce
- Client relationships: Salesforce Accounts
- Product usage: Salesforce OpportunityLineItem + Assets
```

---

## Performance Optimization

### Database Optimization

#### Indexes
```cypher
// Essential indexes for query performance
CREATE INDEX client_name IF NOT EXISTS FOR (c:Client) ON (c.name);
CREATE INDEX product_name IF NOT EXISTS FOR (p:Product) ON (p.name);
CREATE INDEX vendor_name IF NOT EXISTS FOR (v:Vendor) ON (v.name);
CREATE INDEX employee_email IF NOT EXISTS FOR (e:Employee) ON (e.email);
CREATE INDEX purchased_date IF NOT EXISTS FOR ()-[p:PURCHASED]-() ON (p.purchased_date);
CREATE INDEX installed_date IF NOT EXISTS FOR ()-[i:HAS_INSTALLED]-() ON (i.install_date);
```

#### Query Optimization
- **Use LIMIT**: Always limit results for list queries
- **Index Hints**: Use index hints for complex queries
- **Relationship Direction**: Specify relationship direction when possible
- **OPTIONAL MATCH**: Use carefully to avoid cartesian products

### Caching Strategy

#### Query Result Caching
```python
import redis
import json
from datetime import timedelta

class QueryCache:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.default_ttl = timedelta(hours=1)
    
    def get_cached_result(self, query_hash):
        """Get cached query result"""
        cached = self.redis.get(f"query:{query_hash}")
        if cached:
            return json.loads(cached)
        return None
    
    def cache_result(self, query_hash, result, ttl=None):
        """Cache query result"""
        ttl = ttl or self.default_ttl
        self.redis.setex(
            f"query:{query_hash}",
            ttl,
            json.dumps(result, default=str)
        )
```

#### Schema Caching
- Cache node counts and relationship counts
- Cache common entity lists (client names, product names)
- Cache schema metadata for query generation

### Response Time Targets

| Query Type | Target Response Time | Optimization Strategy |
|------------|---------------------|----------------------|
| Simple Count | < 500ms | Indexed aggregation |
| Entity List | < 1s | Pagination + caching |
| Complex Analysis | < 3s | Pre-computed views |
| Full-text Search | < 2s | Vector index + hybrid search |

---

## Security & Access Control

### Authentication
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

@app.post("/query")
async def process_query(request: QueryRequest, user=Depends(verify_token)):
    # Process query with user context
    pass
```

### Data Access Control

#### Role-Based Access
```python
class AccessControl:
    def __init__(self):
        self.role_permissions = {
            "admin": ["all"],
            "manager": ["clients", "products", "employees", "revenue"],
            "employee": ["clients", "products"],
            "readonly": ["public_data"]
        }
    
    def check_permission(self, user_role, query_intent):
        """Check if user role has permission for query intent"""
        permissions = self.role_permissions.get(user_role, [])
        
        if "all" in permissions:
            return True
        
        intent_permissions = {
            "count_clients_by_vendor": "clients",
            "list_deals_by_client": "revenue",
            "find_account_manager": "employees"
        }
        
        required_permission = intent_permissions.get(query_intent, "public_data")
        return required_permission in permissions
```

#### Data Filtering
```python
def apply_data_filters(cypher_query, user_context):
    """Apply user-specific data filters to Cypher query"""
    
    if user_context.get("role") == "regional_manager":
        region = user_context.get("region")
        # Add region filter to query
        cypher_query += f" AND EXISTS((c)-[:LOCATED_IN]->(:Region {{name: '{region}'}}))"
    
    if user_context.get("role") == "account_manager":
        employee_id = user_context.get("employee_id")
        # Limit to managed clients only
        cypher_query += f" AND EXISTS((c)-[:MANAGED_BY]->(:Employee {{azure_id: '{employee_id}'}}))"
    
    return cypher_query
```

---

## Monitoring & Analytics

### Query Analytics
```python
class QueryAnalytics:
    def __init__(self, db_client):
        self.db = db_client
    
    def log_query(self, user_id, query, intent, response_time, success):
        """Log query for analytics"""
        log_entry = {
            "timestamp": datetime.utcnow(),
            "user_id": user_id,
            "query": query,
            "intent": intent,
            "response_time_ms": response_time,
            "success": success
        }
        self.db.queries.insert_one(log_entry)
    
    def get_popular_queries(self, days=7):
        """Get most popular query patterns"""
        pipeline = [
            {"$match": {"timestamp": {"$gte": datetime.utcnow() - timedelta(days=days)}}},
            {"$group": {"_id": "$intent", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        return list(self.db.queries.aggregate(pipeline))
```

### Performance Monitoring
- **Response Time Tracking**: Monitor query execution times
- **Error Rate Monitoring**: Track failed queries and reasons
- **Usage Analytics**: Popular queries, user patterns
- **Data Freshness**: Monitor sync status and data age

### Health Checks
```python
@app.get("/health")
async def health_check():
    """System health check"""
    checks = {
        "neo4j": check_neo4j_connection(),
        "llm_service": check_llm_service(),
        "cache": check_redis_connection(),
        "data_freshness": check_data_freshness()
    }
    
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return {"status": "healthy" if all_healthy else "unhealthy", "checks": checks}
```

---

## Deployment Architecture

### Container Architecture
```dockerfile
# Dockerfile for tskgRAG API
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  tskgrag-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - neo4j
      - redis
    networks:
      - tskgrag-network

  neo4j:
    image: neo4j:5.15
    environment:
      - NEO4J_AUTH=neo4j/${NEO4J_PASSWORD}
      - NEO4J_PLUGINS=["apoc"]
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data
    networks:
      - tskgrag-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - tskgrag-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - tskgrag-api
    networks:
      - tskgrag-network

networks:
  tskgrag-network:
    driver: bridge

volumes:
  neo4j_data:
  redis_data:
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tskgrag-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tskgrag-api
  template:
    metadata:
      labels:
        app: tskgrag-api
    spec:
      containers:
      - name: tskgrag-api
        image: tskgrag:latest
        ports:
        - containerPort: 8000
        env:
        - name: NEO4J_URI
          value: "bolt://neo4j-service:7687"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: tskgrag-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

---

## Testing Strategy

### Unit Tests
```python
import pytest
from unittest.mock import Mock, patch
from tskgrag.query_generator import CypherGenerator
from tskgrag.intent_classifier import IntentClassifier

class TestCypherGenerator:
    def setup_method(self):
        self.generator = CypherGenerator(mock_schema)
    
    def test_count_query_generation(self):
        """Test COUNT query generation"""
        intent = "count_clients_by_vendor"
        entities = {"vendor": ["HashiCorp"]}
        temporal_filters = {"year": 2025}
        
        cypher, params = self.generator.generate(intent, entities, temporal_filters)
        
        assert "count(DISTINCT c)" in cypher
        assert "Vendor {name: $vendor}" in cypher
        assert "purchased_date >=" in cypher
        assert params["vendor"] == "HashiCorp"
        assert params["start_date"] == "2025-01-01"

class TestIntentClassifier:
    def setup_method(self):
        self.classifier = IntentClassifier()
    
    def test_count_intent_classification(self):
        """Test count query intent classification"""
        query = "How many clients purchased HashiCorp products in 2025?"
        result = self.classifier.classify(query)
        
        assert result["intent"] == "count_clients_by_vendor"
        assert result["confidence"] > 0.8
        assert "HashiCorp" in result["entities"]["vendors"]
        assert 2025 in result["entities"]["years"]
```

### Integration Tests
```python
class TestTSKBIntegration:
    def setup_method(self):
        self.db = TSKBGraphDB(test_neo4j_uri, test_user, test_password)
        self.api_client = TestClient(app)
    
    def test_end_to_end_query(self):
        """Test complete query flow"""
        query = "How many clients purchased HashiCorp products?"
        
        response = self.api_client.post("/query", json={"query": query})
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "cypher_query" in data
        assert data["results_count"] >= 0
        assert "Salesforce" in data["data_sources"]
    
    def test_entity_validation(self):
        """Test entity validation against graph"""
        entities = {"vendors": ["HashiCorp"], "clients": ["Wix"]}
        
        validated = self.db.validate_entities(entities)
        
        assert "HashiCorp" in validated
        assert len(validated["HashiCorp"]) > 0
```

### Performance Tests
```python
import time
import concurrent.futures

class TestPerformance:
    def test_query_response_time(self):
        """Test query response time requirements"""
        queries = [
            "How many clients purchased HashiCorp products?",
            "List all products for Wix",
            "Which employees manage the most clients?"
        ]
        
        for query in queries:
            start_time = time.time()
            response = self.api_client.post("/query", json={"query": query})
            response_time = time.time() - start_time
            
            assert response.status_code == 200
            assert response_time < 3.0  # 3 second max
    
    def test_concurrent_queries(self):
        """Test concurrent query handling"""
        def execute_query(query):
            return self.api_client.post("/query", json={"query": query})
        
        queries = ["How many clients are there?"] * 10
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(execute_query, q) for q in queries]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        assert all(r.status_code == 200 for r in results)
```

---

## Future Enhancements

### Phase 2: Advanced Analytics
- **Trend Analysis**: Time-series analysis of sales, usage patterns
- **Predictive Analytics**: Client churn prediction, upsell opportunities
- **Recommendation Engine**: Product recommendations based on client profile
- **Competitive Analysis**: Market share analysis, competitive positioning

### Phase 3: Multi-Modal Capabilities
- **Document Integration**: PDF reports, presentations, technical documentation
- **Image Analysis**: Architecture diagrams, network topology
- **Voice Interface**: Speech-to-text query input
- **Visual Responses**: Charts, graphs, network visualizations

### Phase 4: Advanced NLP
- **Multi-turn Conversations**: Context-aware follow-up questions
- **Query Refinement**: Interactive query building
- **Explanation Generation**: "Why" and "How" questions
- **Hypothesis Testing**: "What if" scenario analysis

### Phase 5: Real-time Intelligence
- **Streaming Data**: Real-time Salesforce updates
- **Alert System**: Automated insights and notifications
- **Dashboard Integration**: Embedded analytics in existing tools
- **Mobile App**: Native mobile interface

---

## Success Metrics

### Technical Metrics
- **Query Success Rate**: > 95%
- **Average Response Time**: < 2 seconds
- **System Uptime**: > 99.9%
- **Data Freshness**: < 1 hour lag

### Business Metrics
- **User Adoption**: Monthly active users
- **Query Volume**: Queries per day/week/month
- **User Satisfaction**: Feedback scores, NPS
- **Business Impact**: Time saved, insights generated

### Quality Metrics
- **Answer Accuracy**: Human evaluation of responses
- **Entity Recognition**: Precision/recall for entity extraction
- **Intent Classification**: Classification accuracy
- **Response Relevance**: Relevance scoring

---

## Conclusion

The tskgRAG system represents a comprehensive solution for natural language access to TeraSky's technical knowledge base. By combining the power of Neo4j's graph database with modern LLM capabilities, the system enables intuitive, conversational access to complex business intelligence.

### Key Success Factors
1. **Rich Data Model**: Comprehensive schema with 3,093+ nodes and 14,000+ relationships
2. **Real-time Integration**: Live Salesforce and MS Graph data
3. **Intelligent Query Processing**: Multi-strategy retrieval and generation
4. **Scalable Architecture**: Container-based deployment with monitoring
5. **Security-First Design**: Role-based access control and data filtering

### Implementation Roadmap
1. **Phase 1** (Weeks 1-4): Core API development and basic query types
2. **Phase 2** (Weeks 5-8): Advanced query processing and optimization
3. **Phase 3** (Weeks 9-12): Security, monitoring, and production deployment
4. **Phase 4** (Weeks 13-16): Testing, documentation, and user training

The system is designed to evolve with TeraSky's needs, providing a foundation for advanced analytics, predictive insights, and intelligent automation across the organization.

---

**Document Version**: 1.1.0  
**Last Updated**: 2025-11-10  
**Next Review**: 2025-12-10  
**Author**: TSKB-RAG Development Team

---

## AI Assistant Implementation Checklist

### Phase 1: Core API (Week 1-2)
- [ ] FastAPI application setup with health checks
- [ ] Neo4j connection and query execution
- [ ] Basic intent classification (5 query types)
- [ ] Simple Cypher query generation
- [ ] LLM integration for response generation

### Phase 2: Query Processing (Week 3-4)
- [ ] Entity extraction with spaCy
- [ ] Template-based query generation
- [ ] Response validation and formatting
- [ ] Error handling and fallback responses
- [ ] Basic caching with Redis

### Phase 3: Advanced Features (Week 5-6)
- [ ] Vector similarity search
- [ ] Hybrid retrieval strategies
- [ ] Performance optimization
- [ ] Security and access control
- [ ] Monitoring and analytics

### Phase 4: Production (Week 7-8)
- [ ] Docker containerization
- [ ] Comprehensive testing
- [ ] Documentation and deployment
- [ ] User training and feedback

### Success Criteria
- [ ] Query success rate > 95%
- [ ] Average response time < 2 seconds
- [ ] Support for all 5 query categories
- [ ] Accurate entity recognition
- [ ] Proper data source citations

### Recent Updates (v1.1.0)
- **OPPORTUNITY Relationships**: Migrated from PURCHASED to OPPORTUNITY with `opportunity_stage` property
- **Progress Monitoring**: Added real-time import progress tracking (every 50 items)
- **Business Intelligence**: Enhanced deal stage filtering for accurate revenue analysis
- **Performance Optimization**: Improved import pipeline with progress indicators and flush output

---

## Quick Start Guide for AI Assistant

### Essential Information
1. **Neo4j Connection**: `bolt://localhost:7687` (neo4j/password)
2. **Database Schema**: 9 node types, 9 relationship types (see schema section)
3. **Key Relationships**: OPPORTUNITY (deals), MANAGED_BY (account management), HAS_INSTALLED (deployments)
4. **Sample Queries**: See "Example Query Implementations" section
5. **API Framework**: FastAPI with Pydantic models

### Critical Implementation Notes
- **OPPORTUNITY Stage Filtering**: Always filter by `opportunity_stage = 'Closed Won'` for revenue queries
- **Entity Matching**: Use fuzzy matching for client/product names (case-insensitive)
- **Response Format**: Include data sources, confidence scores, and follow-up suggestions
- **Error Handling**: Validate entities exist before generating Cypher queries
- **Performance**: Use indexes on name fields, limit results with pagination

### Required Dependencies
```
fastapi>=0.104.0
neo4j>=5.15.0
openai>=1.0.0
uvicorn>=0.24.0
pydantic>=2.0.0
spacy>=3.7.0
scikit-learn>=1.3.0
redis>=5.0.0
```

---

## Docker Deployment

### Production Docker Command
```bash
sudo docker run --rm \
  --env-file ../.env \
  --network TS_AI_network \
  --network-alias tskb-chat-bot \
  -v /home/ubuntu/meetingsBotLogs:/app/logs \
  -v /home/ubuntu/ssl:/app/ssl:ro \
  tskb-chatbot
```

### Environment Variables (.env)
```bash
# Neo4j Configuration
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# AWS Bedrock Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# Application Configuration
API_PORT=8000
CONFIDENCE_THRESHOLD=0.7
MAX_QUERY_RESULTS=100
```

---

## AWS Bedrock Integration

### LLM Service Configuration
```python
import boto3
import json

class BedrockLLMClient:
    def __init__(self, region='us-east-1'):
        self.bedrock = boto3.client('bedrock-runtime', region_name=region)
        self.model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
    
    def generate_response(self, prompt, max_tokens=1000):
        """Generate response using AWS Bedrock"""
        response = self.bedrock.invoke_model(
            modelId=self.model_id,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        return json.loads(response['body'].read())
```

---

## Universal Query Support & Self-Learning

### Dynamic Schema Discovery
```python
def discover_schema(self):
    """Dynamically discover Neo4j schema and capabilities"""
    schema_query = """
    CALL db.schema.nodeTypeProperties() YIELD nodeType, propertyName, propertyTypes
    RETURN nodeType, collect({property: propertyName, types: propertyTypes}) as properties
    """
    return self.execute_query(schema_query)
```

### Confidence Calculation
```python
class ConfidenceCalculator:
    def calculate_confidence(self, query_result):
        """Calculate confidence score (0-100%)"""
        factors = {
            'entity_match_score': self._calculate_entity_confidence(query_result),
            'schema_alignment': self._calculate_schema_confidence(query_result),
            'result_completeness': self._calculate_completeness(query_result),
            'historical_accuracy': self._get_historical_accuracy(query_result)
        }
        
        weights = {'entity_match_score': 0.3, 'schema_alignment': 0.25, 
                  'result_completeness': 0.25, 'historical_accuracy': 0.2}
        
        confidence = sum(factors[k] * weights[k] for k in factors)
        return min(100, max(0, confidence))
```

### Self-Learning System
```python
class QueryLearningSystem:
    def learn_from_query(self, query, cypher, success, user_feedback):
        """Learn from query execution and user feedback"""
        pattern = self._extract_pattern(query)
        self.query_patterns[pattern].append({
            'query': query,
            'cypher': cypher,
            'success': success,
            'feedback': user_feedback,
            'timestamp': datetime.now()
        })
        self._optimize_future_queries(pattern)
```

---

## Updated Implementation Checklist

### Phase 1: Core Infrastructure (Week 1-2)
- [ ] FastAPI application with SSL support
- [ ] AWS Bedrock LLM integration
- [ ] Neo4j connection with dynamic schema discovery
- [ ] Docker container with TS_AI_network integration
- [ ] Logging system with volume mounting

### Phase 2: Universal Query Engine (Week 3-4)
- [ ] Dynamic schema analysis and understanding
- [ ] Universal query processing (unlimited question types)
- [ ] Confidence calculation system
- [ ] Entity extraction with fuzzy matching
- [ ] Cypher query generation from natural language

### Phase 3: Self-Learning System (Week 5-6)
- [ ] Query pattern learning and optimization
- [ ] Historical accuracy tracking
- [ ] User feedback integration
- [ ] Performance optimization based on usage
- [ ] Continuous schema adaptation

### Phase 4: Production & Monitoring (Week 7-8)
- [ ] SSL certificate integration
- [ ] Comprehensive error handling
- [ ] Performance monitoring and analytics
- [ ] User training and documentation
- [ ] Production deployment validation

### Success Criteria
- [ ] Query success rate > 95% with confidence scores
- [ ] Average response time < 2 seconds
- [ ] Support for unlimited query types
- [ ] Confidence accuracy > 85%
- [ ] Self-learning improvement rate > 10% monthly
- [ ] Docker deployment with SSL and logging

---

**Document Version**: 2.0.0  
**Last Updated**: 2025-11-10  
**Next Review**: 2025-12-10  
**Author**: TSKB-RAG Development Team

### Major Updates (v2.0.0)
- **AWS Bedrock Integration**: Replaced OpenAI/Claude with AWS Bedrock LLM services
- **Universal Query Support**: Removed hardcoded query categories, supports unlimited question types
- **Confidence Scoring**: Every response includes multi-factor confidence calculation (0-100%)
- **Self-Learning System**: Continuous improvement through query pattern learning
- **Docker Production**: Full containerization with SSL support and logging on TS_AI_network
- **Schema Discovery**: Dynamic Neo4j schema analysis for intelligent query generation