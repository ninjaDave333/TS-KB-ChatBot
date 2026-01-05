# TSKB-RAG Schema Update - OPPORTUNITY.close_date Field

**Date**: 2025-11-12  
**Version**: 2.4.0  
**Impact**: Critical for temporal queries and 2025 deal tracking

---

## Summary

Added `close_date` field to all OPPORTUNITY relationships to track actual deal close dates separately from line item creation dates.

---

## Schema Changes

### OPPORTUNITY Relationship (Updated)

**Pattern**: `(Client)-[:OPPORTUNITY]->(Product)`

**New Property**:
```json
{
  "close_date": "string (ISO) - Actual deal close date from Opportunity.CloseDate"
}
```

**Complete Relationship Properties**:
```json
{
  "sf_opportunity_line_item_id": "string (UNIQUE)",
  "opportunity_name": "string",
  "opportunity_stage": "string (Closed Won|Closed Lost|Qualification|etc.)",
  "close_date": "string (ISO) - Actual deal close date",
  "quantity": "number",
  "unit_price": "number",
  "total_price": "number",
  "description": "string",
  "purchased_date": "string (ISO) - Line item creation date",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

---

## Key Differences

| Field | Source | Purpose | Example |
|-------|--------|---------|---------|
| **close_date** | Opportunity.CloseDate | Actual deal close date | "2025-06-15T00:00:00Z" |
| **purchased_date** | OpportunityLineItem.CreatedDate | Line item creation date | "2024-06-15T00:00:00Z" |

**Important**: `close_date` is the authoritative field for temporal queries about when deals were actually closed.

---

## Query Updates for RAG System

### ❌ OLD (Incorrect for 2025 deals)
```cypher
MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
WHERE o.opportunity_stage = 'Closed Won'
AND o.purchased_date >= '2025-01-01'
RETURN c.name, p.name, o.total_price
```

### ✅ NEW (Correct)
```cypher
MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
WHERE o.opportunity_stage = 'Closed Won'
AND o.close_date >= '2025-01-01' AND o.close_date < '2026-01-01'
RETURN c.name, p.name, o.close_date, o.total_price
ORDER BY o.close_date DESC
```

---

## Common RAG Query Patterns

### 1. Deals Closed in Specific Year
```cypher
MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
WHERE o.opportunity_stage = 'Closed Won'
AND o.close_date >= '2025-01-01' AND o.close_date < '2026-01-01'
RETURN c.name as client, p.name as product, 
       o.close_date as close_date, o.total_price as value
ORDER BY o.close_date DESC
```

### 2. Revenue by Time Period
```cypher
MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
WHERE o.opportunity_stage = 'Closed Won'
AND o.close_date >= '2025-01-01' AND o.close_date < '2026-01-01'
RETURN date(o.close_date).year as year,
       date(o.close_date).month as month,
       sum(o.total_price) as monthly_revenue
ORDER BY year, month
```

### 3. Recent Deals (Last N Days)
```cypher
MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
WHERE o.opportunity_stage = 'Closed Won'
AND o.close_date >= date() - duration({days: 90})
RETURN c.name, p.name, o.close_date, o.total_price
ORDER BY o.close_date DESC
LIMIT 20
```

### 4. Deals by Product in Time Range
```cypher
MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
WHERE toLower(p.name) CONTAINS 'vault'
AND o.opportunity_stage = 'Closed Won'
AND o.close_date >= '2025-01-01'
RETURN c.name as client, p.name as product,
       o.close_date as close_date, o.total_price as value
ORDER BY o.close_date DESC
```

### 5. Client Purchase History with Dates
```cypher
MATCH (c:Client {name: 'Wix.com'})-[o:OPPORTUNITY]->(p:Product)
WHERE o.opportunity_stage = 'Closed Won'
RETURN p.name as product,
       o.close_date as close_date,
       o.total_price as value,
       o.quantity as quantity
ORDER BY o.close_date DESC
```

---

## Chatbot Query Generation Guidelines

### For Temporal Queries:
1. **Always use `close_date`** for "when was deal closed" questions
2. **Use `purchased_date`** only for "when was line item created" questions
3. **Filter by `opportunity_stage = 'Closed Won'`** for actual revenue
4. **Include date range filters** for specific time periods

### Example User Questions → Cypher:

**Q**: "How many clients purchased Vault in 2025?"
```cypher
MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
WHERE toLower(p.name) CONTAINS 'vault'
AND o.opportunity_stage = 'Closed Won'
AND o.close_date >= '2025-01-01' AND o.close_date < '2026-01-01'
RETURN count(DISTINCT c) as client_count
```

**Q**: "What's our revenue for Q1 2025?"
```cypher
MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)
WHERE o.opportunity_stage = 'Closed Won'
AND o.close_date >= '2025-01-01' AND o.close_date < '2025-04-01'
RETURN sum(o.total_price) as q1_revenue
```

**Q**: "Show me recent HashiCorp deals"
```cypher
MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)<-[:MAKES]-(v:Vendor {name: 'HashiCorp'})
WHERE o.opportunity_stage = 'Closed Won'
AND o.close_date >= date() - duration({days: 90})
RETURN c.name, p.name, o.close_date, o.total_price
ORDER BY o.close_date DESC
```

---

## Data Coverage

- **Total OPPORTUNITY relationships**: 10,032
- **Relationships with close_date**: 10,032 (100%)
- **Date range**: 2022-11-30 to 2025-11-12
- **Stage distribution**: Closed Won (~45%), Closed Lost (~25%), Pipeline (~30%)

---

## Migration Status

✅ **Completed**: All 10,032 OPPORTUNITY relationships updated with close_date field  
✅ **Verified**: 100% coverage of close_date property  
✅ **Tested**: Queries validated with 2025 deals  
✅ **Documented**: SchemaSync.md, CHANGELOG.md, tskgRAG.md updated  

---

## Integration Checklist for RAG System

- [ ] Update Cypher query templates to use `close_date` for temporal filters
- [ ] Modify intent classification to distinguish "close date" vs "creation date" queries
- [ ] Update response templates to include close_date in deal summaries
- [ ] Add date range validation for user queries (e.g., "2025" → "2025-01-01 to 2025-12-31")
- [ ] Test chatbot with sample queries: "deals closed in 2025", "recent wins", "Q1 revenue"
- [ ] Update schema documentation in RAG system configuration
- [ ] Add confidence scoring for temporal queries based on date field availability

---

## Support

For questions about this schema update:
- **Schema Reference**: `docs/SchemaSync.md` (v2.4.0)
- **Changelog**: `docs/CHANGELOG.md` (v2.4.0)
- **Query Examples**: `README.md` - Opportunity Queries section
- **Test Scripts**: `Tests/verify_opportunity_stages.py`

---

**End of Schema Update Document**
