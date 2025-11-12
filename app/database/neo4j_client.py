import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

class Neo4jClient:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.username = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.driver = None
        
        if not self.uri or not self.username or not self.password:
            raise ValueError(f"Missing Neo4j credentials: URI={self.uri}, USERNAME={self.username}, PASSWORD={'***' if self.password else None}")
        
    def connect(self):
        if not self.driver:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.username, self.password)
            )
        return self.driver
    
    def execute_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict]:
        with self.connect().session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
    
    def get_schema(self) -> Dict[str, Any]:
        """Get basic schema information"""
        nodes_query = "CALL db.labels() YIELD label RETURN collect(label) as node_types"
        rels_query = "CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) as relationship_types"
        
        nodes = self.execute_query(nodes_query)[0]["node_types"]
        rels = self.execute_query(rels_query)[0]["relationship_types"]
        
        return {"node_types": nodes, "relationship_types": rels}
    
    def close(self):
        if self.driver:
            self.driver.close()