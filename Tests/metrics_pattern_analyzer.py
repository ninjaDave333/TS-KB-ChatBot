#!/usr/bin/env python3
"""
Enhanced Pattern Learning from Production Metrics
Uses the rich production_metrics.json data for better pattern identification
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
import re

class MetricsPatternAnalyzer:
    def __init__(self):
        self.metrics_file = Path("data/production_metrics.json")
        self.metrics = {}
        self.patterns = []
        
    def load_metrics(self):
        with open(self.metrics_file, 'r', encoding='utf-8') as f:
            self.metrics = json.load(f)
        
        queries = self.metrics.get('query_history', [])
        print(f"Loaded {len(queries)} queries from production metrics")
        return queries
    
    def find_successful_patterns(self, queries):
        # Group successful queries by intent and Cypher
        successful = [q for q in queries if q.get('success', False) and q.get('cypher')]
        
        print(f"Found {len(successful)} successful queries with Cypher")
        
        # Group by Cypher query (exact matches)
        cypher_groups = defaultdict(list)
        for q in successful:
            cypher = q['cypher'].strip()
            cypher_groups[cypher].append(q)
        
        # Find patterns (Cypher used 1+ times, excluding already learned)
        learned_file = Path("data/learned_patterns.json")
        learned_cyphers = set()
        if learned_file.exists():
            with open(learned_file, 'r', encoding='utf-8') as f:
                learned = json.load(f)
                learned_cyphers = {p['cypher_template'].strip() for p in learned}
        
        patterns = []
        for cypher, group in cypher_groups.items():
            if cypher not in learned_cyphers and len(group) >= 1:
                pattern = self.create_pattern(group, cypher)
                if pattern:
                    patterns.append(pattern)
        
        print(f"Found {len(patterns)} potential learned patterns")
        return patterns
    
    def create_pattern(self, queries, cypher):
        # Extract pattern details
        questions = [q['query'] for q in queries]
        intents = [q['intent'] for q in queries]
        answers = [q['answer'] for q in queries if q.get('answer')]
        
        # Find common intent
        intent_counts = Counter(intents)
        primary_intent = intent_counts.most_common(1)[0][0]
        
        # Classify pattern type
        pattern_type = self.classify_pattern(cypher, questions[0])
        
        # Find trigger keywords
        keywords = self.extract_keywords(questions)
        
        return {
            'id': f"pattern_{len(self.patterns)}",
            'intent': primary_intent,
            'pattern_type': pattern_type,
            'cypher_template': cypher,
            'trigger_keywords': keywords,
            'example_questions': questions[:3],
            'usage_count': len(queries),
            'confidence': min(1.0, len(queries) / 5.0),
            'sample_answer': answers[0] if answers else "No answer available"
        }
    
    def classify_pattern(self, cypher, question):
        cypher_lower = cypher.lower()
        question_lower = question.lower()
        
        if 'count(' in cypher_lower:
            return 'count_query'
        elif 'top' in question_lower and 'limit' in cypher_lower:
            return 'top_ranking'
        elif 'list' in question_lower:
            return 'list_query'
        elif 'who is' in question_lower or 'who are' in question_lower:
            return 'who_query'
        elif 'what is' in question_lower or 'what are' in question_lower:
            return 'what_query'
        elif 'sum(' in cypher_lower or 'avg(' in cypher_lower:
            return 'aggregation'
        else:
            return 'general_query'
    
    def extract_keywords(self, questions):
        # Combine all questions and extract common words
        all_text = ' '.join(questions).lower()
        words = re.findall(r'\b\w+\b', all_text)
        
        # Count word frequency
        word_counts = Counter(words)
        
        # Filter out stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'what', 'how', 'who', 'when', 'where', 'why', 'do', 'does', 'did', 'can', 'could', 'would', 'should', 'will', 'have', 'has', 'had'}
        
        # Get meaningful keywords that appear in multiple questions
        threshold = max(1, len(questions) // 2)
        keywords = []
        for word, count in word_counts.most_common():
            if (word not in stop_words and 
                len(word) > 2 and 
                count >= threshold and 
                len(keywords) < 5):
                keywords.append(word)
        
        return keywords
    
    def review_patterns(self, patterns):
        if not patterns:
            print("No patterns found to review")
            return []
        
        approved = []
        print(f"\nReviewing {len(patterns)} potential patterns:")
        print("=" * 60)
        
        for i, pattern in enumerate(patterns, 1):
            print(f"\nPATTERN #{i}: {pattern['id']}")
            print(f"Intent: {pattern['intent']}")
            print(f"Type: {pattern['pattern_type']}")
            print(f"Usage: {pattern['usage_count']} times")
            print(f"Confidence: {pattern['confidence']:.2f}")
            
            if pattern['trigger_keywords']:
                print(f"Keywords: {', '.join(pattern['trigger_keywords'])}")
            
            print("\nExample Questions:")
            for j, q in enumerate(pattern['example_questions'], 1):
                print(f"  {j}. {q}")
            
            print(f"\n{'='*60}")
            print("FULL CYPHER QUERY (This is what will be reused):")
            print(f"{'='*60}")
            print(pattern['cypher_template'])
            print(f"{'='*60}")
            
            print(f"\nFULL SAMPLE ANSWER:")
            print(f"{'-'*60}")
            print(pattern['sample_answer'])
            print(f"{'-'*60}")
            
            print("\n" + "-" * 50)
            
            # Get user approval
            while True:
                choice = input("Approve this pattern? (y/n/e=edit/s=skip): ").lower().strip()
                if choice in ['y', 'yes']:
                    approved.append(pattern)
                    print("✓ Pattern approved!")
                    break
                elif choice in ['e', 'edit']:
                    print("\nEnter the corrected Cypher query (paste entire query, then type END on a new line):")
                    lines = []
                    while True:
                        line = input()
                        if line.strip().upper() == 'END':
                            break
                        lines.append(line)
                    
                    corrected_cypher = '\n'.join(lines).strip()
                    if corrected_cypher:
                        pattern['cypher_template'] = corrected_cypher
                        pattern['manually_corrected'] = True
                        approved.append(pattern)
                        print("✓ Pattern approved with corrections!")
                        break
                    else:
                        print("Edit cancelled")
                elif choice in ['n', 'no']:
                    print("✗ Pattern rejected")
                    break
                elif choice in ['s', 'skip']:
                    print("→ Pattern skipped")
                    break
                else:
                    print("Please enter 'y' (yes), 'n' (no), 'e' (edit), or 's' (skip)")
        
        return approved
    
    def save_patterns(self, patterns):
        if not patterns:
            print("No patterns to save")
            return
        
        file_path = Path("data/learned_patterns.json")
        
        # Load existing patterns
        existing = []
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        
        # Add new patterns
        existing.extend(patterns)
        
        # Save updated patterns
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Saved {len(patterns)} new patterns")
        print(f"📊 Total patterns: {len(existing)}")
        
        # Show expected impact
        total_usage = sum(p['usage_count'] for p in patterns)
        print(f"🚀 Expected impact: +{total_usage} queries can now use learned patterns")
        print(f"📈 Estimated speed improvement: {total_usage * 2}s saved per day")
    
    def run_analysis(self):
        print("Enhanced Pattern Learning from Production Metrics")
        print("=" * 55)
        
        # Load production metrics
        queries = self.load_metrics()
        
        if not queries:
            print("No query data found")
            return
        
        # Find successful patterns
        patterns = self.find_successful_patterns(queries)
        
        if not patterns:
            print("No reusable patterns found")
            return
        
        # Review patterns with user
        approved = self.review_patterns(patterns)
        
        # Save approved patterns
        if approved:
            self.save_patterns(approved)
            print(f"\n🎉 Pattern learning complete!")
            print(f"✅ {len(approved)} patterns approved and saved")
        else:
            print("\n⚠️ No patterns were approved")

def main():
    analyzer = MetricsPatternAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main()