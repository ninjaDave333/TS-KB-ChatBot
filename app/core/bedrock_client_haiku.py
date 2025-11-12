import boto3
import json
from typing import Dict, Any

class BedrockClient:
    def __init__(self):
        try:
            self.client = boto3.client('bedrock-runtime', region_name='us-east-1')
            # Use Claude 3 Haiku - more widely available
            self.model_id = "anthropic.claude-3-haiku-20240307-v1:0"
            print("Bedrock client initialized with Claude 3 Haiku")
        except Exception as e:
            print(f"Bedrock client initialization failed: {e}")
            self.client = None
    
    def generate_cypher(self, user_query: str, schema: Dict[str, Any]) -> str:
        """Use Claude to generate Cypher queries"""
        
        if not self.client:
            raise Exception("Bedrock client not initialized")
        
        prompt = f"""You are a Neo4j Cypher query generator. Given a natural language query and database schema, generate a precise Cypher query.

Schema:
Node types: {', '.join(schema['node_types'])}
Relationship types: {', '.join(schema['relationship_types'])}

Key patterns:
- Client nodes: Use for customers/accounts
- Employee nodes: Use for staff/people
- Product nodes: Use for products/services
- MANAGED_BY: Client-Employee relationships
- OPPORTUNITY: Client-Product purchase relationships
- HAS_INSTALLED: Client-Product installation relationships

User Query: {user_query}

Generate ONLY the Cypher query, no explanation:"""

        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 200,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            print(f"Calling Bedrock with query: {user_query}")
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            result = json.loads(response['body'].read())
            cypher_query = result['content'][0]['text'].strip()
            print(f"Bedrock generated: {cypher_query}")
            return cypher_query
            
        except Exception as e:
            print(f"Bedrock API error: {e}")
            raise e