# Teams Recording Query Requirements

**Date**: 2025-11-17  
**Priority**: HIGH  
**Status**: IMPLEMENTATION REQUIRED

## Required Query Capabilities

### 1. External Meeting Analytics
**Query**: "How many external meetings recorded during 2025?"

**Requirements**:
- Count recordings with external participants
- Filter by 2025 date range
- Distinguish internal vs external meetings

**Cypher Pattern**:
```cypher
MATCH (r:Recording)-[:LINKED_TO]->(c:CalendarEvent)
WHERE r.createdDateTime >= '2025-01-01T00:00:00Z' 
AND r.createdDateTime < '2026-01-01T00:00:00Z'
AND size(c.externalParticipants) > 0
RETURN count(r) as external_meetings_recorded
```

### 2. Employee Meeting Breakdown
**Query**: "How many meetings owned by David Gidony recorded during 2025, show total number, internal number and external number"

**Requirements**:
- Find specific employee by name
- Count owned meetings with recordings
- Separate internal vs external meetings
- 2025 date filtering

**Cypher Pattern**:
```cypher
MATCH (e:Employee)-[:OWNER_OF]->(c:CalendarEvent)<-[:LINKED_TO]-(r:Recording)
WHERE toLower(e.name) CONTAINS 'david gidony'
AND r.createdDateTime >= '2025-01-01T00:00:00Z' 
AND r.createdDateTime < '2026-01-01T00:00:00Z'
WITH c, r
RETURN 
  count(r) as total_recorded_meetings,
  sum(CASE WHEN size(c.externalParticipants) = 0 THEN 1 ELSE 0 END) as internal_meetings,
  sum(CASE WHEN size(c.externalParticipants) > 0 THEN 1 ELSE 0 END) as external_meetings
```

### 3. Most Active Employee (Annual)
**Query**: "Who is the most active employee meeting wise (most owned and participated in meetings) during 2025?"

**Requirements**:
- Combine OWNER_OF and INVITED_TO relationships
- Count total meeting participation
- Rank employees by activity
- 2025 date filtering

**Cypher Pattern**:
```cypher
MATCH (e:Employee)-[rel:OWNER_OF|INVITED_TO]->(c:CalendarEvent)
WHERE c.startTime >= '2025-01-01T00:00:00Z' 
AND c.startTime < '2026-01-01T00:00:00Z'
WITH e, count(DISTINCT c) as total_meetings,
     sum(CASE WHEN type(rel) = 'OWNER_OF' THEN 1 ELSE 0 END) as owned_meetings,
     sum(CASE WHEN type(rel) = 'INVITED_TO' THEN 1 ELSE 0 END) as participated_meetings
RETURN e.name, total_meetings, owned_meetings, participated_meetings
ORDER BY total_meetings DESC LIMIT 1
```

### 4. Most Active Employee (Monthly)
**Query**: "Who is the most active employee meeting wise (most owned and participated in meetings) during July 2025?"

**Requirements**:
- Same as annual but July 2025 specific
- Month-specific date filtering

**Cypher Pattern**:
```cypher
MATCH (e:Employee)-[rel:OWNER_OF|INVITED_TO]->(c:CalendarEvent)
WHERE c.startTime >= '2025-07-01T00:00:00Z' 
AND c.startTime < '2025-08-01T00:00:00Z'
WITH e, count(DISTINCT c) as total_meetings,
     sum(CASE WHEN type(rel) = 'OWNER_OF' THEN 1 ELSE 0 END) as owned_meetings,
     sum(CASE WHEN type(rel) = 'INVITED_TO' THEN 1 ELSE 0 END) as participated_meetings
RETURN e.name, total_meetings, owned_meetings, participated_meetings
ORDER BY total_meetings DESC LIMIT 1
```

### 5. Top Client Meeting Activity
**Query**: "Top 3 clients that had the most recorded meetings during 2025, try to list their meeting subjects"

**Requirements**:
- Link clients to recorded meetings
- Count meetings per client
- Include meeting subjects/titles
- Top 3 ranking

**Cypher Pattern**:
```cypher
MATCH (c:Client)-[:MANAGED_BY]->(e:Employee)-[:OWNER_OF|INVITED_TO]->(ce:CalendarEvent)<-[:LINKED_TO]-(r:Recording)
WHERE r.createdDateTime >= '2025-01-01T00:00:00Z' 
AND r.createdDateTime < '2026-01-01T00:00:00Z'
WITH c, count(DISTINCT r) as recorded_meetings, collect(DISTINCT ce.title)[0..5] as sample_subjects
RETURN c.sf_name as client_name, recorded_meetings, sample_subjects
ORDER BY recorded_meetings DESC LIMIT 3
```

## Implementation Challenges

### 1. Date Field Alignment
**Issue**: Recording.createdDateTime vs CalendarEvent.startTime
**Solution**: Use appropriate date field based on query context

### 2. Client-Meeting Linking
**Issue**: No direct Client-CalendarEvent relationship
**Solution**: Link via Employee (account managers) participation

### 3. External Meeting Detection
**Issue**: Define "external" meeting criteria
**Solution**: Use externalParticipants array size > 0

### 4. Employee Name Matching
**Issue**: Partial name matching (David Gidony)
**Solution**: Use toLower() and CONTAINS for flexible matching

## Query Complexity Levels

### Level 1: Simple Counts
- External meetings count
- Employee meeting counts

### Level 2: Aggregated Analytics  
- Meeting breakdowns (internal/external)
- Employee activity rankings

### Level 3: Complex Relationships
- Client meeting activity via employee relationships
- Multi-dimensional analytics

## Testing Requirements

### 1. Data Validation
- Verify date ranges work correctly
- Confirm external participant detection
- Test employee name matching

### 2. Performance Testing
- Large dataset query performance
- Complex relationship traversal timing
- Result accuracy validation

### 3. Edge Cases
- Employees with no meetings
- Meetings with no recordings
- Missing external participant data

## Answer Generation Patterns

### Count Responses
```
"During 2025, there were X external meetings recorded, representing Y% of all recorded meetings."
```

### Employee Analytics
```
"David Gidony owned X recorded meetings in 2025: Y internal meetings and Z external meetings, totaling W meetings."
```

### Ranking Responses
```
"The most active employee in 2025 was [Name] with X total meetings (Y owned, Z participated)."
```

### Client Analytics
```
"Top 3 clients with most recorded meetings in 2025:
1. [Client] - X meetings (subjects: [list])
2. [Client] - Y meetings (subjects: [list])  
3. [Client] - Z meetings (subjects: [list])"
```

## Implementation Priority

### Phase 1: Basic Queries (Week 1)
- [x] External meeting counts
- [x] Employee meeting breakdowns
- [x] Date filtering validation

### Phase 2: Analytics Queries (Week 2)  
- [ ] Employee activity rankings
- [ ] Monthly vs annual comparisons
- [ ] Performance optimization

### Phase 3: Complex Relationships (Week 3)
- [ ] Client meeting activity
- [ ] Multi-dimensional analytics
- [ ] Advanced answer generation

## Success Criteria

### Accuracy
- ✅ Correct date filtering (2025, July 2025)
- ✅ Accurate relationship traversal
- ✅ Proper external meeting detection

### Performance
- ✅ Query execution < 5 seconds
- ✅ Handles large datasets efficiently
- ✅ Optimized relationship patterns

### User Experience
- ✅ Natural language answers
- ✅ Contextual data presentation
- ✅ Actionable insights provided

---

**Next Actions**:
1. Implement and test all 5 query patterns
2. Add to schema descriptions and answer generator
3. Create comprehensive test suite
4. Validate with actual data
5. Optimize performance and accuracy