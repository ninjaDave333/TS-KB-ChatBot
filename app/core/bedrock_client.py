import re
from typing import Dict, Any
from .schema_descriptions import SCHEMA_DESCRIPTIONS
from .llm_client import LLMClient

class BedrockClient:
    def __init__(self, llm_client: LLMClient = None):
        """Initialize with LLMClient for actual model calls."""
        self.llm_client = llm_client or LLMClient()
        print(f"BedrockClient initialized with LLMClient")
    
    async def generate_cypher(self, user_query: str, schema: Dict[str, Any]) -> str:
        """Build prompt and use LLMClient to generate Cypher queries"""
        
        if not self.llm_client:
            raise Exception("LLMClient not initialized")
        
        # Build enhanced prompt with schema descriptions
        nodes_desc = "\n".join([f"- {name}: {info['purpose']} (key: {info['name_field']})" 
                                for name, info in SCHEMA_DESCRIPTIONS['nodes'].items()])
        
        relationships_desc = "\n".join([f"- {name}: {info['purpose']} - {info['pattern']}" 
                                       for name, info in SCHEMA_DESCRIPTIONS['relationships'].items()])
        
        critical_notes = "\n".join([f"- {note}" for note in SCHEMA_DESCRIPTIONS['critical_notes'].values()])
        
        # Extract filters from query
        import re
        year_match = re.search(r'\b(20\d{2})\b', user_query)
        vendor_match = re.search(r'\b(hashicorp|aws|microsoft|google|vmware)\b', user_query, re.IGNORECASE)
        israel_match = re.search(r'\b(israel|israeli)\b', user_query, re.IGNORECASE)
        
        # Check if this is a Teams Recording query
        is_teams_query = any(term in user_query.lower() for term in ['meeting', 'recording', 'external', 'active employee', 'breakdown'])
        
        filters = []
        # Only add filters for non-Teams Recording queries
        if not is_teams_query:
            if year_match:
                year = year_match.group(1)
                filters.append(f"o.close_date >= '{year}-01-01' AND o.close_date < '{int(year)+1}-01-01'")
            if vendor_match:
                vendor = vendor_match.group(1).lower()
                filters.append(f"toLower(p.name) CONTAINS '{vendor}'")
            if israel_match:
                filters.append("c.region = 'IL'")
        
        filter_hint = f"\n\nREQUIRED FILTERS: {' AND '.join(filters)}" if filters else ""
        
        print(f"Extracted filters: {filters}")  # Debug
        print(f"Filter hint: {filter_hint}")  # Debug
        
        # Teams Recording context and date handling
        teams_context = ""
        date_context = ""
        
        if is_teams_query:
            teams_context = f"""

TEAMS RECORDING DATA (Available 2024-08-22 to 2025-12-10):
- Recording nodes: 490 recordings with status, transcriptUrl, createdDateTime
- CalendarEvent nodes: 470 events with title, startTime, endTime, internalParticipants, externalParticipants
- Relationships: Recording-[:LINKED_TO]->CalendarEvent, Employee-[:OWNER_OF|INVITED_TO]->CalendarEvent
- External meetings: size(c.externalParticipants) > 0
- Date fields: r.createdDateTime for recordings, c.startTime for meetings
- Employee activity: Combine OWNER_OF + INVITED_TO for total participation
- Client meetings: Link via Client-[:MANAGED_BY]->Employee-[:OWNER_OF|INVITED_TO]->CalendarEvent

COMMON PATTERNS:
- External meeting count: MATCH (r:Recording)-[:LINKED_TO]->(c:CalendarEvent) WHERE size(c.externalParticipants) > 0 RETURN count(r) as external_meetings_recorded
- Most active employee: MATCH (e:Employee)-[rel:OWNER_OF|INVITED_TO]->(c:CalendarEvent) RETURN e.name as employee, count(rel) as meeting_count ORDER BY meeting_count DESC LIMIT 1
- Meeting breakdown: MATCH (e:Employee {{name: 'David Gidony'}})-[rel:OWNER_OF|INVITED_TO]->(c:CalendarEvent) WITH c, CASE WHEN size(c.externalParticipants) > 0 THEN 'External' ELSE 'Internal' END as meeting_type RETURN meeting_type, count(c) as meeting_count
- Top clients by meetings: MATCH (client:Client)-[:MANAGED_BY]->(e:Employee)-[rel:OWNER_OF|INVITED_TO]->(c:CalendarEvent) RETURN client.sf_name as client, count(c) as meeting_count ORDER BY meeting_count DESC LIMIT 3
"""
            
            # Add date context for Teams Recording queries
            if year_match:
                year = year_match.group(1)
                if year == '2024':
                    date_context = f"\nDATE FILTER: c.startTime >= '2024-08-22' AND c.startTime < '2025-01-01'"
                elif year == '2025':
                    date_context = f"\nDATE FILTER: c.startTime >= '2025-01-01' AND c.startTime <= '2025-12-10'"
            else:
                # If no year specified, use full available range
                date_context = f"\nDATE RANGE AVAILABLE: 2024-08-22 to 2025-12-10"
        
        prompt = f"""Generate Cypher for: {user_query}

CRITICAL RULES:
- Client names: c.sf_name (NOT c.name)
- Israeli clients: c.region = 'IL' (NOT c.country = 'Israel')
- Account managers: Employee node (NOT AccountManager)
- Dates: o.close_date for temporal queries (actual deal close date)
- Extract year: substring(o.close_date, 0, 4) NOT YEAR() or extract()
- Vendor filtering: Use p.vendor field directly
- Exclude vendor: WHERE NOT toLower(p.vendor) CONTAINS 'vendorname'
- Successful deals: o.opportunity_stage = 'Closed Won'{teams_context}{date_context}{filter_hint}

EXAMPLE:
MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product) WHERE o.opportunity_stage = 'Closed Won' AND NOT toLower(p.vendor) CONTAINS 'terasky' WITH o.close_date as date, c.sf_name as client, p.name as product ORDER BY date ASC LIMIT 1 RETURN substring(date, 0, 4) as year, client, product

Cypher:"""

        try:
            system_prompt = "You are a precise Cypher query generator. Generate ONLY valid Cypher syntax. Do NOT add explanations. MUST include ALL filters from user query. For 'non-X vendor' use: WHERE NOT toLower(p.vendor) CONTAINS 'x'. Return ALL requested fields. For Teams Recording queries: Use exact patterns provided. External meetings: size(c.externalParticipants) > 0. Employee activity: combine OWNER_OF + INVITED_TO relationships. Date filtering: use c.startTime for meetings, r.createdDateTime for recordings."
            
            # Use LLMClient for actual model call
            cypher_query = await self.llm_client.complete(system_prompt, prompt, max_tokens=4096)
            
            # Extract only the Cypher query - keep all lines, just clean up
            lines = cypher_query.split('\n')
            cypher_lines = []
            in_query = False
            
            for line in lines:
                line = line.strip()
                # Start collecting when we see MATCH
                if line.startswith('MATCH'):
                    in_query = True
                
                # Collect all lines once we're in the query
                if in_query and line:
                    # Skip lines that are just comments or explanations
                    if not line.startswith('#') and not line.startswith('//'):
                        cypher_lines.append(line)
            
            if cypher_lines:
                cypher_query = ' '.join(cypher_lines)  # Join with space to avoid syntax errors
                # Clean up multiple spaces
                cypher_query = re.sub(r'\s+', ' ', cypher_query)
                # Remove markdown code fences
                cypher_query = cypher_query.replace('```', '').strip()
            
            print(f"Bedrock cleaned: {cypher_query}")
            
            # Post-process: inject missing filters (skip for Teams Recording queries)
            if filters and not is_teams_query:
                # Check if filters are missing
                missing_filters = [f for f in filters if f not in cypher_query]
                
                if missing_filters:
                    print(f"Injecting missing filters: {missing_filters}")
                    # Find WHERE clause and add filters
                    if 'WHERE' in cypher_query:
                        # Add to existing WHERE
                        cypher_query = cypher_query.replace(
                            'WHERE ',
                            f"WHERE {' AND '.join(missing_filters)} AND "
                        )
                    else:
                        # Add new WHERE clause after first line
                        lines = cypher_query.split('\n')
                        lines.insert(1, f"WHERE {' AND '.join(missing_filters)}")
                        cypher_query = '\n'.join(lines)
                    
                    print(f"Fixed query: {cypher_query}")
            
            return cypher_query
            
        except Exception as e:
            print(f"Bedrock API error: {e}")
            raise e