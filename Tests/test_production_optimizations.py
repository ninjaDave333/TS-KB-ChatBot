"""
Test Production Optimizations - Validate production learning integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.enhanced_query_generator import EnhancedQueryGenerator
from app.core.production_learning_loader import ProductionLearningLoader

def test_production_optimizations():
    """Test production optimization features"""
    print("=== Testing Production Optimizations ===")
    
    generator = EnhancedQueryGenerator()
    
    # Load production patterns
    ProductionLearningLoader.load_production_patterns(generator)
    
    # Test queries from production logs
    test_queries = [
        "How many external meetings recorded?",
        "How many internal meetings recorded?", 
        "List 10 Israeli clients with managers",
        "List Israeli clients with managers",
        "who are the top 10 most active clients in 2025?"
    ]
    
    print(f"Testing {len(test_queries)} production queries...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"--- Test {i}: {query} ---")
        
        # Generate with learning
        result = generator.generate_cypher_with_learning(query)
        
        print(f"Method: {result['method']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Cypher: {result['cypher']}")
        
        # Check for optimizations
        if result.get('optimization_result'):
            opt = result['optimization_result']
            if opt['optimizations_applied']:
                print(f"Optimizations: {', '.join(opt['optimizations_applied'])}")
                print(f"Reason: {opt['improvement_reason']}")
        
        # Get suggestions
        suggestions = generator.optimizer.suggest_query_improvements(query)
        if suggestions:
            print(f"Suggestions: {'; '.join(suggestions)}")
        
        print()
    
    # Test pattern statistics
    stats = generator.classifier.get_pattern_statistics()
    print(f"=== Learning Statistics ===")
    print(f"Total patterns: {stats['total_patterns']}")
    print(f"Production patterns loaded: {len([p for p in generator.classifier.query_patterns.values() if p.get('production_optimized')])}")
    
    return generator

if __name__ == "__main__":
    test_production_optimizations()