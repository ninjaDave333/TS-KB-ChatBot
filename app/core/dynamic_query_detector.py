"""
Dynamic Query Detector - Automatically discovers new query types from user interactions
Part of Dynamic RAG Enhancement Phase 1
"""

import json
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re

class DynamicQueryDetector:
    """Automatically discovers new query types from user interactions"""
    
    def __init__(self, classifier):
        self.classifier = classifier
        self.recent_queries = []
        self.discovered_patterns = {}
        self.pattern_suggestions = []
    
    def add_query(self, query: str, timestamp: Optional[datetime] = None):
        """Add a query to recent queries for pattern analysis"""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.recent_queries.append({
            'query': query,
            'timestamp': timestamp,
            'tokens': self._tokenize_query(query),
            'entities': self._extract_entities(query)
        })
        
        # Keep only last 100 queries
        if len(self.recent_queries) > 100:
            self.recent_queries = self.recent_queries[-100:]
    
    def _tokenize_query(self, query: str) -> List[str]:
        """Simple tokenization of query"""
        # Remove punctuation and convert to lowercase
        clean_query = re.sub(r'[^\w\s]', ' ', query.lower())
        return clean_query.split()
    
    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract entities from query"""
        query_lower = query.lower()
        
        entities = {
            'business_entities': [],
            'actions': [],
            'temporal': [],
            'metrics': []
        }
        
        # Business entities
        business_terms = ['client', 'customer', 'employee', 'product', 'deal', 'opportunity', 
                         'meeting', 'recording', 'project', 'vendor', 'partner']
        for term in business_terms:
            if term in query_lower:
                entities['business_entities'].append(term)
        
        # Actions
        action_terms = ['count', 'list', 'show', 'find', 'get', 'search', 'analyze', 
                       'compare', 'rank', 'sort', 'filter']
        for term in action_terms:
            if term in query_lower:
                entities['actions'].append(term)
        
        # Temporal
        temporal_terms = ['2024', '2025', 'year', 'month', 'week', 'day', 'recent', 
                         'last', 'this', 'next', 'previous']
        for term in temporal_terms:
            if term in query_lower:
                entities['temporal'].append(term)
        
        # Metrics
        metric_terms = ['total', 'sum', 'average', 'max', 'min', 'top', 'bottom', 
                       'highest', 'lowest', 'most', 'least']
        for term in metric_terms:
            if term in query_lower:
                entities['metrics'].append(term)
        
        return entities
    
    def detect_new_patterns(self, time_window_hours: int = 24) -> List[Dict]:
        """Analyze recent queries to identify emerging patterns"""
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        recent = [q for q in self.recent_queries if q['timestamp'] > cutoff_time]
        
        if len(recent) < 3:  # Need at least 3 queries to detect patterns
            return []
        
        new_patterns = []
        
        # Group queries by similar entity combinations
        entity_groups = defaultdict(list)
        for query_data in recent:
            entities = query_data['entities']
            # Create a signature from entities
            signature = tuple(sorted([
                tuple(entities['business_entities']),
                tuple(entities['actions']),
                tuple(entities['temporal']),
                tuple(entities['metrics'])
            ]))
            entity_groups[signature].append(query_data)
        
        # Identify groups with multiple queries (potential patterns)
        for signature, queries in entity_groups.items():
            if len(queries) >= 2:  # At least 2 similar queries
                pattern = self._analyze_query_group(queries)
                if pattern and not self._is_known_pattern(pattern):
                    new_patterns.append(pattern)
        
        return new_patterns
    
    def _analyze_query_group(self, queries: List[Dict]) -> Optional[Dict]:
        """Analyze a group of similar queries to extract pattern"""
        if len(queries) < 2:
            return None
        
        # Find common tokens
        all_tokens = [set(q['tokens']) for q in queries]
        common_tokens = set.intersection(*all_tokens) if all_tokens else set()
        
        # Find common entities
        common_entities = {}
        for entity_type in ['business_entities', 'actions', 'temporal', 'metrics']:
            entity_sets = [set(q['entities'][entity_type]) for q in queries]
            common_entities[entity_type] = list(set.intersection(*entity_sets)) if entity_sets else []
        
        # Create pattern description
        pattern = {
            'pattern_id': f"auto_detected_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'common_tokens': list(common_tokens),
            'common_entities': common_entities,
            'example_queries': [q['query'] for q in queries],
            'frequency': len(queries),
            'detected_at': datetime.now().isoformat(),
            'confidence': self._calculate_pattern_confidence(queries, common_tokens, common_entities)
        }
        
        return pattern if pattern['confidence'] > 0.6 else None
    
    def _calculate_pattern_confidence(self, queries: List[Dict], common_tokens: Set[str], 
                                    common_entities: Dict[str, List[str]]) -> float:
        """Calculate confidence score for detected pattern"""
        if len(queries) < 2:
            return 0.0
        
        # Base confidence from frequency
        frequency_score = min(len(queries) / 5.0, 1.0)  # Max at 5 queries
        
        # Token overlap score
        avg_query_length = sum(len(q['tokens']) for q in queries) / len(queries)
        token_score = len(common_tokens) / max(avg_query_length, 1) if avg_query_length > 0 else 0
        
        # Entity consistency score
        total_entities = sum(len(entities) for entities in common_entities.values())
        entity_score = min(total_entities / 3.0, 1.0)  # Max at 3 entities
        
        # Weighted average
        return (frequency_score * 0.4) + (token_score * 0.3) + (entity_score * 0.3)
    
    def _is_known_pattern(self, pattern: Dict) -> bool:
        """Check if pattern is already known"""
        pattern_signature = self._create_pattern_signature(pattern)
        
        # Check against existing patterns in classifier
        for existing_pattern_str in self.classifier.query_patterns.keys():
            existing_pattern = json.loads(existing_pattern_str)
            existing_signature = self._create_pattern_signature_from_stored(existing_pattern)
            
            if self._patterns_similar(pattern_signature, existing_signature):
                return True
        
        return False
    
    def _create_pattern_signature(self, pattern: Dict) -> str:
        """Create a signature for pattern comparison"""
        entities = pattern['common_entities']
        signature_parts = []
        
        for entity_type, entity_list in entities.items():
            if entity_list:
                signature_parts.append(f"{entity_type}:{','.join(sorted(entity_list))}")
        
        return '|'.join(sorted(signature_parts))
    
    def _create_pattern_signature_from_stored(self, stored_pattern: Dict) -> str:
        """Create signature from stored pattern format"""
        signature_parts = []
        
        # Convert stored pattern format to signature
        if 'entities' in stored_pattern:
            for entity in stored_pattern['entities']:
                signature_parts.append(f"business_entities:{entity}")
        
        if 'query_types' in stored_pattern:
            for query_type in stored_pattern['query_types']:
                signature_parts.append(f"actions:{query_type}")
        
        return '|'.join(sorted(signature_parts))
    
    def _patterns_similar(self, sig1: str, sig2: str, threshold: float = 0.7) -> bool:
        """Check if two pattern signatures are similar"""
        parts1 = set(sig1.split('|'))
        parts2 = set(sig2.split('|'))
        
        if not parts1 and not parts2:
            return True
        
        intersection = len(parts1.intersection(parts2))
        union = len(parts1.union(parts2))
        
        similarity = intersection / union if union > 0 else 0
        return similarity >= threshold
    
    def suggest_new_query_types(self) -> List[Dict]:
        """Suggest new query type classifications based on usage patterns"""
        new_patterns = self.detect_new_patterns()
        suggestions = []
        
        for pattern in new_patterns:
            if pattern['confidence'] > 0.7:
                suggestion = {
                    'suggested_name': self._generate_pattern_name(pattern),
                    'description': self._generate_pattern_description(pattern),
                    'example_queries': pattern['example_queries'],
                    'confidence': pattern['confidence'],
                    'implementation_hint': self._generate_implementation_hint(pattern)
                }
                suggestions.append(suggestion)
        
        return suggestions
    
    def _generate_pattern_name(self, pattern: Dict) -> str:
        """Generate a descriptive name for the pattern"""
        entities = pattern['common_entities']
        
        # Primary entity
        primary_entity = None
        if entities['business_entities']:
            primary_entity = entities['business_entities'][0]
        
        # Primary action
        primary_action = None
        if entities['actions']:
            primary_action = entities['actions'][0]
        elif entities['metrics']:
            primary_action = entities['metrics'][0]
        
        # Temporal aspect
        temporal = entities['temporal'][0] if entities['temporal'] else None
        
        # Construct name
        name_parts = []
        if primary_action:
            name_parts.append(primary_action.title())
        if primary_entity:
            name_parts.append(primary_entity.title())
        if temporal:
            name_parts.append(f"({temporal})")
        
        return " ".join(name_parts) if name_parts else "Unknown Pattern"
    
    def _generate_pattern_description(self, pattern: Dict) -> str:
        """Generate a description for the pattern"""
        entities = pattern['common_entities']
        examples = pattern['example_queries']
        
        description = f"Pattern detected from {len(examples)} similar queries. "
        
        if entities['business_entities']:
            description += f"Focuses on {', '.join(entities['business_entities'])}. "
        
        if entities['actions']:
            description += f"Common actions: {', '.join(entities['actions'])}. "
        
        if entities['temporal']:
            description += f"Temporal aspects: {', '.join(entities['temporal'])}. "
        
        return description
    
    def _generate_implementation_hint(self, pattern: Dict) -> str:
        """Generate implementation hints for the pattern"""
        entities = pattern['common_entities']
        
        hints = []
        
        if 'count' in entities.get('actions', []):
            hints.append("Implement COUNT aggregation")
        
        if 'list' in entities.get('actions', []):
            hints.append("Implement MATCH with RETURN")
        
        if entities.get('temporal'):
            hints.append("Add temporal filtering")
        
        if entities.get('metrics'):
            hints.append("Add aggregation functions")
        
        return "; ".join(hints) if hints else "Custom implementation needed"
    
    def get_detection_statistics(self) -> Dict:
        """Get statistics about pattern detection"""
        return {
            'total_queries_analyzed': len(self.recent_queries),
            'patterns_detected': len(self.discovered_patterns),
            'suggestions_generated': len(self.pattern_suggestions),
            'recent_activity': len([q for q in self.recent_queries 
                                  if q['timestamp'] > datetime.now() - timedelta(hours=1)])
        }