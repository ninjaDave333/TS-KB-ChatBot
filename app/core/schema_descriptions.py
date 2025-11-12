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
            "note": "Use direct region property, not LOCATED_IN relationship"
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
        "collection_syntax": "collect({...})[0..5] as samples RETURN total, samples (NOT deals[..5])"
    }
}