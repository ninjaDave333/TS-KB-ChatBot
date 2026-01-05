# MCP Integration Plan for TSKB-RAG

**Status**: Planned (Not Implemented)  
**Priority**: Medium  
**Estimated Effort**: 1-2 weeks  
**Target Version**: 3.0.0

---

## Overview

Enable TSKB-RAG to be accessed via Model Context Protocol (MCP), allowing other AI agents to query the TeraSky Knowledge Base programmatically.

---

## Use Cases

### 1. AI Agent Collaboration
- **Scenario**: Another AI agent needs TeraSky business data
- **Example**: "What HashiCorp products did we sell in 2024?"
- **Benefit**: Agents can access live data without human intervention

### 2. Multi-Agent Workflows
- **Scenario**: Sales agent queries TSKB-RAG for client history
- **Example**: "Get account manager for client X"
- **Benefit**: Automated workflows with real-time data

### 3. Cross-Service Integration
- **Scenario**: MeetingsBot queries TSKB-RAG for context
- **Example**: "Who attended meetings with client Y?"
- **Benefit**: Unified AI ecosystem across TeraSky services

---

## Technical Architecture

### MCP Server Implementation

```python
# app/mcp/server.py
from mcp.server import Server
from mcp.types import Tool, TextContent

class TSKBMCPServer(Server):
    """MCP server exposing TSKB-RAG capabilities"""
    
    def __init__(self):
        super().__init__("tskb-rag")
        self.register_tools()
    
    def register_tools(self):
        """Register available tools for AI agents"""
        
        @self.tool()
        async def query_knowledge_base(
            question: str,
            intent: str = "auto"
        ) -> TextContent:
            """
            Query TeraSky Knowledge Base with natural language.
            
            Args:
                question: Natural language question
                intent: Optional intent hint (sales_v1, calendar_v1, product_v1, strict_v1)
            
            Returns:
                Natural language answer with data
            """
            # Call existing RAG pipeline
            result = await process_query(question, intent)
            return TextContent(
                type="text",
                text=result["answer"]
            )
        
        @self.tool()
        async def get_cypher_query(
            question: str
        ) -> TextContent:
            """
            Generate Cypher query from natural language.
            
            Args:
                question: Natural language question
            
            Returns:
                Validated Cypher query
            """
            # Generate and validate Cypher
            cypher = await generate_cypher(question)
            return TextContent(
                type="text",
                text=cypher
            )
        
        @self.tool()
        async def execute_cypher(
            cypher: str
        ) -> TextContent:
            """
            Execute Cypher query directly (advanced users).
            
            Args:
                cypher: Valid Cypher query
            
            Returns:
                JSON results
            """
            # Validate and execute
            results = await execute_query(cypher)
            return TextContent(
                type="text",
                text=json.dumps(results)
            )
        
        @self.tool()
        async def get_schema_info(
            node_type: str = None
        ) -> TextContent:
            """
            Get Neo4j schema information.
            
            Args:
                node_type: Optional specific node type
            
            Returns:
                Schema description
            """
            schema = await get_schema(node_type)
            return TextContent(
                type="text",
                text=json.dumps(schema)
            )
```

### MCP Client Usage Example

```python
# Example: Another AI agent using TSKB-RAG via MCP
from mcp.client import Client

async def sales_agent_workflow():
    """Sales agent queries TSKB-RAG for client data"""
    
    client = Client("tskb-rag")
    
    # Query 1: Get client history
    result = await client.call_tool(
        "query_knowledge_base",
        question="What products did Wix purchase in 2024?",
        intent="sales_v1"
    )
    print(result.text)
    
    # Query 2: Get account manager
    result = await client.call_tool(
        "query_knowledge_base",
        question="Who is the account manager for Wix?",
        intent="sales_v1"
    )
    print(result.text)
    
    # Query 3: Get meeting history
    result = await client.call_tool(
        "query_knowledge_base",
        question="How many meetings did we have with Wix in 2024?",
        intent="calendar_v1"
    )
    print(result.text)
```

---

## Implementation Plan

### Phase 1: MCP Server Setup (Week 1)
1. **Install MCP SDK**
   ```bash
   pip install mcp-sdk
   ```

2. **Create MCP Server Module**
   - `app/mcp/__init__.py`
   - `app/mcp/server.py`
   - `app/mcp/tools.py`

3. **Register Core Tools**
   - `query_knowledge_base`: Main RAG query
   - `get_cypher_query`: Cypher generation only
   - `execute_cypher`: Direct execution
   - `get_schema_info`: Schema introspection

4. **Testing**
   - Unit tests for each tool
   - Integration tests with MCP client
   - Error handling validation

### Phase 2: Security & Authentication (Week 1)
1. **MCP Authentication**
   - JWT token validation for MCP clients
   - Service-to-service authentication
   - Rate limiting per client

2. **Authorization**
   - Tool-level permissions
   - Query result filtering by client
   - Audit logging for MCP calls

3. **Security Hardening**
   - Input validation for all tools
   - Cypher injection prevention
   - Resource limits (query timeout, result size)

### Phase 3: Integration & Deployment (Week 2)
1. **Docker Integration**
   - Add MCP server to Docker container
   - Expose MCP port (default: 8003)
   - Update docker-compose.yml

2. **Documentation**
   - MCP tool reference
   - Client integration guide
   - Example workflows

3. **Monitoring**
   - MCP call metrics
   - Tool usage analytics
   - Error tracking

---

## MCP Tools Reference

### Tool: query_knowledge_base
**Purpose**: Main RAG query interface  
**Input**: Natural language question + optional intent  
**Output**: Natural language answer with data  
**Use Case**: General knowledge base queries

### Tool: get_cypher_query
**Purpose**: Generate Cypher without execution  
**Input**: Natural language question  
**Output**: Validated Cypher query  
**Use Case**: Query generation for external execution

### Tool: execute_cypher
**Purpose**: Direct Cypher execution  
**Input**: Cypher query string  
**Output**: JSON results  
**Use Case**: Advanced users with Cypher knowledge

### Tool: get_schema_info
**Purpose**: Schema introspection  
**Input**: Optional node type filter  
**Output**: Schema description  
**Use Case**: Understanding data structure

---

## Security Considerations

### Authentication
- **JWT Tokens**: Service-to-service authentication
- **API Keys**: Alternative for simple clients
- **Domain Restriction**: Only TeraSky services allowed

### Authorization
- **Tool Permissions**: Different clients get different tools
- **Query Filtering**: Results filtered by client permissions
- **Audit Trail**: All MCP calls logged with client ID

### Rate Limiting
- **Per Client**: 100 queries/minute default
- **Per Tool**: Different limits for different tools
- **Burst Protection**: Prevent abuse

---

## Configuration

### Environment Variables
```env
# MCP Server Configuration
MCP_ENABLED=true
MCP_PORT=8003
MCP_HOST=0.0.0.0

# MCP Authentication
MCP_JWT_SECRET=<64-char-hex-secret>
MCP_ALLOWED_CLIENTS=meetingsBot,salesAgent,analyticsAgent

# MCP Rate Limiting
MCP_RATE_LIMIT_PER_MINUTE=100
MCP_RATE_LIMIT_BURST=20
```

### MCP Config File
```yaml
# config/mcp_config.yaml
server:
  name: "tskb-rag"
  version: "1.0.0"
  port: 8003

tools:
  query_knowledge_base:
    enabled: true
    rate_limit: 100
    timeout: 30
  
  get_cypher_query:
    enabled: true
    rate_limit: 50
    timeout: 10
  
  execute_cypher:
    enabled: false  # Disabled by default for security
    rate_limit: 10
    timeout: 30
  
  get_schema_info:
    enabled: true
    rate_limit: 20
    timeout: 5

clients:
  meetingsBot:
    allowed_tools: ["query_knowledge_base", "get_schema_info"]
    rate_limit: 200
  
  salesAgent:
    allowed_tools: ["query_knowledge_base"]
    rate_limit: 100
  
  analyticsAgent:
    allowed_tools: ["query_knowledge_base", "get_cypher_query"]
    rate_limit: 50
```

---

## Benefits

### For AI Agents
- **Programmatic Access**: Query TSKB-RAG without human intervention
- **Real-time Data**: Always current business data
- **Natural Language**: No need to learn Cypher

### For TeraSky
- **Unified AI Ecosystem**: All agents can access knowledge base
- **Automation**: Automated workflows with live data
- **Scalability**: Multiple agents can query simultaneously

### For Developers
- **Standard Protocol**: MCP is industry standard
- **Easy Integration**: Simple client libraries
- **Extensibility**: Easy to add new tools

---

## Testing Strategy

### Unit Tests
- Test each MCP tool independently
- Mock RAG pipeline for fast tests
- Validate input/output formats

### Integration Tests
- Test MCP client → server communication
- Validate authentication flow
- Test error handling

### Load Tests
- Simulate multiple concurrent clients
- Test rate limiting
- Validate performance under load

---

## Monitoring & Metrics

### MCP-Specific Metrics
- **Tool Usage**: Calls per tool per client
- **Response Times**: Latency per tool
- **Error Rates**: Failures per tool per client
- **Rate Limit Hits**: Throttling events

### Dashboard Integration
- Add MCP metrics to existing dashboard
- Real-time MCP call monitoring
- Client usage analytics

---

## Future Enhancements

### Phase 2 Features
- **Streaming Responses**: For long-running queries
- **Batch Queries**: Multiple questions in one call
- **Subscription Model**: Push updates to clients
- **Advanced Tools**: Aggregation, trend analysis, predictions

### Phase 3 Features
- **Multi-Language Support**: Tools in multiple languages
- **Custom Tools**: Client-specific tool registration
- **Federated Queries**: Query multiple knowledge bases
- **AI-to-AI Collaboration**: Agents collaborate on complex queries

---

## Dependencies

### Required Packages
```txt
mcp-sdk>=1.0.0
pydantic>=2.0.0
fastapi>=0.100.0
```

### Optional Packages
```txt
redis>=5.0.0  # For rate limiting
prometheus-client>=0.19.0  # For metrics
```

---

## Rollout Plan

### Week 1: Development
- Implement MCP server
- Create core tools
- Unit testing

### Week 2: Integration
- Docker integration
- Security hardening
- Documentation

### Week 3: Beta Testing
- Deploy to test environment
- Test with meetingsBot
- Gather feedback

### Week 4: Production
- Deploy to production
- Monitor performance
- Iterate based on usage

---

## Success Criteria

### Technical
- ✅ All 4 core tools working
- ✅ Authentication & authorization implemented
- ✅ Rate limiting functional
- ✅ 100% test coverage

### Performance
- ✅ <100ms MCP overhead
- ✅ Support 10+ concurrent clients
- ✅ 99.9% uptime

### Adoption
- ✅ 3+ AI agents using MCP
- ✅ 1000+ MCP calls/day
- ✅ <1% error rate

---

**Last Updated**: 2025-01-XX  
**Next Review**: After v2.1.0 release  
**Owner**: TeraSky AI Team
