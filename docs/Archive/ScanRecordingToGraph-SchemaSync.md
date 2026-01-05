# Teams Recording Scanner - Schema Synchronization Documentation

**Last Updated:** 2025-11-17  
**Version:** 2.0  
**Source:** RecordingScanner  

## Tool Purpose

The Teams Recording Scanner is an enterprise data discovery and integration tool that automatically scans Microsoft Teams recordings across an organization and creates a structured knowledge graph in Neo4j. The tool bridges the gap between Microsoft Graph API data and downstream AI/ML processing systems by:

- **Discovering** Teams recordings via Microsoft Graph API across all organizational users
- **Enriching** recording metadata with calendar context (participants, meeting details, timestamps)
- **Structuring** data into a graph database with proper relationships between recordings, meetings, and employees
- **Enabling** automated processing workflows for transcription, analysis, and knowledge extraction
- **Providing** a standardized data layer for RAG (Retrieval-Augmented Generation) systems and other AI applications

This tool serves as the foundational data pipeline for meeting intelligence platforms, enabling organizations to unlock insights from their Teams meeting recordings at scale.

## Overview

This document provides the complete schema structure, relationships, and data formats used by the Teams Recording Scanner tool. This schema is designed for consumption by other services and LLM-based systems that need to understand and work with the generated data.

## Core Node Types

### 1. Recording Node

**Label:** `Recording`  
**Primary Key:** `name` (filename)  
**Unique Identifier:** `contentUrl`  

#### Properties

| Property | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `name` | String | Yes | Recording filename (primary key) | `"Meeting Recording-20241117_143022.mp4"` |
| `contentUrl` | String | Yes | Microsoft Graph content URL (unique) | `"https://graph.microsoft.com/v1.0/drives/{id}/items/{id}"` |
| `meetingId` | String | Yes | iCalUid for linking to calendar events | `"040000008200E00074C5B7101A82E00800000000..."` |
| `title` | String | Yes | Human-readable meeting title | `"Weekly Team Standup"` |
| `meetingOwner` | String | Yes | Email of meeting organizer | `"john.doe@terasky.com"` |
| `createdDateTime` | DateTime | Yes | Recording creation timestamp (UTC) | `2024-11-17T14:30:22.123456Z` |
| `size` | Integer | Yes | File size in megabytes | `245` |
| `transcriptUrl` | String | No | URL to transcript (future use) | `""` |
| `analysisUrl` | String | No | URL to analysis results (future use) | `""` |
| `discovered_by` | String | Yes | Discovery method | `"API"` |
| `language` | String | Yes | Recording language | `"en-US"` |
| `source` | String | Yes | Source system | `"RecordingScanner"` |
| `status` | String | Yes | Processing status | `"new"`, `"processing"`, `"processed"`, `"failed"` |
| `processingStarted` | DateTime | No | When processing began | `2024-11-17T15:00:00.000000Z` |
| `processingCompleted` | DateTime | No | When processing finished | `2024-11-17T15:30:00.000000Z` |
| `processingFailed` | DateTime | No | When processing failed | `2024-11-17T15:15:00.000000Z` |
| `processingJobId` | String | No | External processing job ID | `"job-12345-abcde"` |
| `errorMessage` | String | No | Error details if failed | `"API timeout during processing"` |
| `retryCount` | Integer | No | Number of retry attempts | `3` |

#### Status Values

- `new`: Newly discovered, ready for processing
- `processing`: Currently being processed by external system
- `processed`: Successfully processed
- `failed`: Processing failed (see errorMessage)

### 2. CalendarEvent Node

**Label:** `CalendarEvent`  
**Primary Key:** `name` (iCalUid)  

#### Properties

| Property | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `name` | String | Yes | iCalUid (primary key for linking) | `"040000008200E00074C5B7101A82E00800000000..."` |
| `title` | String | Yes | Meeting subject/title | `"Weekly Team Standup"` |
| `owner` | String | Yes | Meeting organizer email | `"john.doe@terasky.com"` |
| `internalParticipants` | List[String] | Yes | Internal attendee emails | `["jane.smith@terasky.com", "bob.wilson@terasky.com"]` |
| `externalParticipants` | List[String] | Yes | External attendee emails | `["client@external.com"]` |
| `startTime` | DateTime | No | Meeting start time (UTC) | `2024-11-17T14:00:00.000000Z` |
| `endTime` | DateTime | No | Meeting end time (UTC) | `2024-11-17T15:00:00.000000Z` |
| `category` | String | Yes | Meeting type classification | `"internal"`, `"external"` |
| `source` | String | Yes | Source system | `"RecordingScanner"` |

#### Category Classification Logic

- `internal`: Only participants from internal domain (@terasky.com)
- `external`: Contains at least one external participant

### 3. Employee Node (Referenced)

**Label:** `Employee`  
**Note:** This node type is managed by other systems but referenced by this scanner.

#### Referenced Properties

| Property | Type | Description |
|----------|------|-------------|
| `email` | String | Employee email address (used for matching) |
| `name` | String | Employee display name |
| `azure_id` | String | Microsoft Azure AD user ID |
| `active` | Boolean | Whether employee is active |

### 4. ScanMetadata Node

**Label:** `ScanMetadata`  
**Primary Key:** `type`  

#### Properties

| Property | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `type` | String | Yes | Scan type (primary key) | `"full"`, `"incremental"` |
| `lastScanTime` | DateTime | Yes | Last successful scan timestamp | `2024-11-17T16:00:00.000000Z` |
| `updatedAt` | DateTime | Yes | Metadata update timestamp | `2024-11-17T16:00:00.000000Z` |
| `totalRecordingsFound` | Integer | Yes | Total recordings in last scan | `25` |
| `newRecordingsProcessed` | Integer | Yes | New recordings processed | `5` |
| `foundNewRecordings` | Integer | Yes | Alias for newRecordingsProcessed | `5` |
| `scanCount` | Integer | Yes | Total number of scans performed | `42` |
| `source` | String | Yes | Source system | `"RecordingScanner"` |

## Relationships

### 1. LINKED_TO Relationship

**Pattern:** `(Recording)-[:LINKED_TO]->(CalendarEvent)`

#### Description
Links recording files to their corresponding calendar events using iCalUid matching.

#### Properties
- No additional properties on relationship

#### Cardinality
- One-to-Many: Multiple recordings can link to the same calendar event
- Each recording links to exactly one calendar event

### 2. OWNER_OF Relationship

**Pattern:** `(Employee)-[:OWNER_OF]->(CalendarEvent)`

#### Description
Identifies the meeting organizer/owner.

#### Properties
- No additional properties on relationship

#### Cardinality
- One-to-Many: Employee can own multiple calendar events
- Each calendar event has exactly one owner

### 3. INVITED_TO Relationship

**Pattern:** `(Employee)-[:INVITED_TO]->(CalendarEvent)`

#### Description
Identifies meeting participants (internal employees only).

#### Properties
- No additional properties on relationship

#### Cardinality
- Many-to-Many: Employees can be invited to multiple meetings
- Calendar events can have multiple invited employees

## Data Flow and Processing Logic

### 1. Recording Discovery Process

```
Microsoft Graph API → File Metadata Extraction → iCalUid Extraction → Calendar Event Matching
```

#### Key Steps:
1. **User Enumeration**: Scan all users in organization or active employees
2. **Recording Retrieval**: Get recordings via `getAllRecordings` API
3. **Metadata Extraction**: Extract file metadata including iCalUid from source
4. **Size Filtering**: Skip recordings < 10MB
5. **Duplicate Detection**: Check existing recordings by filename
6. **Calendar Matching**: Match recordings to calendar events via iCalUid

### 2. Calendar Event Matching Strategy

#### Primary Method: iCalUid Direct Match
```cypher
MATCH (event) WHERE event.iCalUId = $ical_uid
```

#### Fallback Methods (in order):
1. **Organizer Calendar Search**: Search organizer's calendar by iCalUid
2. **CalendarView Time Window**: Search within recording date ±24 hours
3. **Attendee Calendar Search**: Search participant calendars
4. **Extended Time Window**: Search ±2 days for timezone issues
5. **OnlineMeetings Endpoint**: Search by externalId
6. **Fuzzy Time Matching**: Score-based matching (60% subject + 40% time proximity)

### 3. Data Linking Logic

#### Recording-to-CalendarEvent Linking
```cypher
MATCH (r:Recording {contentUrl: $content_url})
MATCH (c:CalendarEvent {name: $ical_uid})
MERGE (r)-[:LINKED_TO]->(c)
```

#### Employee-to-CalendarEvent Linking
```cypher
// Owner relationship
MATCH (e:Employee {email: $owner_email})
MATCH (c:CalendarEvent {name: $ical_uid})
MERGE (e)-[:OWNER_OF]->(c)

// Participant relationships
MATCH (e:Employee {email: $participant_email})
MATCH (c:CalendarEvent {name: $ical_uid})
MERGE (e)-[:INVITED_TO]->(c)
```

## Query Patterns for Consuming Services

### 1. Get All New Recordings for Processing

```cypher
MATCH (r:Recording {status: 'new'})
RETURN r.name as recordingName, r.contentUrl as contentUrl, r.title as title
ORDER BY r.createdDateTime ASC
```

### 2. Get Recording with Calendar Context

```cypher
MATCH (r:Recording)-[:LINKED_TO]->(c:CalendarEvent)
WHERE r.name = $recordingName
RETURN r, c
```

### 3. Get Meeting Participants

```cypher
MATCH (r:Recording {name: $recordingName})-[:LINKED_TO]->(c:CalendarEvent)
MATCH (owner:Employee)-[:OWNER_OF]->(c)
OPTIONAL MATCH (participant:Employee)-[:INVITED_TO]->(c)
RETURN owner, collect(participant) as participants, c
```

### 4. Get Recordings by Status and Time Range

```cypher
MATCH (r:Recording)
WHERE r.status = $status 
  AND r.createdDateTime >= datetime($startTime)
  AND r.createdDateTime <= datetime($endTime)
RETURN r
ORDER BY r.createdDateTime DESC
```

### 5. Update Recording Status

```cypher
MATCH (r:Recording {name: $recordingName})
SET r.status = $newStatus,
    r.processingStarted = CASE WHEN $newStatus = 'processing' THEN datetime() ELSE r.processingStarted END,
    r.processingCompleted = CASE WHEN $newStatus = 'processed' THEN datetime() ELSE r.processingCompleted END,
    r.processingFailed = CASE WHEN $newStatus = 'failed' THEN datetime() ELSE r.processingFailed END,
    r.errorMessage = CASE WHEN $newStatus = 'failed' THEN $errorMessage ELSE null END
RETURN r
```

## Configuration and Constants

### Domain Configuration
- **Internal Domain**: `terasky.com` (configurable via INTERNAL_DOMAIN)
- **Allowed Domain**: `terasky.com` (configurable via ALLOWED_DOMAIN)

### API Endpoints
- **Graph Base URL**: `https://graph.microsoft.com/v1.0`
- **Recording API**: `/users/{userId}/onlineMeetings/getAllRecordings(meetingOrganizerUserId='{userId}')`
- **File Metadata**: `/drives/{driveId}/items/{itemId}`
- **Calendar Events**: `/users/{userId}/calendar/events` or `/users/{userId}/calendar/calendarView`

### Processing Limits
- **Minimum File Size**: 10MB
- **API Timeout**: 90 seconds per request
- **Retry Logic**: Exponential backoff (10s, 20s, 40s, 80s, max 300s)
- **Concurrent Workers**: 5 (configurable, range 3-8 recommended)

## Data Quality and Validation

### Required Data Validation
1. **Recording Name**: Must be valid filename, not "Unknown.mp4"
2. **Content URL**: Must be accessible Microsoft Graph URL
3. **File Size**: Must be ≥ 10MB
4. **iCalUid**: Should be present in file metadata for proper linking
5. **Timestamps**: Must be valid ISO 8601 format with UTC timezone

### Data Integrity Checks
1. **Duplicate Prevention**: Check existing recordings by filename before creation
2. **Orphaned Records**: All recordings should link to calendar events
3. **Status Consistency**: Processing status should align with timestamps
4. **Email Validation**: Employee emails should match internal domain pattern

## Integration Points for Consuming Services

### 1. Meeting Bot API Integration
- **Input**: Recording names with status 'new'
- **Processing**: External transcription and analysis
- **Callback**: Status updates via webhook
- **Output**: Processed recordings with transcriptUrl and analysisUrl

### 2. Notification Service Integration
- **Triggers**: Scan completion, processing errors
- **Channels**: Email, Slack, AWS SNS
- **Data**: Scan statistics, error details

### 3. Automated Processing Workflow
- **Batch Processing**: Process recordings in configurable batches
- **Status Tracking**: Real-time status updates via callbacks
- **Error Handling**: Retry logic with exponential backoff
- **Job Management**: External job ID tracking

## Performance Characteristics

### Concurrent Processing (3.2x Performance Improvement)
- **Sequential Mode**: ~70 users/minute
- **Concurrent Mode**: ~222 users/minute (5 workers)
- **Optimal Workers**: 3-8 concurrent workers depending on organization size
- **Rate Limiting**: 600 API calls/minute with intelligent throttling

### Batch Optimizations
- **Existence Checking**: Single batch query for all recordings
- **Metadata Extraction**: Concurrent file metadata retrieval
- **Calendar Matching**: Sequential to maintain accuracy
- **Database Writes**: Transactional batches per meeting

## Error Handling and Recovery

### Common Error Scenarios
1. **API Rate Limiting (429)**: Exponential backoff retry
2. **File Not Found (404)**: Skip recording, log as deleted
3. **Permission Denied (403)**: Skip recording, log access issue
4. **Server Errors (5xx)**: Retry with backoff, mark user as failed after max attempts
5. **Calendar Access Issues**: Multiple fallback strategies
6. **Network Timeouts**: Configurable timeout with retry logic

### Recovery Mechanisms
- **Failed User Tracking**: Skip users with persistent failures
- **Incremental Scanning**: Resume from last successful timestamp
- **Status Reset**: Clear failure status for retry attempts
- **Graceful Degradation**: Continue processing other recordings on individual failures

---

**Note**: This schema is actively maintained and updated with each significant change to the Teams Recording Scanner. Consuming services should implement proper error handling and status checking when integrating with this data structure.