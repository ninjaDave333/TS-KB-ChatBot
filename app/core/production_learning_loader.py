"""
Production Learning Loader - Initialize Dynamic RAG with production insights
"""

import json
import os
from .enhanced_query_generator import EnhancedQueryGenerator

class ProductionLearningLoader:
    """Load production insights into Dynamic RAG system"""
    
    @staticmethod
    def load_production_patterns(generator: EnhancedQueryGenerator):
        """Load production patterns into the enhanced generator"""
        
        # Load production seed data
        seed_file = "data/production_learning_seed.json"
        if os.path.exists(seed_file):
            with open(seed_file, 'r') as f:
                seed_data = json.load(f)
            
            # Import the learning data
            generator.import_learning_data(seed_data)
            print(f"Loaded {len(seed_data.get('patterns', {}))} production patterns")
        
        # Add specific production optimizations
        ProductionLearningLoader._add_data_quality_filters(generator)
        ProductionLearningLoader._add_teams_recording_templates(generator)
    
    @staticmethod
    def _add_data_quality_filters(generator: EnhancedQueryGenerator):
        """Add automatic data quality filters based on production insights"""
        
        # Israeli clients with managers - auto-filter Unknown
        generator.classifier.query_patterns[
            '{"complexity": 3, "entities": ["client"], "query_types": ["list_queries", "filter_queries"]}'
        ] = {
            'cypher_template': 'MATCH (c:Client)-[:MANAGED_BY]->(e:Employee) WHERE c.region = "IL" AND e.name IS NOT NULL AND toLower(e.name) <> "unknown" RETURN c.sf_name as client_name, e.name as manager_name',
            'success_rate': 0.9,
            'avg_execution_time': 1.7,
            'usage_count': 3,
            'data_count': 25,
            'example_queries': ['List Israeli clients with managers', 'List 10 Israeli clients with managers'],
            'created_at': '2025-11-17T16:45:00.000000',
            'production_optimized': True
        }
    
    @staticmethod
    def _add_teams_recording_templates(generator: EnhancedQueryGenerator):
        """Add Teams Recording templates based on production usage"""
        
        # External meetings template
        generator.classifier.query_patterns[
            '{"complexity": 2, "entities": ["meeting", "recording"], "query_types": ["count_queries"], "meeting_type": "external"}'
        ] = {
            'cypher_template': 'MATCH (r:Recording)-[:LINKED_TO]->(c:CalendarEvent) WHERE size(c.externalParticipants) > 0 RETURN count(r) as external_meetings_recorded',
            'success_rate': 1.0,
            'avg_execution_time': 1.5,
            'usage_count': 5,
            'data_count': 1,
            'example_queries': ['How many external meetings recorded?', 'Count external meetings'],
            'created_at': '2025-11-17T16:45:00.000000',
            'production_optimized': True
        }
        
        # Internal meetings template
        generator.classifier.query_patterns[
            '{"complexity": 2, "entities": ["meeting", "recording"], "query_types": ["count_queries"], "meeting_type": "internal"}'
        ] = {
            'cypher_template': 'MATCH (r:Recording)-[:LINKED_TO]->(c:CalendarEvent) WHERE size(c.externalParticipants) = 0 RETURN count(r) as internal_meetings_recorded',
            'success_rate': 1.0,
            'avg_execution_time': 1.3,
            'usage_count': 3,
            'data_count': 1,
            'example_queries': ['How many internal meetings recorded?', 'Count internal meetings'],
            'created_at': '2025-11-17T16:45:00.000000',
            'production_optimized': True
        }
        
        # 2025 active clients template
        generator.classifier.query_patterns[
            '{"complexity": 4, "entities": ["client"], "query_types": ["comparison_queries", "temporal_queries"]}'
        ] = {
            'cypher_template': 'MATCH (c:Client)-[o:OPPORTUNITY]->(p:Product) WHERE o.opportunity_stage = \'Closed Won\' AND o.close_date >= \'2025-01-01\' AND o.close_date < \'2026-01-01\' WITH c, count(o) as deal_count ORDER BY deal_count DESC LIMIT 10 RETURN c.sf_name as client_name, deal_count',
            'success_rate': 1.0,
            'avg_execution_time': 1.6,
            'usage_count': 2,
            'data_count': 10,
            'example_queries': ['who are the top 10 most active clients in 2025?', 'top active clients 2025'],
            'created_at': '2025-11-17T16:45:00.000000',
            'production_optimized': True
        }
        
        # Save the updated patterns
        generator.classifier.save_patterns()
        print("Added production-optimized Teams Recording templates")