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
        
        # Handle Teams Recording queries first
        query_type = self._detect_query_type(user_query)
        if query_type in ['external_meeting_analytics', 'employee_activity_ranking', 'meeting_breakdown', 'client_meeting_ranking']:
            return self._generate_meeting_analytics_answer(user_query, data, query_type)
        
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
    
    def _detect_query_type(self, query: str) -> str:
        """Detect the type of query for performance monitoring"""
        query_lower = query.lower()
        
        # Teams Recording query types
        if any(term in query_lower for term in ['external meeting', 'external participant', 'external recorded']):
            return "external_meeting_analytics"
        elif any(term in query_lower for term in ['most active', 'meeting wise', 'activity']) and 'employee' in query_lower:
            return "employee_activity_ranking"
        elif 'breakdown' in query_lower and any(term in query_lower for term in ['internal', 'external']):
            return "meeting_breakdown"
        elif 'top' in query_lower and 'client' in query_lower and 'meeting' in query_lower:
            return "client_meeting_ranking"
        
        # Original query types
        elif any(keyword in query_lower for keyword in ["how many", "count", "number of"]):
            return "count"
        elif any(keyword in query_lower for keyword in ["list", "show", "display"]):
            return "list"
        elif any(keyword in query_lower for keyword in ["hashicorp", "microsoft", "aws", "vendor"]):
            return "vendor"
        else:
            return "general"
    
    def _generate_meeting_analytics_answer(self, user_query: str, data: List[Dict], query_type: str) -> str:
        """Generate answers for Teams Recording analytics queries"""
        if not data:
            return "No meeting data found for your query."
        
        query_lower = user_query.lower()
        
        if query_type == "external_meeting_analytics":
            # Handle external meeting count queries
            if len(data) == 1 and 'external_meetings_recorded' in data[0]:
                count = data[0]['external_meetings_recorded']
                return f"There were {count} external meetings recorded during the specified period."
            else:
                return f"Found {len(data)} external meeting records."
        
        elif query_type == "employee_activity_ranking":
            # Handle most active employee queries
            if data:
                employee_data = data[0]
                employee_name = employee_data.get('employee', employee_data.get('e.name', employee_data.get('name', 'Unknown')))
                meeting_count = employee_data.get('meeting_count', employee_data.get('total_meetings', 0))
                
                if 'david gidony' in query_lower:
                    # Special handling for David Gidony breakdown
                    if len(data) >= 2:
                        breakdown_info = []
                        for record in data:
                            meeting_type = record.get('meeting_type', 'Unknown')
                            count = record.get('meeting_count', 0)
                            breakdown_info.append(f"{meeting_type}: {count}")
                        return f"David Gidony's meeting breakdown - {', '.join(breakdown_info)}"
                
                return f"The most active employee is {employee_name} with {meeting_count} meetings."
        
        elif query_type == "meeting_breakdown":
            # Handle internal/external breakdown
            if len(data) >= 2:
                breakdown_info = []
                for record in data:
                    meeting_type = record.get('meeting_type', 'Unknown')
                    count = record.get('meeting_count', 0)
                    breakdown_info.append(f"{meeting_type}: {count}")
                return f"Meeting breakdown - {', '.join(breakdown_info)}"
        
        elif query_type == "client_meeting_ranking":
            # Handle top clients by meeting count
            if data:
                client_info = []
                for i, record in enumerate(data[:3], 1):
                    client = record.get('client', record.get('sf_name', 'Unknown'))
                    # Try multiple possible field names for count
                    count = record.get('recorded_meetings', record.get('meeting_count', 0))
                    client_info.append(f"{i}. {client}: {count} meetings")
                return f"Top clients by meeting count:\n{chr(10).join(client_info)}"
        
        # Fallback to default formatting
        return self._generate_default_answer(user_query, data)