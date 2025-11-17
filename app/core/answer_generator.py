"""
Answer Generator for TSKB RAG System
Generates natural language answers from Cypher query results
"""

from typing import List, Dict, Any

class AnswerGenerator:
    """Generates natural language answers from query results"""
    
    def generate_answer(self, user_query: str, cypher_query: str, data: List[Dict[str, Any]]) -> str:
        """Generate natural language answer from query results"""
        
        if not data or len(data) == 0:
            return "No results found for your query."
        
        # Extract query intent
        query_lower = user_query.lower()
        
        # Handle count queries
        if self._is_count_query(query_lower, data):
            return self._generate_count_answer(user_query, data)
        
        # Handle list queries
        if self._is_list_query(query_lower):
            return self._generate_list_answer(user_query, data)
        
        # Handle vendor-specific queries
        if self._is_vendor_query(query_lower):
            return self._generate_vendor_answer(user_query, data)
        
        # Default structured answer
        return self._generate_default_answer(user_query, data)
    
    def _is_count_query(self, query: str, data: List[Dict]) -> bool:
        """Check if this is a count/how many query"""
        count_keywords = ["how many", "count", "number of", "total"]
        has_count_keyword = any(keyword in query for keyword in count_keywords)
        
        # Only consider it a count query if it has count keywords AND numeric results
        if has_count_keyword and data and len(data) > 0:
            first_result = data[0]
            # Look for actual count fields (numeric values with count-like names)
            count_fields = [k for k in first_result.keys() if 
                          any(word in k.lower() for word in ["count", "total", "number"]) and 
                          isinstance(first_result[k], (int, float))]
            return len(count_fields) > 0
        
        return False
    
    def _is_list_query(self, query: str) -> bool:
        """Check if this is a list query"""
        list_keywords = ["list", "show", "display", "get"]
        return any(keyword in query for keyword in list_keywords)
    
    def _is_vendor_query(self, query: str) -> bool:
        """Check if this is a vendor-specific query"""
        vendor_keywords = ["hashicorp", "microsoft", "aws", "google", "oracle", "products", "vendor"]
        return any(keyword in query for keyword in vendor_keywords)
    
    def _generate_count_answer(self, user_query: str, data: List[Dict]) -> str:
        """Generate answer for count queries"""
        if not data:
            return "No results found."
        
        result = data[0]
        
        # Find the count field
        count_field = None
        count_value = 0
        
        for key, value in result.items():
            if isinstance(value, (int, float)):
                count_field = key
                count_value = value
                break
        
        if count_field is None:
            return f"Found {len(data)} results."
        
        # Generate contextual answer based on query
        query_lower = user_query.lower()
        
        if "hashicorp" in query_lower and "2025" in query_lower:
            return f"In 2025, {count_value} HashiCorp products were purchased by clients."
        elif "deals" in query_lower and "2025" in query_lower:
            return f"There were {count_value} successful deals conducted during 2025."
        elif "clients" in query_lower:
            return f"Found {count_value} clients matching your criteria."
        else:
            return f"The query returned {count_value} results."
    
    def _generate_list_answer(self, user_query: str, data: List[Dict]) -> str:
        """Generate answer for list queries"""
        if not data:
            return "No items found to list."
        
        # Handle Israeli clients with managers specifically
        if "israel" in user_query.lower() and "manager" in user_query.lower():
            client_manager_pairs = []
            for record in data[:5]:
                client = record.get("client", record.get("sf_name", "Unknown"))
                manager = record.get("account_manager", record.get("name", "Unknown"))
                client_manager_pairs.append(f"{client} (managed by {manager})")
            
            if client_manager_pairs:
                return f"Here are 5 Israeli clients with their account managers: {', '.join(client_manager_pairs)}"
        
        # Extract names or relevant fields for other queries
        items = []
        for record in data[:5]:  # Limit to 5 items
            if "sf_name" in record:
                items.append(record["sf_name"])
            elif "name" in record:
                items.append(record["name"])
            elif "client" in record:
                items.append(record["client"])
            else:
                # Use first string field
                for value in record.values():
                    if isinstance(value, str):
                        items.append(value)
                        break
        
        if items:
            item_list = ", ".join(items)
            return f"Here are the results: {item_list}"
        else:
            return f"Found {len(data)} results but couldn't extract readable names."
    
    def _generate_vendor_answer(self, user_query: str, data: List[Dict]) -> str:
        """Generate answer for vendor-specific queries"""
        if not data:
            return "No vendor-specific results found."
        
        query_lower = user_query.lower()
        
        # Handle HashiCorp specifically
        if "hashicorp" in query_lower:
            result = data[0]
            
            # Look for count fields
            for key, value in result.items():
                if isinstance(value, (int, float)) and "hashicorp" in key.lower():
                    if "2025" in query_lower:
                        return f"In 2025, {value} HashiCorp products were purchased across various clients."
                    else:
                        return f"Found {value} HashiCorp products in the system."
        
        return self._generate_default_answer(user_query, data)
    
    def _generate_default_answer(self, user_query: str, data: List[Dict]) -> str:
        """Generate default structured answer"""
        if not data:
            return "No results found."
        
        count = len(data)
        
        # Try to extract meaningful information
        sample = data[0]
        
        # Look for key fields
        key_info = []
        for key, value in sample.items():
            if isinstance(value, (str, int, float)) and value is not None:
                key_info.append(f"{key}: {value}")
        
        if key_info:
            sample_info = ", ".join(key_info[:3])  # First 3 fields
            return f"Found {count} results. Sample: {sample_info}"
        else:
            return f"Query executed successfully, found {count} results."