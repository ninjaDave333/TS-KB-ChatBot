"""
Learned Pattern Matcher - Apply approved patterns from metrics_pattern_analyzer
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any

class LearnedPatternMatcher:
    def __init__(self):
        self.patterns_file = Path("ref_data/learned_patterns.json")
        self.patterns = []
        self.load_patterns()
    
    def load_patterns(self):
        if self.patterns_file.exists():
            with open(self.patterns_file, 'r', encoding='utf-8') as f:
                self.patterns = json.load(f)
            print(f"Loaded {len(self.patterns)} learned patterns")
    
    def match_pattern(self, question: str, intent: str) -> Optional[Dict[str, Any]]:
        """Match question to learned pattern"""
        question_lower = question.lower()
        
        for pattern in self.patterns:
            # Match intent
            if pattern['intent'] != intent:
                continue
            
            # Match keywords
            keywords = pattern.get('trigger_keywords', [])
            if keywords and any(kw in question_lower for kw in keywords):
                return pattern
        
        return None
    
    def get_cypher(self, pattern: Dict[str, Any]) -> str:
        """Get Cypher template from pattern"""
        return pattern['cypher_template']
