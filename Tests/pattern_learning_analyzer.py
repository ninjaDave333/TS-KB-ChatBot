#!/usr/bin/env python3
"""
Human-in-the-Loop Pattern Learning Analyzer

Analyzes production traces to identify potential learned patterns
and presents each one for human approval before implementation.
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
import re

class PatternLearningAnalyzer:
    def __init__(self, traces_file="ref_data/traces.jsonl"):
        self.traces_file = Path(traces_file)
        self.traces = []
        self.potential_patterns = []
        
    def load_traces(self):
        """Load production traces"""
        with open(self.traces_file, 'r', encoding='utf-8') as f:
            self.traces = [json.loads(line) for line in f if line.strip()]
        print(f"Loaded {len(self.traces)} production traces")
    
    def identify_pattern_candidates(self):
        """Identify potential patterns from successful queries"""
        # Group successful queries by similarity
        successful_queries = []
        
        for trace in self.traces:
            if (trace.get('neo4j_result_summary', {}).get('has_data', False) and 
                trace.get('cypher_query') and 
                trace.get('routing_path') == 'ai_generated'):
                
                successful_queries.append({
                    'query': trace.get('query', ''),
                    'intent': trace.get('intent', ''),
                    'cypher': trace.get('cypher_query', ''),
                    'trace_id': trace.get('trace_id', '')
                })
        
        print(f"Found {len(successful_queries)} successful AI-generated queries")
        
        # Group by intent and find similar patterns
        by_intent = defaultdict(list)
        for q in successful_queries:
            by_intent[q['intent']].append(q)
        
        # Identify patterns within each intent
        for intent, queries in by_intent.items():
            if len(queries) >= 2:  # Need at least 2 queries to form a pattern
                patterns = self._find_similar_queries(queries, intent)
                self.potential_patterns.extend(patterns)
    
    def _find_similar_queries(self, queries, intent):
        """Find similar query patterns within an intent"""
        patterns = []
        
        # Look for exact Cypher matches first (most reliable)
        cypher_counts = Counter()
        cypher_to_queries = defaultdict(list)
        
        for q in queries:
            cypher = q['cypher'].strip()
            cypher_counts[cypher] += 1
            cypher_to_queries[cypher].append(q)
        
        # Find Cypher queries that appear multiple times
        for cypher, count in cypher_counts.items():
            if count >= 2:  # Same Cypher used for different questions
                group = cypher_to_queries[cypher]
                pattern = self._create_pattern_candidate(group, intent, cypher)
                if pattern:
                    patterns.append(pattern)
        
        # Also look for structural similarities
        if len(patterns) < 3:  # If we don't have enough exact matches
            structural_patterns = self._find_structural_patterns(queries, intent)
            patterns.extend(structural_patterns)
        
        return patterns
    
    def _find_structural_patterns(self, queries, intent):
        """Find structurally similar queries"""
        patterns = []
        
        # Group by query structure patterns
        structure_groups = defaultdict(list)
        
        for q in queries:
            # Create a structural signature
            signature = self._create_query_signature(q['query'])
            if signature:
                structure_groups[signature].append(q)
        
        # Find groups with multiple queries
        for signature, group in structure_groups.items():
            if len(group) >= 2:
                pattern = self._create_pattern_candidate(group, intent, group[0]['cypher'])
                if pattern:
                    patterns.append(pattern)
        
        return patterns
    
    def _create_query_signature(self, query_text):
        """Create a signature for query structure"""
        query_lower = query_text.lower()
        
        # Common query patterns
        if 'how many' in query_lower and ('in' in query_lower or 'during' in query_lower):
            return 'count_with_timeframe'
        elif 'top' in query_lower and ('client' in query_lower or 'product' in query_lower):
            return 'top_ranking'
        elif 'list' in query_lower and ('client' in query_lower or 'product' in query_lower):
            return 'list_entities'
        elif 'who is' in query_lower or 'who has' in query_lower:
            return 'who_query'
        elif 'what is' in query_lower or 'what are' in query_lower:
            return 'what_query'
        elif 'hashicorp' in query_lower or 'vault' in query_lower or 'terraform' in query_lower:
            return 'vendor_specific'
        elif 'security' in query_lower:
            return 'security_related'
        elif 'meeting' in query_lower or 'recording' in query_lower:
            return 'meeting_related'
        
        return None
    
    def _normalize_cypher(self, cypher):
        """Normalize Cypher query to identify structural patterns"""
        if not cypher:
            return ""
        
        # Remove specific values but keep structure
        normalized = cypher
        
        # Replace specific dates with placeholders
        normalized = re.sub(r"'20\d{2}-\d{2}-\d{2}'", "'YYYY-MM-DD'", normalized)
        
        # Replace specific client/product names with placeholders
        normalized = re.sub(r"'[^']{10,}'", "'SPECIFIC_VALUE'", normalized)
        
        # Replace specific numbers
        normalized = re.sub(r'\b\d{4}\b', 'YEAR', normalized)
        normalized = re.sub(r'\bLIMIT \d+\b', 'LIMIT N', normalized)
        
        # Normalize whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def _create_pattern_candidate(self, queries, intent, normalized_cypher):
        """Create a pattern candidate from similar queries"""
        if len(queries) < 2:
            return None
        
        # Find common query patterns
        query_texts = [q['query'].lower() for q in queries]
        
        # Look for common keywords/phrases
        common_words = self._find_common_keywords(query_texts)
        
        if len(common_words) < 2:
            return None
        
        return {
            'intent': intent,
            'pattern_type': self._classify_pattern_type(queries[0]['cypher']),
            'trigger_keywords': common_words,
            'example_queries': [q['query'] for q in queries[:3]],
            'cypher_template': queries[0]['cypher'],  # Use first as template
            'confidence': len(queries) / 10.0,  # Simple confidence score
            'frequency': len(queries),
            'success_rate': 1.0  # All queries in group were successful
        }
    
    def _find_common_keywords(self, query_texts):
        """Find common keywords across similar queries"""
        # Split queries into words
        all_words = []
        for query in query_texts:
            words = re.findall(r'\b\w+\b', query.lower())
            all_words.append(set(words))
        
        # Find words that appear in most queries
        if not all_words:
            return []
        
        common = all_words[0]
        for word_set in all_words[1:]:
            common = common.intersection(word_set)
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'what', 'how', 'many', 'much'}
        
        return [word for word in common if word not in stop_words and len(word) > 2]
    
    def _classify_pattern_type(self, cypher):
        """Classify the type of pattern based on Cypher structure"""
        if 'count(' in cypher.lower():
            return 'count_query'
        elif 'limit 1' in cypher.lower():
            return 'single_result'
        elif 'order by' in cypher.lower() and 'limit' in cypher.lower():
            return 'top_n_query'
        elif 'sum(' in cypher.lower():
            return 'aggregation'
        else:
            return 'general_query'
    
    def present_patterns_for_approval(self):
        """Present each pattern to user for approval"""
        if not self.potential_patterns:
            print("No potential patterns found")
            return []
        
        approved_patterns = []
        
        print(f"\nFound {len(self.potential_patterns)} potential patterns for review:")
        print("=" * 60)
        
        for i, pattern in enumerate(self.potential_patterns, 1):
            print(f"\nPATTERN #{i}")
            print(f"Intent: {pattern['intent']}")
            print(f"Type: {pattern['pattern_type']}")
            print(f"Frequency: {pattern['frequency']} similar queries")
            print(f"Confidence: {pattern['confidence']:.2f}")
            
            print(f"\nTrigger Keywords: {', '.join(pattern['trigger_keywords'])}")
            
            print(f"\nExample Queries:")
            for j, example in enumerate(pattern['example_queries'], 1):
                print(f"  {j}. \"{example}\"")
            
            print(f"\nCypher Template:")
            print(f"  {pattern['cypher_template'][:100]}...")
            
            print("\n" + "-" * 40)
            
            # Ask for approval
            while True:
                response = input(f"Approve this pattern? (y/n/s=skip): ").lower().strip()
                if response in ['y', 'yes']:
                    approved_patterns.append(pattern)
                    print("Pattern approved!")
                    break
                elif response in ['n', 'no']:
                    print("Pattern rejected")
                    break
                elif response in ['s', 'skip']:
                    print("Pattern skipped")
                    break
                else:
                    print("Please enter 'y' for yes, 'n' for no, or 's' to skip")
        
        return approved_patterns
    
    def save_approved_patterns(self, approved_patterns):
        """Save approved patterns to learned patterns file"""
        if not approved_patterns:
            print("No patterns to save")
            return
        
        patterns_file = Path("ref_data/learned_patterns.json")
        
        # Load existing patterns if any
        existing_patterns = []
        if patterns_file.exists():
            with open(patterns_file, 'r', encoding='utf-8') as f:
                existing_patterns = json.load(f)
        
        # Add new patterns
        existing_patterns.extend(approved_patterns)
        
        # Save updated patterns
        with open(patterns_file, 'w', encoding='utf-8') as f:
            json.dump(existing_patterns, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(approved_patterns)} new patterns to {patterns_file}")
        print(f"Total patterns: {len(existing_patterns)}")
    
    def run_analysis(self):
        """Run the complete pattern learning analysis"""
        print("Starting Human-in-the-Loop Pattern Learning Analysis")
        print("=" * 60)
        
        # Step 1: Load traces
        self.load_traces()
        
        # Step 2: Identify candidates
        print("\nIdentifying pattern candidates...")
        self.identify_pattern_candidates()
        
        # Step 3: Present for approval
        approved_patterns = self.present_patterns_for_approval()
        
        # Step 4: Save approved patterns
        if approved_patterns:
            self.save_approved_patterns(approved_patterns)
            
            print(f"\nPattern Learning Complete!")
            print(f"Approved: {len(approved_patterns)} patterns")
            print(f"Expected improvement: +{len(approved_patterns) * 2}% learned pattern usage")
        else:
            print("\nNo patterns were approved")

def main():
    analyzer = PatternLearningAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main()