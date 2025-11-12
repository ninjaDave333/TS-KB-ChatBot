#!/usr/bin/env python3

import re

test_queries = [
    "how many successful deals were conducted during 2025, show 5 examples",
    "list 5 clients in israel with their account managers",
    "how many hashicorp products were purchased in 2025"
]

for query in test_queries:
    print(f"\nQuery: {query}")
    
    # Test year extraction
    year_match = re.search(r'\b(20\d{2})\b', query)
    print(f"  Year: {year_match.group(1) if year_match else 'NOT FOUND'}")
    
    # Test vendor extraction
    vendor_match = re.search(r'\b(hashicorp|aws|microsoft|google|vmware)\b', query, re.IGNORECASE)
    print(f"  Vendor: {vendor_match.group(1) if vendor_match else 'NOT FOUND'}")
    
    # Build filters
    filters = []
    if year_match:
        filters.append(f"o.purchased_date CONTAINS '{year_match.group(1)}'")
    if vendor_match:
        vendor = vendor_match.group(1).lower()
        filters.append(f"toLower(p.name) CONTAINS '{vendor}'")
    
    print(f"  Filters: {' AND '.join(filters) if filters else 'NONE'}")
