"""
Query Validation Layer - Prevents invalid Cypher from reaching Neo4j
"""

import re
from typing import Tuple, List

class CypherValidator:
    def __init__(self):
        self.common_fixes = {
            # Fix trailing commas
            r'RETURN\s+([^,\n]+),\s*$': r'RETURN \1',
            r'RETURN\s+([^,\n]+),\s*\n': r'RETURN \1\n',
            
            # Fix incomplete RETURN statements
            r'RETURN\s+[^,\n]+,\s*$': lambda m: m.group(0).rstrip(',').strip(),
            
            # Fix variable consistency issues
            r'collect\([^)]+\)\s+as\s+(\w+).*?RETURN[^,]+,\s*(\w+)': self._fix_variable_mismatch,
        }
    
    def validate_and_fix(self, cypher: str) -> Tuple[bool, str, List[str]]:
        """
        Validate Cypher query and attempt auto-fixes
        Returns: (is_valid, fixed_query, issues_found)
        """
        issues = []
        fixed_query = cypher.strip()
        
        # Check for basic syntax issues
        if self._has_trailing_comma(fixed_query):
            issues.append("Trailing comma in RETURN statement")
            fixed_query = self._fix_trailing_comma(fixed_query)
        
        if self._has_incomplete_return(fixed_query):
            issues.append("Incomplete RETURN statement")
            fixed_query = self._fix_incomplete_return(fixed_query)
        
        if self._has_variable_mismatch(fixed_query):
            issues.append("Variable name mismatch")
            fixed_query = self._fix_variable_names(fixed_query)
        
        # Check for forbidden patterns
        if 'apoc.' in fixed_query.lower():
            issues.append("APOC functions not available")
            return False, fixed_query, issues
        
        if 'LOCATED_IN' in fixed_query and 'Client' in fixed_query:
            issues.append("Client LOCATED_IN relationship doesn't exist")
            fixed_query = self._fix_location_pattern(fixed_query)
        
        if 'YEAR(' in fixed_query:
            issues.append("YEAR() function not available - using substring()")
            fixed_query = re.sub(r'YEAR\(([^)]+)\)', r'substring(\1, 0, 4)', fixed_query)
        
        if 'extract(' in fixed_query.lower():
            issues.append("extract() function not available - using substring()")
            fixed_query = re.sub(r'extract\(\s*year\s+FROM\s+date\(([^)]+)\)\s*\)', r'substring(\1, 0, 4)', fixed_query, flags=re.IGNORECASE)
        
        # Basic structure validation
        if not self._has_valid_structure(fixed_query):
            issues.append("Invalid query structure")
            return False, fixed_query, issues
        
        # Always return valid=True after fixes, let Neo4j be the final judge
        # Only return False for APOC functions which we know won't work
        has_blocking_issue = any('not available' in issue.lower() for issue in issues)
        return not has_blocking_issue, fixed_query, issues
    
    def _has_trailing_comma(self, query: str) -> bool:
        """Check for trailing commas in RETURN and WITH statements"""
        return bool(re.search(r'(RETURN|WITH)\s+[^,\n]+,\s*$', query, re.MULTILINE))
    
    def _fix_trailing_comma(self, query: str) -> str:
        """Remove trailing commas from RETURN and WITH statements"""
        # Fix RETURN trailing commas
        query = re.sub(r'(RETURN\s+[^,\n]+),\s*$', r'\1', query, flags=re.MULTILINE)
        # Fix WITH trailing commas
        query = re.sub(r'(WITH\s+[^,\n]+),\s*\n', r'\1\n', query, flags=re.MULTILINE)
        return query
    
    def _has_incomplete_return(self, query: str) -> bool:
        """Check for incomplete RETURN statements"""
        return bool(re.search(r'RETURN\s+[^,\n]+,\s*$', query))
    
    def _fix_incomplete_return(self, query: str) -> str:
        """Fix incomplete RETURN statements by removing trailing comma"""
        return re.sub(r'(RETURN\s+[^,\n]+),\s*$', r'\1', query)
    
    def _has_variable_mismatch(self, query: str) -> bool:
        """Check for variable name mismatches between collection and return"""
        collect_match = re.search(r'collect\([^)]+\)\s+as\s+(\w+)', query)
        if not collect_match:
            return False
        
        collected_var = collect_match.group(1)
        return_match = re.search(r'RETURN[^,]+,\s*(\w+)', query)
        if return_match:
            return_var = return_match.group(1)
            return collected_var != return_var
        return False
    
    def _fix_variable_names(self, query: str) -> str:
        """Fix variable name mismatches"""
        collect_match = re.search(r'collect\([^)]+\)\s+as\s+(\w+)', query)
        if collect_match:
            collected_var = collect_match.group(1)
            # Replace mismatched variable in RETURN
            query = re.sub(r'(RETURN[^,]+,\s*)\w+(\s*$)', rf'\1{collected_var}\2', query)
        return query
    
    def _fix_location_pattern(self, query: str) -> str:
        """Fix Client LOCATED_IN patterns to use direct region property"""
        # Replace Client LOCATED_IN with direct region property
        pattern = r'MATCH\s+\(c:Client\)-\[:LOCATED_IN\]->\(r:Region\)\s+WHERE\s+r\.name\s*=\s*[\'"]([^\'"]+)[\'"]'
        replacement = r"MATCH (c:Client) WHERE c.region = '\1'"
        return re.sub(pattern, replacement, query)
    
    def _has_valid_structure(self, query: str) -> bool:
        """Basic structure validation"""
        query_upper = query.upper()
        
        # Must have MATCH
        if 'MATCH' not in query_upper:
            return False
        
        # Must have RETURN
        if 'RETURN' not in query_upper:
            return False
        
        # Check for balanced parentheses
        open_count = query.count('(')
        close_count = query.count(')')
        if open_count != close_count:
            return False
        
        return True
    
    def _fix_variable_mismatch(self, match):
        """Helper for regex replacement of variable mismatches"""
        return match.group(0).replace(match.group(2), match.group(1))