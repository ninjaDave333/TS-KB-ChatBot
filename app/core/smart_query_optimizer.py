"""
Smart Query Optimizer - Apply production insights to improve queries
"""

import re
from typing import Dict, List, Any, Optional

class SmartQueryOptimizer:
    """Optimize queries based on production learning insights"""
    
    def __init__(self):
        self.optimization_rules = {
            'auto_unknown_filter': self._add_unknown_filter,
            'israeli_client_optimization': self._optimize_israeli_clients,
            'teams_recording_optimization': self._optimize_teams_queries
        }
    
    def optimize_query(self, query: str, cypher: str) -> Dict[str, Any]:
        """Apply optimizations based on query patterns"""
        
        optimized_cypher = cypher
        optimizations_applied = []
        
        query_lower = query.lower()
        
        # Apply optimization rules
        for rule_name, rule_func in self.optimization_rules.items():
            result = rule_func(query_lower, optimized_cypher)
            if result['applied']:
                optimized_cypher = result['cypher']
                optimizations_applied.append(rule_name)
        
        return {
            'original_cypher': cypher,
            'optimized_cypher': optimized_cypher,
            'optimizations_applied': optimizations_applied,
            'improvement_reason': self._get_improvement_reason(optimizations_applied)
        }
    
    def _add_unknown_filter(self, query: str, cypher: str) -> Dict[str, Any]:
        """Auto-add Unknown manager filtering"""
        
        if ('manager' in query or 'managed' in query) and 'MANAGED_BY' in cypher:
            if 'unknown' not in cypher.lower() and 'IS NOT NULL' not in cypher:
                # Add Unknown filter
                if 'WHERE' in cypher:
                    # Add to existing WHERE clause
                    cypher = cypher.replace(
                        'WHERE', 
                        'WHERE e.name IS NOT NULL AND toLower(e.name) <> "unknown" AND'
                    )
                else:
                    # Add WHERE clause before RETURN
                    cypher = cypher.replace(
                        'RETURN',
                        'WHERE e.name IS NOT NULL AND toLower(e.name) <> "unknown" RETURN'
                    )
                
                return {'applied': True, 'cypher': cypher}
        
        return {'applied': False, 'cypher': cypher}
    
    def _optimize_israeli_clients(self, query: str, cypher: str) -> Dict[str, Any]:
        """Optimize Israeli client queries"""
        
        if ('israeli' in query or 'israel' in query) and 'Client' in cypher:
            # Only add region filter if not already present
            if "c.region = 'IL'" not in cypher and "c.region = \"IL\"" not in cypher and "c.country" not in cypher:
                if 'WHERE' in cypher:
                    cypher = cypher.replace('WHERE', "WHERE c.region = 'IL' AND")
                else:
                    cypher = cypher.replace('RETURN', "WHERE c.region = 'IL' RETURN")
                
                return {'applied': True, 'cypher': cypher}
        
        return {'applied': False, 'cypher': cypher}
    
    def _optimize_teams_queries(self, query: str, cypher: str) -> Dict[str, Any]:
        """Optimize Teams Recording queries"""
        
        # External meetings optimization
        if 'external' in query and 'meeting' in query:
            if 'externalParticipants' not in cypher:
                cypher = 'MATCH (r:Recording)-[:LINKED_TO]->(c:CalendarEvent) WHERE size(c.externalParticipants) > 0 RETURN count(r) as external_meetings_recorded'
                return {'applied': True, 'cypher': cypher}
        
        # Internal meetings optimization
        if 'internal' in query and 'meeting' in query:
            if 'externalParticipants' not in cypher:
                cypher = 'MATCH (r:Recording)-[:LINKED_TO]->(c:CalendarEvent) WHERE size(c.externalParticipants) = 0 RETURN count(r) as internal_meetings_recorded'
                return {'applied': True, 'cypher': cypher}
        
        # Total meetings optimization
        if 'total' in query and 'meeting' in query and 'recording' in query:
            if 'Recording' not in cypher:
                cypher = 'MATCH (r:Recording) RETURN count(r) as total_recorded_meetings'
                return {'applied': True, 'cypher': cypher}
        
        return {'applied': False, 'cypher': cypher}
    
    def _get_improvement_reason(self, optimizations: List[str]) -> str:
        """Generate human-readable improvement reason"""
        
        reasons = {
            'auto_unknown_filter': 'Added automatic Unknown manager filtering based on production patterns',
            'israeli_client_optimization': 'Applied Israeli client region filtering optimization',
            'teams_recording_optimization': 'Used optimized Teams Recording query template'
        }
        
        if not optimizations:
            return 'No optimizations applied'
        
        return '; '.join([reasons.get(opt, opt) for opt in optimizations])
    
    def suggest_query_improvements(self, query: str) -> List[str]:
        """Suggest improvements based on production patterns"""
        
        suggestions = []
        query_lower = query.lower()
        
        # Manager query suggestions
        if 'manager' in query_lower and 'unknown' not in query_lower:
            suggestions.append("Consider adding 'that is not Unknown' to filter out Unknown managers")
        
        # Israeli client suggestions
        if ('israeli' in query_lower or 'israel' in query_lower) and 'manager' in query_lower:
            suggestions.append("Israeli client queries often need Unknown manager filtering")
        
        # Teams Recording suggestions
        if 'meeting' in query_lower:
            if 'external' not in query_lower and 'internal' not in query_lower:
                suggestions.append("Consider specifying 'external' or 'internal' meetings for more precise results")
        
        return suggestions