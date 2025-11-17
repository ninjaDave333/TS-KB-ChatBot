import boto3
import json
import re
import os
from typing import Dict, Any
from .schema_descriptions import SCHEMA_DESCRIPTIONS

class BedrockClient:
    def __init__(self):
        try:
            self.client = boto3.client('bedrock-runtime', region_name='us-east-1')
            self.model_id = os.getenv('AWS_BEDROCK_MODEL_ID', 'us.anthropic.claude-3-5-haiku-20241022-v1:0')
            print(f"Bedrock client initialized with model: {self.model_id}")
        except Exception as e:
            print(f"Bedrock client initialization failed: {e}")
            self.client = None
            self.model_id = None
    
    def generate_cypher(self, user_query: str, schema: Dict[str, Any]) -> str:
        """Use Claude to generate Cypher queries"""
        
        if not self.client:
            raise Exception("Bedrock client not initialized")
        
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
        
        filters = []
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
        
        prompt = f"""Generate Cypher for: {user_query}

CRITICAL RULES:
- Client names: c.sf_name (NOT c.name)
- Israeli clients: c.region = 'IL' (NOT c.country = 'Israel')
- Account managers: Employee node (NOT AccountManager)
- Dates: o.close_date for temporal queries (actual deal close date)
- Extract year: substring(o.close_date, 0, 4) NOT YEAR() or extract()
- Vendor filtering: Use p.vendor field directly
- Exclude vendor: WHERE NOT toLower(p.vendor) CONTAINS 'vendorname'
- Successful deals: o.opportunity_stage = 'Closed Won'{filter_hint}

EXAMPLE:
MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product) WHERE o.opportunity_stage = 'Closed Won' AND NOT toLower(p.vendor) CONTAINS 'terasky' WITH o.close_date as date, c.sf_name as client, p.name as product ORDER BY date ASC LIMIT 1 RETURN substring(date, 0, 4) as year, client, product

Cypher:"""

        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,  # Maximum allowed by Claude
                "system": "You are a precise Cypher query generator. Generate ONLY valid Cypher syntax. Do NOT add explanations. MUST include ALL filters from user query. For 'non-X vendor' use: WHERE NOT toLower(p.vendor) CONTAINS 'x'. Return ALL requested fields.",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            result = json.loads(response['body'].read())
            cypher_query = result['content'][0]['text'].strip()
            
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
            
            # Post-process: inject missing filters
            if filters:
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