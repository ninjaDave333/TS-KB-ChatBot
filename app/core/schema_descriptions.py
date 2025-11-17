"""
Schema Description Layer - Internal MCP for LLM Query Generation
Provides detailed context for each node type and relationship pattern
"""

SCHEMA_DESCRIPTIONS = {
    "CRITICAL_SYNTAX_RULES": {
        "NO_TRAILING_COMMAS": "NEVER end RETURN statements with commas - always complete the statement",
        "COMPLETE_RETURNS": "Examples: 'RETURN total, samples' NOT 'RETURN total,'",
        "VALIDATE_SYNTAX": "Every generated query must be syntactically complete"
    },
    "nodes": {
        "Client": {
            "purpose": "Customer accounts from Salesforce",
            "primary_key": "sf_id",
            "name_field": "sf_name",  # CRITICAL: Use sf_name, NOT name
            "key_properties": {
                "sf_id": "Unique Salesforce Account ID - links to opportunities/assets",
                "sf_name": "Client name - USE THIS for name searches, not 'name'",
                "name": "Often empty - DO NOT USE, use sf_name instead",
                "sf_type": "Customer|Prospect|Partner",
                "sf_billing_country": "Country name - maps to Region nodes",
                "region": "Derived region code: IL|US|UK",
                "sf_owner_id": "Links to Employee.sf_id",
                "sf_owner_email": "Links to Employee.email",
                "sf_account_manager_cloud_id": "Links to Employee.sf_id",
                "sf_industry": "Industry classification",
                "sf_company_size": "Enterprise|SMB|etc",
                "sf_account_status": "Active|Inactive",
                "sf_active_contract": "boolean"
            },
            "search_patterns": [
                "MATCH (c:Client) WHERE toLower(c.sf_name) CONTAINS toLower('searchterm')",
                "MATCH (c:Client {sf_id: 'exact_id'})"
            ],
            "common_values": {
                "sf_type": ["Customer", "Prospect", "Partner"],
                "region": ["IL", "US", "UK"],
                "sf_company_size": ["Enterprise", "SMB", "Mid-Market"]
            }
        },
        
        "Employee": {
            "purpose": "Staff from MS Graph + Salesforce",
            "primary_key": "azure_id",
            "name_field": "name",
            "key_properties": {
                "azure_id": "Primary key from MS Graph",
                "sf_id": "Salesforce User ID - links to Client ownership",
                "name": "Full name",
                "email": "terasky.com email - links to Client.sf_owner_email",
                "title": "Job title",
                "sf_team": "Team name - links to BU.name",
                "sf_group": "Group name - links to BU.name", 
                "sf_location": "Location code: IL|US|UK - links to Region.name",
                "sf_default_geo": "Geographic region - links to Region.name",
                "ms_department": "Department from MS Graph"
            },
            "search_patterns": [
                "MATCH (e:Employee) WHERE toLower(e.name) CONTAINS toLower('searchterm')",
                "MATCH (e:Employee {email: 'exact@terasky.com'})"
            ]
        },
        
        "Product": {
            "purpose": "Products/services from Salesforce",
            "primary_key": "name",
            "name_field": "name",
            "key_properties": {
                "sf_id": "Salesforce Product2 ID",
                "name": "Product name - stable identifier",
                "sf_name": "Salesforce product name",
                "vendor": "Vendor name - links to Vendor.name",
                "sf_vendor": "Salesforce vendor field",
                "sf_family": "Product family/category",
                "sf_business_unit": "Links to BU.name",
                "sf_delivery_team": "Links to Skill.name",
                "sf_strategic_vendor": "boolean - strategic vendor flag",
                "sf_is_active": "boolean - active product flag"
            },
            "search_patterns": [
                "MATCH (p:Product) WHERE toLower(p.name) CONTAINS toLower('searchterm')",
                "MATCH (p:Product {sf_strategic_vendor: true})"
            ]
        },
        
        "Vendor": {
            "purpose": "Product vendors/manufacturers",
            "primary_key": "name",
            "name_field": "name",
            "key_properties": {
                "name": "Vendor name - links from Product.vendor or Product.sf_vendor"
            },
            "common_values": {
                "name": ["HashiCorp", "AWS", "Microsoft", "Google", "VMware"]
            }
        },
        
        "Region": {
            "purpose": "Geographic regions",
            "primary_key": "name", 
            "name_field": "name",
            "key_properties": {
                "name": "Region code: IL|US|UK",
                "description": "Full region name"
            },
            "valid_values": ["IL", "US", "UK"],
            "country_mapping": {
                "Israel": "IL",
                "United States": "US", 
                "USA": "US",
                "Germany": "UK",
                "United Kingdom": "UK",
                "UK": "UK"
            }
        },
        
        "Skill": {
            "purpose": "Technical skills/competencies",
            "primary_key": "name",
            "name_field": "name", 
            "key_properties": {
                "name": "Skill name - links from Product.sf_delivery_team",
                "category": "DevOps|Cloud|Security|Data|Infrastructure",
                "description": "Skill description"
            },
            "common_values": {
                "category": ["DevOps", "Cloud", "Security", "Data", "Infrastructure"],
                "name": ["kubernetes", "terraform", "aws", "azure", "docker"]
            }
        },
        
        "BU": {
            "purpose": "Business Units from Salesforce teams/groups",
            "primary_key": "name",
            "name_field": "name",
            "key_properties": {
                "name": "BU name - links from Employee.sf_team, Employee.sf_group, Product.sf_business_unit",
                "sf_source": "group|team - source type"
            }
        },
        
        "Recording": {
            "purpose": "Teams meeting recordings with transcription and analysis (490 nodes)",
            "primary_key": "name",
            "name_field": "name",
            "key_properties": {
                "name": "Recording filename - unique identifier",
                "title": "Meeting title/subject",
                "contentUrl": "Microsoft Graph URL to recording file",
                "status": "Processing status: new|processing|processed|failed",
                "createdDateTime": "Recording creation timestamp (ISO)",
                "size": "File size in bytes (NOT sizeInBytes)",
                "meetingId": "Teams meeting identifier",
                "meetingOwner": "Meeting organizer email",
                "transcriptUrl": "Direct URL to transcript file (empty until processed)",
                "analysisUrl": "Direct URL to analysis results (empty until processed)",
                "language": "Recording language (e.g. en-US)",
                "processingStarted": "Processing start timestamp",
                "processingFailed": "Processing failure timestamp",
                "errorMessage": "Error details if processing failed"
            },
            "search_patterns": [
                "MATCH (r:Recording) WHERE toLower(r.title) CONTAINS toLower('searchterm')",
                "MATCH (r:Recording {status: 'processed'}) WHERE r.transcriptUrl <> ''"
            ],
            "common_values": {
                "status": ["processed", "new", "processing", "failed"],
                "common_errors": ["Meeting Bot API call failed", "Recording file not accessible", "Transcription service unavailable"]
            }
        },
        
        "CalendarEvent": {
            "purpose": "Meeting events from Microsoft Graph calendar (470 nodes)",
            "primary_key": "name",
            "name_field": "title",
            "key_properties": {
                "name": "iCalUid - unique calendar identifier",
                "title": "Meeting subject/title (NOT subject)",
                "startTime": "Meeting start time (ISO)",
                "endTime": "Meeting end time (ISO)",
                "owner": "Meeting organizer email (NOT organizer)",
                "category": "Meeting category",
                "internalParticipants": "Array of @terasky.com email strings",
                "externalParticipants": "Array of external email strings"
            },
            "search_patterns": [
                "MATCH (c:CalendarEvent) WHERE toLower(c.title) CONTAINS toLower('searchterm')",
                "MATCH (c:CalendarEvent) WHERE c.startTime >= '2024-11-01T00:00:00Z'",
                "MATCH (c:CalendarEvent) WHERE ANY(email IN c.internalParticipants WHERE email CONTAINS 'searchterm')"
            ],
            "participant_queries": {
                "internal_search": "ANY(email IN c.internalParticipants WHERE email CONTAINS 'term')",
                "external_search": "ANY(email IN c.externalParticipants WHERE email CONTAINS 'term')"
            }
        },
        
        "ScanMetadata": {
            "purpose": "Teams recording scan execution tracking (2 nodes)",
            "primary_key": "type",
            "name_field": "type",
            "key_properties": {
                "type": "Scan type identifier (full|incremental)",
                "lastScanTime": "Last successful scan timestamp",
                "totalRecordingsFound": "Total recordings discovered",
                "newRecordingsProcessed": "New recordings processed in last scan",
                "scanCount": "Total number of scans performed",
                "source": "RecordingScanner"
            }
        }
    },
    
    "relationships": {
        "OPPORTUNITY": {
            "pattern": "(Client)-[:OPPORTUNITY]->(Product)",
            "purpose": "Client purchased/bought products from OpportunityLineItem",
            "properties": {
                "sf_opportunity_line_item_id": "Unique OpportunityLineItem ID",
                "opportunity_name": "Deal name",
                "opportunity_stage": "Deal stage - USE 'Closed Won' for successful deals",
                "close_date": "Actual deal close date (ISO) - USE THIS for temporal queries",
                "quantity": "Number of units",
                "unit_price": "Price per unit", 
                "total_price": "Total deal value - USE THIS for cost/amount calculations, NOT 'amount'",
                "purchased_date": "Line item creation date (ISO) - rarely used",
                "description": "Deal description"
            },
            "cost_calculation": {
                "field_name": "total_price",
                "note": "NO 'amount' field exists - always use o.total_price for deal costs",
                "aggregation": "sum(toFloat(o.total_price)) for total cost"
            },
            "temporal_queries": {
                "primary_field": "close_date",
                "note": "ALWAYS use o.close_date for temporal queries, NOT o.purchased_date",
                "year_filter": "o.close_date >= '2025-01-01' AND o.close_date < '2026-01-01'"
            },
            "common_stages": ["Closed Won", "Closed Lost", "Qualification", "Quote Preparation"],
            "query_examples": [
                "// Find successful deals for client",
                "MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)",
                "WHERE toLower(c.sf_name) CONTAINS 'wix' AND o.opportunity_stage = 'Closed Won'",
                "RETURN c.sf_name, p.name, o.total_price, o.purchased_date",
                "",
                "// Find 2025 deals",
                "MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product)",
                "WHERE o.opportunity_stage = 'Closed Won' AND o.close_date >= '2025-01-01' AND o.close_date < '2026-01-01'",
                "RETURN c.sf_name, p.name, o.close_date, o.total_price"
            ]
        },
        
        "HAS_INSTALLED": {
            "pattern": "(Client)-[:HAS_INSTALLED]->(Product)", 
            "purpose": "Client has installed/deployed products from Assets",
            "properties": {
                "sf_asset_id": "Unique Asset ID",
                "asset_name": "Asset name",
                "status": "Installed|Shipped|Registered",
                "quantity": "Number installed",
                "install_date": "Installation date",
                "usage_end_date": "License/usage end date"
            },
            "common_statuses": ["Installed", "Shipped", "Registered"]
        },
        
        "MANAGED_BY": {
            "pattern": "(Client)-[:MANAGED_BY]->(Employee)",
            "purpose": "Client account ownership/management",
            "matching_logic": [
                "Client.sf_owner_email = Employee.email (primary)",
                "Client.sf_owner_id = Employee.sf_id (secondary)", 
                "Client.sf_account_manager_cloud_id = Employee.sf_id (tertiary)"
            ],
            "query_examples": [
                "// Find client's account manager",
                "MATCH (c:Client)-[:MANAGED_BY]->(e:Employee)",
                "WHERE toLower(c.sf_name) CONTAINS 'wix'",
                "RETURN c.sf_name, e.name, e.email"
            ]
        },
        
        "LOCATED_IN": {
            "pattern": "(Employee)-[:LOCATED_IN]->(Region)",
            "purpose": "Employee geographic location mapping",
            "matching_logic": [
                "Employee.sf_location = Region.name OR Employee.sf_default_geo = Region.name"
            ],
            "note": "Clients do NOT use LOCATED_IN - they have direct region property"
        },
        
        "BELONGS_TO": {
            "pattern": "(Employee|Product)-[:BELONGS_TO]->(BU)",
            "purpose": "Business unit assignment",
            "matching_logic": [
                "Employee.sf_team = BU.name OR Employee.sf_group = BU.name",
                "Product.sf_business_unit = BU.name"
            ]
        },
        
        "MAKES": {
            "pattern": "(Vendor)-[:MAKES]->(Product)",
            "purpose": "Vendor manufactures/provides product",
            "matching_logic": [
                "Vendor.name = Product.vendor OR Vendor.name = Product.sf_vendor"
            ]
        },
        
        "HAS_SKILL": {
            "pattern": "(Employee)-[:HAS_SKILL]->(Skill)",
            "purpose": "Employee technical competencies (legacy/manual)"
        },
        
        "REQUIRES_SKILL": {
            "pattern": "(Product)-[:REQUIRES_SKILL]->(Skill)",
            "purpose": "Product requires specific skills for delivery",
            "matching_logic": [
                "Product.sf_delivery_team = Skill.name"
            ]
        },
        
        "SUPPORTS": {
            "pattern": "(Product)-[:SUPPORTS]->(Compliance)",
            "purpose": "Product supports compliance standards (legacy)"
        },
        
        "LINKED_TO": {
            "pattern": "(Recording)-[:LINKED_TO]->(CalendarEvent)",
            "purpose": "Recording files linked to their calendar events via iCalUid",
            "matching_logic": [
                "Recording extracted iCalUid matches CalendarEvent.name"
            ],
            "cardinality": "Many-to-One (multiple recordings per meeting)",
            "query_examples": [
                "// Find recording with meeting context",
                "MATCH (r:Recording)-[:LINKED_TO]->(c:CalendarEvent)",
                "WHERE toLower(r.title) CONTAINS 'terraform'",
                "RETURN r.name, r.status, c.title, c.startTime"
            ]
        },
        
        "OWNER_OF": {
            "pattern": "(Employee)-[:OWNER_OF]->(CalendarEvent)",
            "purpose": "Employee owns/organizes calendar events",
            "matching_logic": [
                "Employee.email matches CalendarEvent.owner"
            ],
            "cardinality": "One-to-Many (employee owns multiple meetings)",
            "query_examples": [
                "// Find employee's organized meetings",
                "MATCH (e:Employee)-[:OWNER_OF]->(c:CalendarEvent)",
                "WHERE toLower(e.name) CONTAINS 'john'",
                "RETURN e.name, c.title, c.startTime ORDER BY c.startTime DESC"
            ]
        },
        
        "INVITED_TO": {
            "pattern": "(Employee)-[:INVITED_TO]->(CalendarEvent)",
            "purpose": "Employee invited to/participated in calendar events",
            "matching_logic": [
                "Employee.email in CalendarEvent.internalParticipants"
            ],
            "cardinality": "Many-to-Many (employees attend multiple meetings)",
            "query_examples": [
                "// Find employee's meeting participation",
                "MATCH (e:Employee)-[:INVITED_TO]->(c:CalendarEvent)",
                "WHERE toLower(e.name) CONTAINS 'jane'",
                "RETURN e.name, c.title, c.startTime ORDER BY c.startTime DESC LIMIT 10"
            ]
        }
    },
    
    "working_examples": {
        "count_and_sample_clients_by_vendor": {
            "query": "how many clients use hashicorp products and show 5 names",
            "cypher": "MATCH (c:Client)-[rel:OPPORTUNITY|HAS_INSTALLED]->(p:Product) WHERE toLower(p.name) CONTAINS 'hashicorp' WITH DISTINCT c WITH count(c) as total, collect(c.sf_name)[0..5] as samples RETURN total, samples",
            "result": "Returns total count and array of sample client names"
        },
        "count_clients_by_vendor": {
            "query": "how many clients use scaleops products",
            "cypher": "MATCH (c:Client)-[rel:OPPORTUNITY|HAS_INSTALLED]->(p:Product) WHERE toLower(p.name) CONTAINS 'scaleops' RETURN count(DISTINCT c) as total",
            "result": "Returns just the count"
        },
        "processed_recordings_count": {
            "query": "how many recordings have been processed",
            "cypher": "MATCH (r:Recording) WHERE r.status = 'processed' RETURN count(r) as total",
            "result": "Returns count of successfully processed recordings"
        },
        "recent_meeting_recordings": {
            "query": "show recent terraform meeting recordings",
            "cypher": "MATCH (r:Recording)-[:LINKED_TO]->(c:CalendarEvent) WHERE toLower(c.title) CONTAINS 'terraform' RETURN r.name, r.status, c.title, c.startTime ORDER BY c.startTime DESC LIMIT 5",
            "result": "Returns recent terraform-related meeting recordings with context"
        },
        "employee_meeting_activity": {
            "query": "show john's recent meeting activity",
            "cypher": "MATCH (e:Employee)-[rel:OWNER_OF|INVITED_TO]->(c:CalendarEvent) WHERE toLower(e.name) CONTAINS 'john' RETURN e.name, c.title, c.startTime, type(rel) as role ORDER BY c.startTime DESC LIMIT 10",
            "result": "Returns employee's recent meeting participation"
        },
        "recordings_with_transcripts": {
            "query": "show processed recordings with transcripts",
            "cypher": "MATCH (r:Recording {status: 'processed'}) WHERE r.transcriptUrl <> '' AND r.transcriptUrl IS NOT NULL RETURN r.name, r.title, r.transcriptUrl ORDER BY r.createdDateTime DESC LIMIT 5",
            "result": "Returns recordings that have completed transcription"
        },
        "meeting_participants_search": {
            "query": "find meetings with smith in participants",
            "cypher": "MATCH (c:CalendarEvent) WHERE ANY(email IN c.internalParticipants WHERE email CONTAINS 'smith') RETURN c.title, c.internalParticipants, c.startTime ORDER BY c.startTime DESC LIMIT 5",
            "result": "Returns meetings where smith participated"
        }
    },
    
    "query_patterns": {
        "client_lookup": {
            "description": "Find clients by name",
            "template": "MATCH (c:Client) WHERE toLower(c.sf_name) CONTAINS toLower('{client_name}') RETURN c",
            "critical": "Always use sf_name, never name"
        },
        
        "client_products_purchased": {
            "description": "Find products client purchased",
            "template": "MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product) WHERE toLower(c.sf_name) CONTAINS toLower('{client_name}') AND o.opportunity_stage = 'Closed Won' RETURN c.sf_name, p.name, o.total_price",
            "filters": ["opportunity_stage = 'Closed Won'", "opportunity_stage = 'Closed Lost'"]
        },
        
        "client_products_installed": {
            "description": "Find products client has installed", 
            "template": "MATCH (c:Client)-[i:HAS_INSTALLED]->(p:Product) WHERE toLower(c.sf_name) CONTAINS toLower('{client_name}') AND i.status = 'Installed' RETURN c.sf_name, p.name, i.install_date"
        },
        
        "client_account_manager": {
            "description": "Find client's account manager",
            "template": "MATCH (c:Client)-[:MANAGED_BY]->(e:Employee) WHERE toLower(c.sf_name) CONTAINS toLower('{client_name}') RETURN c.sf_name, e.name, e.email"
        },
        
        "employee_clients": {
            "description": "Find employee's managed clients",
            "template": "MATCH (e:Employee)-[:MANAGED_BY]-(c:Client) WHERE toLower(e.name) CONTAINS toLower('{employee_name}') RETURN e.name, collect(c.sf_name) as clients"
        },
        
        "product_vendor": {
            "description": "Find product's vendor",
            "template": "MATCH (v:Vendor)-[:MAKES]->(p:Product) WHERE toLower(p.name) CONTAINS toLower('{product_name}') RETURN p.name, v.name"
        },
        
        "strategic_products": {
            "description": "Find strategic vendor products",
            "template": "MATCH (p:Product) WHERE p.sf_strategic_vendor = true RETURN p.name, p.sf_vendor ORDER BY p.name"
        },
        
        "clients_by_region": {
            "description": "Find clients in specific region",
            "template": "MATCH (c:Client) WHERE c.region = '{region_code}' RETURN c.sf_name, c.sf_billing_country",
            "note": "Use direct region property, not LOCATED_IN relationship",
            "israel_example": "For Israel/Israeli clients: c.region = 'IL' (NOT c.country = 'Israel')"
        },
        
        "israeli_clients_with_managers": {
            "description": "Find Israeli clients with their account managers",
            "template": "MATCH (c:Client)-[:MANAGED_BY]->(e:Employee) WHERE c.region = 'IL' RETURN c.sf_name as client, e.name as account_manager LIMIT 5",
            "note": "Use c.region = 'IL' for Israel, Employee not AccountManager"
        },
        
        "active_clients_by_region": {
            "description": "Find active clients in specific region",
            "template": "MATCH (c:Client) WHERE c.region = '{region_code}' AND c.sf_account_status IS NOT NULL RETURN c.sf_name, c.sf_account_status",
            "note": "No simple 'active' field - check sf_account_status"
        },
        
        "clients_with_vendor_products": {
            "description": "Find clients using products from specific vendor",
            "template": "MATCH (c:Client)-[rel:OPPORTUNITY|HAS_INSTALLED]->(p:Product) WHERE toLower(p.vendor) CONTAINS toLower('{vendor_name}') OR toLower(p.name) CONTAINS toLower('{vendor_name}') RETURN DISTINCT c.sf_name",
            "count_template": "MATCH (c:Client)-[rel:OPPORTUNITY|HAS_INSTALLED]->(p:Product) WHERE toLower(p.vendor) CONTAINS toLower('{vendor_name}') OR toLower(p.name) CONTAINS toLower('{vendor_name}') RETURN count(DISTINCT c) as total",
            "count_and_sample_template": "MATCH (c:Client)-[rel:OPPORTUNITY|HAS_INSTALLED]->(p:Product) WHERE toLower(p.vendor) CONTAINS toLower('{vendor_name}') OR toLower(p.name) CONTAINS toLower('{vendor_name}') WITH DISTINCT c WITH count(c) as total, collect(c.sf_name)[0..5] as sample_names RETURN total, sample_names",
            "vendor_year_deals_template": "MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product) WHERE o.opportunity_stage = 'Closed Won' AND (toLower(p.vendor) CONTAINS '{vendor}' OR toLower(p.name) CONTAINS '{vendor}') AND o.close_date >= '{year}-01-01' AND o.close_date < '{year+1}-01-01' WITH count(o) as total, collect({client: c.sf_name, product: p.name, date: o.close_date})[0..5] as samples RETURN total, samples",
            "example_complete_query": "MATCH (c:Client)-[rel:OPPORTUNITY|HAS_INSTALLED]->(p:Product) WHERE toLower(p.name) CONTAINS 'scaleops' WITH DISTINCT c WITH count(c) as total, collect(c.sf_name)[0..5] as samples RETURN total, samples"
        },
        
        "recordings_by_status": {
            "description": "Find recordings by processing status",
            "template": "MATCH (r:Recording) WHERE r.status = '{status}' RETURN r.name, r.title, r.createdDateTime ORDER BY r.createdDateTime DESC",
            "statuses": ["new", "processing", "processed", "failed"]
        },
        
        "recordings_with_meetings": {
            "description": "Find recordings with their meeting context",
            "template": "MATCH (r:Recording)-[:LINKED_TO]->(c:CalendarEvent) WHERE toLower(r.title) CONTAINS toLower('{search_term}') RETURN r.name, r.status, c.title, c.startTime, c.endTime"
        },
        
        "employee_meetings_organized": {
            "description": "Find meetings organized by employee",
            "template": "MATCH (e:Employee)-[:OWNER_OF]->(c:CalendarEvent) WHERE toLower(e.name) CONTAINS toLower('{employee_name}') RETURN e.name, c.title, c.startTime ORDER BY c.startTime DESC"
        },
        
        "employee_meetings_attended": {
            "description": "Find meetings attended by employee",
            "template": "MATCH (e:Employee)-[:INVITED_TO]->(c:CalendarEvent) WHERE toLower(e.name) CONTAINS toLower('{employee_name}') RETURN e.name, c.title, c.startTime ORDER BY c.startTime DESC"
        },
        
        "recordings_by_date_range": {
            "description": "Find recordings in date range",
            "template": "MATCH (r:Recording) WHERE r.createdDateTime >= '{start_date}' AND r.createdDateTime <= '{end_date}' RETURN r.name, r.title, r.status, r.createdDateTime ORDER BY r.createdDateTime DESC"
        },
        
        "failed_recordings": {
            "description": "Find failed recordings with error details",
            "template": "MATCH (r:Recording) WHERE r.status = 'failed' RETURN r.name, r.title, r.errorMessage, r.processingFailed ORDER BY r.processingFailed DESC"
        },
        
        "meeting_recordings_with_participants": {
            "description": "Find meeting recordings with organizer and participants",
            "template": "MATCH (r:Recording)-[:LINKED_TO]->(c:CalendarEvent) OPTIONAL MATCH (owner:Employee)-[:OWNER_OF]->(c) OPTIONAL MATCH (participant:Employee)-[:INVITED_TO]->(c) WHERE toLower(c.title) CONTAINS toLower('{meeting_topic}') RETURN r.name, r.status, c.title, owner.name as organizer, collect(DISTINCT participant.name) as participants"
        },
        
        "external_meetings_recorded_by_year": {
            "description": "Count external meetings recorded in specific year",
            "template": "MATCH (r:Recording)-[:LINKED_TO]->(c:CalendarEvent) WHERE r.createdDateTime >= '{year}-01-01T00:00:00Z' AND r.createdDateTime < '{year+1}-01-01T00:00:00Z' AND size(c.externalParticipants) > 0 RETURN count(r) as external_meetings_recorded",
            "note": "External meetings have externalParticipants array size > 0"
        },
        
        "employee_meeting_breakdown_by_year": {
            "description": "Employee's owned meetings breakdown (internal/external) for specific year",
            "template": "MATCH (e:Employee)-[:OWNER_OF]->(c:CalendarEvent)<-[:LINKED_TO]-(r:Recording) WHERE toLower(e.name) CONTAINS toLower('{employee_name}') AND r.createdDateTime >= '{year}-01-01T00:00:00Z' AND r.createdDateTime < '{year+1}-01-01T00:00:00Z' WITH c, r RETURN count(r) as total_recorded_meetings, sum(CASE WHEN size(c.externalParticipants) = 0 THEN 1 ELSE 0 END) as internal_meetings, sum(CASE WHEN size(c.externalParticipants) > 0 THEN 1 ELSE 0 END) as external_meetings"
        },
        
        "most_active_employee_by_period": {
            "description": "Find most active employee by meeting participation in time period",
            "template": "MATCH (e:Employee)-[rel:OWNER_OF|INVITED_TO]->(c:CalendarEvent) WHERE c.startTime >= '{start_date}' AND c.startTime < '{end_date}' WITH e, count(DISTINCT c) as total_meetings, sum(CASE WHEN type(rel) = 'OWNER_OF' THEN 1 ELSE 0 END) as owned_meetings, sum(CASE WHEN type(rel) = 'INVITED_TO' THEN 1 ELSE 0 END) as participated_meetings RETURN e.name, total_meetings, owned_meetings, participated_meetings ORDER BY total_meetings DESC LIMIT 1",
            "yearly": "start_date: '2025-01-01T00:00:00Z', end_date: '2026-01-01T00:00:00Z'",
            "monthly": "start_date: '2025-07-01T00:00:00Z', end_date: '2025-08-01T00:00:00Z'"
        },
        
        "top_clients_by_recorded_meetings": {
            "description": "Top clients with most recorded meetings via employee relationships",
            "template": "MATCH (c:Client)-[:MANAGED_BY]->(e:Employee)-[:OWNER_OF|INVITED_TO]->(ce:CalendarEvent)<-[:LINKED_TO]-(r:Recording) WHERE r.createdDateTime >= '{year}-01-01T00:00:00Z' AND r.createdDateTime < '{year+1}-01-01T00:00:00Z' WITH c, count(DISTINCT r) as recorded_meetings, collect(DISTINCT ce.title)[0..5] as sample_subjects RETURN c.sf_name as client_name, recorded_meetings, sample_subjects ORDER BY recorded_meetings DESC LIMIT 3",
            "note": "Links clients via account manager (MANAGED_BY) participation in meetings"
        }
    },
    
    "critical_notes": {
        "client_names": "ALWAYS use Client.sf_name for name searches, NEVER use Client.name (often empty)",
        "opportunity_stages": "Use exact values: 'Closed Won', 'Closed Lost', 'Qualification'",
        "regions": "Only 3 valid regions: IL, US, UK",
        "case_sensitivity": "Always use toLower() and CONTAINS for text matching",
        "boolean_values": "Use true/false (not 'true'/'false' strings)",
        "date_format": "Dates are ISO strings, use string comparison or datetime() conversion",
        "client_location": "Clients have direct 'region' property (c.region = 'IL'), NO LOCATED_IN relationships",
        "client_active_status": "No simple 'active' field - use c.sf_account_status for status checks",
        "vendor_searches": "Search both p.vendor and p.name fields for vendor names like 'HashiCorp'",
        "multiple_relationships": "Use [rel:OPPORTUNITY|HAS_INSTALLED] for clients who bought OR installed products",
        "query_completion": "Always complete RETURN statements - never end with trailing commas",
        "no_apoc_functions": "NEVER use APOC functions like apoc.coll.randomItems - use standard Cypher only",
        "sampling_method": "For random sampling, use clients[0..5] or clients[..5] for first 5 items",
        "complete_return_example": "RETURN total, samples (NEVER end with comma like 'RETURN total,')",
        "syntax_rule": "Every RETURN statement must be complete - no trailing commas allowed",
        "mandatory_complete_return": "ALWAYS end queries with complete RETURN like 'RETURN total, samples' NEVER 'RETURN total,'",
        "cypher_validation": "Before generating, ensure RETURN statement has all required fields after commas",
        "date_fields": "Use o.close_date for OPPORTUNITY temporal queries (actual close date), NOT o.purchased_date (line item creation)",
        "cost_fields": "Use o.total_price for deal costs, NOT o.amount (amount field does not exist)",
        "cost_aggregation": "For total cost use: sum(toFloat(o.total_price)) as total_cost",
        "temporal_filtering": "For year filtering use: o.close_date >= '2025-01-01' AND o.close_date < '2026-01-01'",
        "mandatory_filters": "ALWAYS include ALL user-specified filters - vendor AND year AND status",
        "filter_combination": "When user asks for 'hashicorp 2025 deals' include BOTH vendor filter AND year filter",
        "variable_consistency": "Use consistent variable names - if you collect as 'samples' return as 'samples', not 'deals'",
        "collection_syntax": "collect({...})[0..5] as samples RETURN total, samples (NOT deals[..5])",
        "israel_queries": "For Israeli/Israel clients ALWAYS use c.region = 'IL' NEVER c.country = 'Israel'",
        "account_manager_queries": "For account managers use Employee node, NEVER AccountManager node",
        "recording_status": "Recording status values: new, processing, processed, failed",
        "meeting_recordings": "Use Recording-[:LINKED_TO]->CalendarEvent for meeting context",
        "meeting_participants": "Use Employee-[:OWNER_OF|INVITED_TO]->CalendarEvent for meeting roles",
        "recording_search": "Search recordings by title, status, or linked meeting subject",
        "meeting_timeline": "Use CalendarEvent.startTime/endTime for temporal meeting queries",
        "transcript_access": "Check r.transcriptUrl <> '' AND r.transcriptUrl IS NOT NULL for available transcripts",
        "participant_arrays": "Use ANY(email IN c.internalParticipants WHERE condition) for participant searches",
        "recording_linking": "85-95% of recordings linked to calendar events via LINKED_TO relationship",
        "processing_status": "Most recordings are 'processed', check status before accessing transcriptUrl/analysisUrl",
        "property_names": "Use 'size' not 'sizeInBytes', 'title' not 'subject', 'owner' not 'organizer'",
        "date_filtering": "Recording dates: 2024-08-22 to 2025-11-16, use r.createdDateTime for recording dates",
        "external_meetings": "300 meetings have external participants (avg 3.6 external per meeting)",
        "meeting_analytics": "Use CalendarEvent.startTime for meeting dates, Recording.createdDateTime for recording dates",
        "client_meeting_linking": "Link clients to meetings via MANAGED_BY employee relationships",
        "activity_ranking": "Combine OWNER_OF and INVITED_TO for total employee meeting activity"
    }
}