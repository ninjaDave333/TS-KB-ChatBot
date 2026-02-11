#!/usr/bin/env python3
"""
Pattern Learning Analyzer - Human-in-the-Loop
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
import re

class PatternAnalyzer:
    def __init__(self):
        self.traces_file = Path("ref_data/traces.jsonl")
        self.traces = []
        self.patterns = []
        
    def load_traces(self):
        with open(self.traces_file, 'r', encoding='utf-8') as f:
            self.traces = [json.loads(line) for line in f if line.strip()]
        print(f"Loaded {len(self.traces)} traces")
    
    def find_patterns(self):
        # Find successful AI-generated queries
        successful = []
        for trace in self.traces:
            if (trace.get('neo4j_result_summary', {}).get('has_data', False) and 
                trace.get('cypher_query') and 
                trace.get('routing_path') == 'ai_generated'):
                
                question = self.extract_question(trace.get('prompt_user', ''))
                successful.append({
                    'question': question,
                    'intent': trace.get('intent', ''),
                    'cypher': trace.get('cypher_query', ''),
                    'answer': trace.get('final_answer', '')
                })
        
        print(f"Found {len(successful)} successful queries")
        
        # Group by exact Cypher
        cypher_groups = defaultdict(list)
        for q in successful:
            cypher_groups[q['cypher']].append(q)
        
        # Find patterns (Cypher used 2+ times)
        for cypher, queries in cypher_groups.items():
            if len(queries) >= 2:
                pattern = {
                    'id': f"pattern_{len(self.patterns)}",
                    'intent': queries[0]['intent'],
                    'cypher': cypher,
                    'questions': [q['question'] for q in queries],
                    'usage_count': len(queries),
                    'keywords': self.find_keywords([q['question'] for q in queries]),
                    'sample_answer': queries[0]['answer']
                }
                self.patterns.append(pattern)
        
        print(f"Found {len(self.patterns)} potential patterns")
    
    def extract_question(self, prompt_user):
        if not prompt_user:
            return "Unknown"
        
        # Look for "Generate Cypher for: [question]"
        match = re.search(r'Generate Cypher for: (.+?)\\n', prompt_user)
        if match:
            return match.group(1).strip()
        
        # Look for other patterns
        match = re.search(r'question into a Cypher query:\\n\\n(.+?)\\n', prompt_user)
        if match:
            return match.group(1).strip()
        
        return "Unknown"
    
    def find_keywords(self, questions):
        words = []
        for q in questions:
            words.extend(re.findall(r'\\b\\w+\\b', q.lower()))
        
        word_counts = Counter(words)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'what', 'how', 'who'}
        
        keywords = []
        for word, count in word_counts.most_common():
            if word not in stop_words and len(word) > 2 and count >= 2:
                keywords.append(word)
        
        return keywords[:3]
    
    def review_patterns(self):
        if not self.patterns:
            print("No patterns found")
            return []
        
        approved = []
        print(f"\\nReviewing {len(self.patterns)} patterns:")
        print("=" * 50)
        
        for i, pattern in enumerate(self.patterns, 1):
            print(f"\\nPATTERN #{i}")
            print(f"Intent: {pattern['intent']}")
            print(f"Used: {pattern['usage_count']} times")
            print(f"Keywords: {', '.join(pattern['keywords'])}")
            
            print("\\nQuestions:")
            for j, q in enumerate(pattern['questions'][:3], 1):
                print(f"  {j}. {q}")
            
            print(f"\\nCypher: {pattern['cypher'][:80]}...")
            print(f"Answer: {pattern['sample_answer'][:60]}...")
            
            while True:
                choice = input("\\nApprove? (y/n/s=skip): ").lower()
                if choice in ['y', 'yes']:
                    approved.append(pattern)
                    print("Approved!")
                    break
                elif choice in ['n', 'no']:
                    print("Rejected")
                    break
                elif choice in ['s', 'skip']:
                    print("Skipped")
                    break
        
        return approved
    
    def save_patterns(self, patterns):
        if not patterns:
            print("No patterns to save")
            return
        
        file_path = Path("ref_data/learned_patterns.json")
        
        existing = []
        if file_path.exists():
            with open(file_path, 'r') as f:
                existing = json.load(f)
        
        existing.extend(patterns)
        
        with open(file_path, 'w') as f:
            json.dump(existing, f, indent=2)
        
        print(f"Saved {len(patterns)} patterns")
        print(f"Total: {len(existing)} patterns")
    
    def run(self):
        print("Pattern Learning Analysis")
        print("=" * 30)
        
        self.load_traces()
        self.find_patterns()
        approved = self.review_patterns()
        
        if approved:
            self.save_patterns(approved)
            print(f"\\nComplete! Approved {len(approved)} patterns")
        else:
            print("\\nNo patterns approved")

if __name__ == "__main__":
    analyzer = PatternAnalyzer()
    analyzer.run()