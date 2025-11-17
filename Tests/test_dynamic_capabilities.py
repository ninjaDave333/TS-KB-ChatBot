"""
Test script for Dynamic RAG capabilities
Tests the adaptive query classifier and dynamic query detector
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.enhanced_query_generator import EnhancedQueryGenerator
import time
import json

def test_basic_learning():
    """Test basic learning functionality"""
    print("=== Testing Basic Learning Functionality ===")
    
    generator = EnhancedQueryGenerator()
    
    # Test queries
    test_queries = [
        "How many clients do we have?",
        "List all employees",
        "Show me products from 2024",
        "Count total deals",
        "Who are our top clients?",
        "How many employees work here?",  # Similar to first query
        "List all clients",  # Similar pattern to employees
        "Show products from 2025"  # Similar temporal pattern
    ]
    
    print(f"Testing with {len(test_queries)} queries...")
    
    for i, query in enumerate(test_queries):
        print(f"\n--- Query {i+1}: {query} ---")
        
        # Generate query with learning
        result = generator.generate_cypher_with_learning(query)
        
        print(f"Method: {result['method']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Cypher: {result['cypher']}")
        
        # Simulate successful execution
        if i % 2 == 0:  # Simulate success for even queries
            generator.record_query_success(
                query=query,
                cypher=result['cypher'],
                execution_time=result['execution_time'],
                data_count=10 + i  # Simulate varying data counts
            )
            print("[SUCCESS] Recorded as successful")
        else:  # Simulate failure for odd queries
            generator.record_query_failure(
                query=query,
                error_type="SyntaxError",
                error_details="Invalid Cypher syntax"
            )
            print("[FAILED] Recorded as failed")
    
    return generator

def test_pattern_detection(generator):
    """Test pattern detection capabilities"""
    print("\n=== Testing Pattern Detection ===")
    
    # Add more similar queries to trigger pattern detection
    similar_queries = [
        "How many deals were closed?",
        "Count the opportunities",
        "Total number of meetings",
        "How many recordings do we have?",
        "Show me all clients from Israel",
        "List employees in Tel Aviv",
        "Display products for HashiCorp",
        "Get all deals from 2024"
    ]
    
    for query in similar_queries:
        result = generator.generate_cypher_with_learning(query)
        generator.record_query_success(
            query=query,
            cypher=result['cypher'],
            execution_time=0.5,
            data_count=5
        )
    
    # Get pattern suggestions
    suggestions = generator.get_pattern_suggestions()
    print(f"Pattern suggestions found: {len(suggestions)}")
    
    for i, suggestion in enumerate(suggestions):
        print(f"\nSuggestion {i+1}:")
        print(f"  Name: {suggestion['suggested_name']}")
        print(f"  Confidence: {suggestion['confidence']:.2f}")
        print(f"  Description: {suggestion['description']}")
        print(f"  Examples: {suggestion['example_queries'][:2]}")

def test_learning_insights(generator):
    """Test learning insights and analytics"""
    print("\n=== Testing Learning Insights ===")
    
    insights = generator.get_learning_insights()
    
    print(f"Learning Maturity: {insights['learning_maturity']:.2f}")
    print(f"Pattern Diversity: {insights['pattern_diversity']:.2f}")
    print(f"Success Trends: {insights['success_trends']}")
    print(f"Failure Insights: {insights['failure_insights']}")
    
    if insights['recommendations']:
        print("\nRecommendations:")
        for rec in insights['recommendations']:
            print(f"  • {rec}")

def test_query_trends(generator):
    """Test query trend analysis"""
    print("\n=== Testing Query Trend Analysis ===")
    
    trends = generator.analyze_query_trends(24)
    
    print(f"New patterns detected: {trends['new_patterns_detected']}")
    print(f"Pattern suggestions: {trends['pattern_suggestions']}")
    print(f"Learning statistics: {trends['learning_statistics']}")
    
    if trends['recommendations']:
        print("\nTrend Recommendations:")
        for rec in trends['recommendations']:
            print(f"  • {rec}")

def test_export_import(generator):
    """Test data export and import functionality"""
    print("\n=== Testing Export/Import Functionality ===")
    
    # Export learning data
    exported_data = generator.export_learning_data()
    
    print(f"Exported data contains:")
    print(f"  - {len(exported_data['query_patterns'])} query patterns")
    print(f"  - {len(exported_data['failure_analysis'])} failure patterns")
    print(f"  - {len(exported_data['recent_queries'])} recent queries")
    
    # Test import (create new generator and import data)
    new_generator = EnhancedQueryGenerator()
    new_generator.import_learning_data(exported_data)
    
    # Verify import
    new_insights = new_generator.get_learning_insights()
    print(f"After import - Learning Maturity: {new_insights['learning_maturity']:.2f}")

def main():
    """Run all dynamic capability tests"""
    print("Starting Dynamic RAG Capabilities Test")
    print("=" * 50)
    
    try:
        # Test basic learning
        generator = test_basic_learning()
        
        # Test pattern detection
        test_pattern_detection(generator)
        
        # Test learning insights
        test_learning_insights(generator)
        
        # Test query trends
        test_query_trends(generator)
        
        # Test export/import
        test_export_import(generator)
        
        print("\n" + "=" * 50)
        print("[SUCCESS] All Dynamic RAG tests completed successfully!")
        
        # Final statistics
        final_stats = generator.classifier.get_pattern_statistics()
        print(f"\nFinal Statistics:")
        print(f"  Total patterns learned: {final_stats['total_patterns']}")
        print(f"  Total failures recorded: {final_stats['total_failures']}")
        print(f"  Average success rate: {final_stats.get('avg_success_rate', 0):.2f}")
        
    except Exception as e:
        print(f"\n[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()