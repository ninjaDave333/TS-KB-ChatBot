import re
from typing import Dict, List, Any

class QueryGenerator:
    def __init__(self):
        self.node_types = ["Employee", "Client", "Product", "Vendor", "Region", "Skill", "BU"]
        
    def extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Basic entity extraction using patterns"""
        entities = {"nodes": [], "numbers": [], "temporal": []}
        
        # Extract node types
        for node_type in self.node_types:
            if node_type.lower() in query.lower():
                entities["nodes"].append(node_type)
        
        # Extract numbers
        numbers = re.findall(r'\b\d+\b', query)
        entities["numbers"] = numbers
        
        # Extract years
        years = re.findall(r'\b(20\d{2})\b', query)
        entities["temporal"] = years
        
        return entities
    
    def generate_cypher(self, query: str) -> str:
        """Generate basic Cypher queries - now handles raw Cypher input"""
        query_stripped = query.strip()
        
        # If it looks like raw Cypher, return as-is
        if query_stripped.upper().startswith(('MATCH', 'RETURN', 'WITH', 'CREATE', 'MERGE')):
            return query_stripped
        
        query_lower = query.lower()
        entities = self.extract_entities(query)
        
        # Count queries
        if "how many" in query_lower:
            if "client" in query_lower:
                return "MATCH (c:Client) RETURN count(c) as total"
            elif "employee" in query_lower:
                return "MATCH (e:Employee) RETURN count(e) as total"
            elif "product" in query_lower:
                return "MATCH (p:Product) RETURN count(p) as total"
        
        # List queries
        if "list" in query_lower or "show" in query_lower:
            if "client" in query_lower:
                return "MATCH (c:Client) RETURN c.name as name LIMIT 10"
            elif "employee" in query_lower:
                return "MATCH (e:Employee) RETURN e.name as name LIMIT 10"
            elif "product" in query_lower:
                return "MATCH (p:Product) RETURN p.name as name LIMIT 10"
        
        # Default fallback
        return "MATCH (n) RETURN count(n) as total_nodes"