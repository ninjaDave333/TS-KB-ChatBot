#!/usr/bin/env python3
"""
Test what the correct Cypher query should be for prompt security deals
"""

# The user asked: "list top 3 biggest prompt security deals"
# But the system generated a query that:
# 1. Searches for 'prompt security' in product names (may not exist)
# 2. Doesn't filter by any year range
# 3. Only found 1 result from 2026

# The correct approach should be:
# 1. Search for security-related products more broadly
# 2. If user doesn't specify year, use recent years (2023-2025)
# 3. Provide helpful suggestions if no exact matches

print("ISSUE ANALYSIS:")
print("================")
print("User query: 'list top 3 biggest prompt security deals'")
print()
print("Generated query searched for:")
print("- toLower(p.name) CONTAINS 'prompt security'")
print("- No year filtering")
print("- Found 1 result from 2026")
print()
print("PROBLEMS:")
print("1. 'prompt security' may not be an exact product name")
print("2. No year filtering means it searches all years")
print("3. Should suggest broader security terms")
print()
print("BETTER APPROACH:")
print("1. Search for 'security' in product names")
print("2. Add default year range (2023-2025) if not specified")
print("3. Provide suggestions if no results")