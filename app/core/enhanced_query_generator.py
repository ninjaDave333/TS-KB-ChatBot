"""
Enhanced Query Generator with Dynamic Learning Capabilities
Integrates with Adaptive Query Classifier and Dynamic Query Detector
"""

from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime
from .adaptive_query_classifier import AdaptiveQueryClassifier
from .dynamic_query_detector import DynamicQueryDetector
from .smart_query_optimizer import SmartQueryOptimizer
from .query_generator import QueryGenerator

class EnhancedQueryGenerator(QueryGenerator):
    """Enhanced query generator with dynamic learning capabilities"""
    
    def __init__(self):
        super().__init__()
        self.classifier = AdaptiveQueryClassifier()
        self.detector = DynamicQueryDetector(self.classifier)
        self.optimizer = SmartQueryOptimizer()
        self.query_history = []
    
    def generate_cypher_with_learning(self, query: str) -> Dict[str, Any]:
        """Generate Cypher with learning capabilities"""
        start_time = datetime.now()
        
        # Add query to detector for pattern analysis
        self.detector.add_query(query)
        
        # Check for similar successful patterns first
        similar_pattern = self.classifier.find_similar_pattern(query)
        
        if similar_pattern and similar_pattern['similarity_score'] > 0.8:
            # Use learned pattern
            cypher = self._adapt_learned_pattern(query, similar_pattern)
            method = "learned_pattern"
            confidence = similar_pattern['similarity_score']
        else:
            # Fall back to original generation
            cypher = self.generate_cypher(query)
            method = "traditional_generation"
            confidence = 0.6  # Default confidence for traditional method
        
        # Apply smart optimizations
        optimization_result = self.optimizer.optimize_query(query, cypher)
        if optimization_result['optimizations_applied']:
            cypher = optimization_result['optimized_cypher']
            method += "_optimized"
            confidence = min(confidence + 0.1, 1.0)  # Boost confidence for optimized queries
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        result = {
            'cypher': cypher,
            'method': method,
            'confidence': confidence,
            'execution_time': execution_time,
            'similar_pattern': similar_pattern,
            'optimization_result': optimization_result if 'optimization_result' in locals() else None,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store for learning
        self.query_history.append({
            'query': query,
            'result': result
        })
        
        return result
    
    def _adapt_learned_pattern(self, query: str, similar_pattern: Dict) -> str:
        """Adapt a learned pattern to the current query"""
        base_cypher = similar_pattern['data']['cypher_template']
        
        # Simple adaptation - replace entity names
        adapted_cypher = base_cypher
        
        # Extract entities from current query
        current_entities = self.extract_entities(query)
        
        # Try to adapt the cypher based on current entities
        query_lower = query.lower()
        
        # Replace node types if different
        if 'client' in query_lower and 'Employee' in base_cypher:
            adapted_cypher = base_cypher.replace('Employee', 'Client').replace('e:', 'c:')
        elif 'employee' in query_lower and 'Client' in base_cypher:
            adapted_cypher = base_cypher.replace('Client', 'Employee').replace('c:', 'e:')
        elif 'product' in query_lower and ('Client' in base_cypher or 'Employee' in base_cypher):
            adapted_cypher = base_cypher.replace('Client', 'Product').replace('Employee', 'Product')
            adapted_cypher = adapted_cypher.replace('c:', 'p:').replace('e:', 'p:')
        
        # Handle temporal adaptations
        if current_entities['temporal']:
            year = current_entities['temporal'][0]
            if 'WHERE' in adapted_cypher:
                # Add year filter to existing WHERE clause
                adapted_cypher = adapted_cypher.replace('WHERE', f'WHERE toString(n.year) = \"{year}\" AND')
            else:
                # Add WHERE clause before RETURN
                adapted_cypher = adapted_cypher.replace('RETURN', f'WHERE toString(n.year) = \"{year}\" RETURN')
        
        return adapted_cypher
    
    def record_query_success(self, query: str, cypher: str, execution_time: float, 
                           data_count: int, user_feedback: Optional[float] = None):
        """Record successful query execution for learning"""
        success_rate = 1.0 if user_feedback is None else user_feedback
        
        self.classifier.learn_from_feedback(
            query=query,
            cypher=cypher,
            success_rate=success_rate,
            execution_time=execution_time,
            data_count=data_count
        )
    
    def record_query_failure(self, query: str, error_type: str, error_details: str):
        """Record failed query for learning"""
        self.classifier.record_failure(query, error_type, error_details)
    
    def get_pattern_suggestions(self) -> List[Dict]:
        """Get suggestions for new query patterns"""
        return self.detector.suggest_new_query_types()
    
    def analyze_query_trends(self, time_window_hours: int = 24) -> Dict:
        """Analyze recent query trends"""
        new_patterns = self.detector.detect_new_patterns(time_window_hours)
        suggestions = self.detector.suggest_new_query_types()
        stats = self.classifier.get_pattern_statistics()
        detection_stats = self.detector.get_detection_statistics()
        
        return {
            'new_patterns_detected': len(new_patterns),
            'pattern_suggestions': len(suggestions),
            'learning_statistics': stats,
            'detection_statistics': detection_stats,
            'recommendations': self._generate_recommendations(new_patterns, suggestions)
        }
    
    def _generate_recommendations(self, new_patterns: List[Dict], 
                                suggestions: List[Dict]) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        if len(new_patterns) > 3:
            recommendations.append(
                f"High pattern activity detected ({len(new_patterns)} new patterns). "
                "Consider implementing automated pattern recognition."
            )
        
        if len(suggestions) > 0:
            high_confidence = [s for s in suggestions if s['confidence'] > 0.8]
            if high_confidence:
                recommendations.append(
                    f"{len(high_confidence)} high-confidence pattern suggestions available. "
                    "Consider implementing these patterns."
                )
        
        # Check for failure patterns
        total_failures = len(self.classifier.failure_analysis)
        if total_failures > 5:
            recommendations.append(
                f"{total_failures} failure patterns identified. "
                "Review and implement fixes for common failure cases."
            )
        
        return recommendations
    
    def export_learning_data(self) -> Dict:
        """Export learning data for analysis or backup"""
        return {
            'query_patterns': self.classifier.query_patterns,
            'success_history': self.classifier.success_history,
            'failure_analysis': self.classifier.failure_analysis,
            'recent_queries': [q for q in self.detector.recent_queries[-50:]],  # Last 50
            'export_timestamp': datetime.now().isoformat(),
            'statistics': {
                'total_patterns': len(self.classifier.query_patterns),
                'total_failures': len(self.classifier.failure_analysis),
                'recent_activity': len(self.detector.recent_queries)
            }
        }
    
    def import_learning_data(self, data: Dict):
        """Import learning data from backup or external source"""
        if 'query_patterns' in data:
            self.classifier.query_patterns.update(data['query_patterns'])
        
        if 'success_history' in data:
            self.classifier.success_history.update(data['success_history'])
        
        if 'failure_analysis' in data:
            self.classifier.failure_analysis.update(data['failure_analysis'])
        
        # Save imported data
        self.classifier.save_patterns()
    
    def get_learning_insights(self) -> Dict:
        """Get insights about the learning process"""
        stats = self.classifier.get_pattern_statistics()
        
        insights = {
            'learning_maturity': self._calculate_learning_maturity(),
            'pattern_diversity': self._calculate_pattern_diversity(),
            'success_trends': self._analyze_success_trends(),
            'failure_insights': self._analyze_failure_patterns(),
            'recommendations': []
        }
        
        # Generate insights-based recommendations
        if insights['learning_maturity'] < 0.3:
            insights['recommendations'].append("System is in early learning phase. Collect more query examples.")
        
        if insights['pattern_diversity'] < 0.5:
            insights['recommendations'].append("Limited pattern diversity. Encourage varied query types.")
        
        return insights
    
    def _calculate_learning_maturity(self) -> float:
        """Calculate how mature the learning system is"""
        total_patterns = len(self.classifier.query_patterns)
        total_usage = sum(p['usage_count'] for p in self.classifier.query_patterns.values())
        
        if total_patterns == 0:
            return 0.0
        
        avg_usage = total_usage / total_patterns
        maturity = min(total_patterns / 20.0, 1.0) * min(avg_usage / 5.0, 1.0)
        
        return maturity
    
    def _calculate_pattern_diversity(self) -> float:
        """Calculate diversity of learned patterns"""
        if not self.classifier.query_patterns:
            return 0.0
        
        # Count unique entity types across patterns
        all_entities = set()
        for pattern_str in self.classifier.query_patterns.keys():
            pattern = json.loads(pattern_str)
            all_entities.update(pattern.get('entities', []))
        
        # Diversity based on entity variety
        return min(len(all_entities) / 10.0, 1.0)  # Max diversity at 10 different entities
    
    def _analyze_success_trends(self) -> Dict:
        """Analyze success rate trends"""
        if not self.classifier.query_patterns:
            return {'trend': 'insufficient_data'}
        
        success_rates = [p['success_rate'] for p in self.classifier.query_patterns.values()]
        avg_success = sum(success_rates) / len(success_rates)
        
        return {
            'average_success_rate': avg_success,
            'trend': 'improving' if avg_success > 0.8 else 'needs_attention',
            'total_successful_patterns': len([r for r in success_rates if r > 0.8])
        }
    
    def _analyze_failure_patterns(self) -> Dict:
        """Analyze common failure patterns"""
        if not self.classifier.failure_analysis:
            return {'status': 'no_failures_recorded'}
        
        # Count error types
        error_type_counts = {}
        for failure_data in self.classifier.failure_analysis.values():
            for error_type, count in failure_data['error_types'].items():
                error_type_counts[error_type] = error_type_counts.get(error_type, 0) + count
        
        most_common_error = max(error_type_counts.items(), key=lambda x: x[1]) if error_type_counts else None
        
        return {
            'total_failure_patterns': len(self.classifier.failure_analysis),
            'error_type_distribution': error_type_counts,
            'most_common_error': most_common_error[0] if most_common_error else None,
            'improvement_priority': 'high' if len(self.classifier.failure_analysis) > 10 else 'medium'
        }