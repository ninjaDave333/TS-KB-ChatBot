"""
Adaptive Query Classifier - Learns query patterns from successful interactions
Part of Dynamic RAG Enhancement Phase 1
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re
from collections import defaultdict

class AdaptiveQueryClassifier:
    """Learns query patterns from successful interactions"""
    
    def __init__(self, patterns_file: str = "data/query_patterns.json"):
        self.patterns_file = patterns_file
        self.query_patterns = {}
        self.success_history = {}
        self.failure_analysis = {}
        self.load_patterns()
    
    def load_patterns(self):
        """Load existing patterns from file"""
        if os.path.exists(self.patterns_file):
            try:
                with open(self.patterns_file, 'r') as f:
                    data = json.load(f)
                    self.query_patterns = data.get('patterns', {})
                    self.success_history = data.get('success_history', {})
                    self.failure_analysis = data.get('failure_analysis', {})
            except Exception as e:
                print(f"Error loading patterns: {e}")
    
    def save_patterns(self):
        """Save patterns to file"""
        os.makedirs(os.path.dirname(self.patterns_file), exist_ok=True)
        data = {
            'patterns': self.query_patterns,
            'success_history': self.success_history,
            'failure_analysis': self.failure_analysis,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.patterns_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def extract_semantic_pattern(self, query: str) -> str:
        """Extract semantic patterns using NLP techniques"""
        query_lower = query.lower().strip()
        
        # Entity extraction patterns
        entities = {
            'count_queries': ['how many', 'count', 'total', 'number of'],
            'list_queries': ['list', 'show', 'display', 'get all'],
            'filter_queries': ['where', 'with', 'having', 'that have'],
            'temporal_queries': ['in 2024', 'in 2025', 'last year', 'this year'],
            'comparison_queries': ['top', 'best', 'highest', 'lowest', 'most', 'least'],
            'relationship_queries': ['managed by', 'works with', 'belongs to', 'part of']
        }
        
        # Extract pattern components
        pattern_components = []
        
        for pattern_type, keywords in entities.items():
            if any(keyword in query_lower for keyword in keywords):
                pattern_components.append(pattern_type)
        
        # Extract entity types
        entity_types = []
        common_entities = ['client', 'employee', 'product', 'deal', 'opportunity', 'recording', 'meeting']
        for entity in common_entities:
            if entity in query_lower:
                entity_types.append(entity)
        
        # Create semantic pattern
        pattern = {
            'query_types': pattern_components,
            'entities': entity_types,
            'complexity': len(pattern_components) + len(entity_types)
        }
        
        return json.dumps(pattern, sort_keys=True)
    
    def learn_from_feedback(self, query: str, cypher: str, success_rate: float, 
                          execution_time: float, data_count: int = 0):
        """Store successful patterns for future reuse"""
        pattern = self.extract_semantic_pattern(query)
        
        if pattern not in self.query_patterns:
            self.query_patterns[pattern] = {
                'cypher_template': cypher,
                'success_rate': success_rate,
                'avg_execution_time': execution_time,
                'usage_count': 1,
                'data_count': data_count,
                'example_queries': [query],
                'created_at': datetime.now().isoformat()
            }
        else:
            # Update existing pattern
            existing = self.query_patterns[pattern]
            existing['usage_count'] += 1
            existing['success_rate'] = (existing['success_rate'] + success_rate) / 2
            existing['avg_execution_time'] = (existing['avg_execution_time'] + execution_time) / 2
            
            if query not in existing['example_queries']:
                existing['example_queries'].append(query)
                if len(existing['example_queries']) > 5:  # Keep only 5 examples
                    existing['example_queries'] = existing['example_queries'][-5:]
            
            existing['last_used'] = datetime.now().isoformat()
        
        self.save_patterns()
    
    def record_failure(self, query: str, error_type: str, error_details: str):
        """Record failed queries for learning"""
        pattern = self.extract_semantic_pattern(query)
        
        if pattern not in self.failure_analysis:
            self.failure_analysis[pattern] = {
                'failure_count': 1,
                'error_types': {error_type: 1},
                'example_failures': [{'query': query, 'error': error_details}],
                'first_failure': datetime.now().isoformat()
            }
        else:
            failure_data = self.failure_analysis[pattern]
            failure_data['failure_count'] += 1
            
            if error_type in failure_data['error_types']:
                failure_data['error_types'][error_type] += 1
            else:
                failure_data['error_types'][error_type] = 1
            
            failure_data['example_failures'].append({'query': query, 'error': error_details})
            if len(failure_data['example_failures']) > 3:  # Keep only 3 examples
                failure_data['example_failures'] = failure_data['example_failures'][-3:]
            
            failure_data['last_failure'] = datetime.now().isoformat()
        
        self.save_patterns()
    
    def find_similar_pattern(self, query: str, threshold: float = 0.7) -> Optional[Dict]:
        """Find similar successful patterns for a new query"""
        target_pattern = json.loads(self.extract_semantic_pattern(query))
        
        best_match = None
        best_score = 0
        
        for pattern_str, pattern_data in self.query_patterns.items():
            stored_pattern = json.loads(pattern_str)
            
            # Calculate similarity score
            score = self._calculate_pattern_similarity(target_pattern, stored_pattern)
            
            if score > best_score and score >= threshold:
                best_score = score
                best_match = {
                    'pattern': stored_pattern,
                    'data': pattern_data,
                    'similarity_score': score
                }
        
        return best_match
    
    def _calculate_pattern_similarity(self, pattern1: Dict, pattern2: Dict) -> float:
        """Calculate similarity between two patterns"""
        # Compare query types
        types1 = set(pattern1.get('query_types', []))
        types2 = set(pattern2.get('query_types', []))
        type_similarity = len(types1.intersection(types2)) / max(len(types1.union(types2)), 1)
        
        # Compare entities
        entities1 = set(pattern1.get('entities', []))
        entities2 = set(pattern2.get('entities', []))
        entity_similarity = len(entities1.intersection(entities2)) / max(len(entities1.union(entities2)), 1)
        
        # Weighted average
        return (type_similarity * 0.6) + (entity_similarity * 0.4)
    
    def get_pattern_statistics(self) -> Dict:
        """Get statistics about learned patterns"""
        total_patterns = len(self.query_patterns)
        total_failures = len(self.failure_analysis)
        
        if total_patterns == 0:
            return {'total_patterns': 0, 'total_failures': total_failures}
        
        avg_success_rate = sum(p['success_rate'] for p in self.query_patterns.values()) / total_patterns
        avg_usage = sum(p['usage_count'] for p in self.query_patterns.values()) / total_patterns
        
        return {
            'total_patterns': total_patterns,
            'total_failures': total_failures,
            'avg_success_rate': avg_success_rate,
            'avg_usage_count': avg_usage,
            'most_used_patterns': sorted(
                self.query_patterns.items(),
                key=lambda x: x[1]['usage_count'],
                reverse=True
            )[:5]
        }