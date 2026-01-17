#!/usr/bin/env python3
"""
Amount extraction utilities for financial flows
"""
import re
from typing import Optional


def extract_amount(text: str) -> Optional[float]:
    """
    Extract dollar amount from text
    Returns amount in USD or None
    """
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Expanded amount patterns
    amount_patterns = [
        # Standard formats: $100 million, $1.5B
        (r'\$(\d+\.?\d*)\s*(?:million|billion|M|B)', True),
        (r'(\d+\.?\d*)\s*(?:million|billion|M|B)\s*(?:dollar|USD)', True),
        (r'\$(\d{1,3}(?:,\d{3})*(?:\.\d+)?)', False),
        
        # Written formats: valued at $X, worth $X, for $X
        (r'valued\s*at\s*\$?(\d+\.?\d*)\s*(?:million|billion|M|B)?', True),
        (r'worth\s*\$?(\d+\.?\d*)\s*(?:million|billion|M|B)?', True),
        (r'for\s*\$?(\d+\.?\d*)\s*(?:million|billion|M|B)?', True),
        (r'deal\s*(?:worth|valued|for)?\s*\$?(\d+\.?\d*)\s*(?:million|billion|M|B)?', True),
        
        # Contract values: contract value $X, awarded $X
        (r'contract\s*(?:value|worth)?\s*\$?(\d+\.?\d*)\s*(?:million|billion|M|B)?', True),
        (r'award(?:ed)?\s*\$?(\d+\.?\d*)\s*(?:million|billion|M|B)?', True),
        (r'contract\s*(?:of|for|worth)?\s*\$?(\d+\.?\d*)\s*(?:million|billion|M|B)?', True),
        
        # Transaction values: transaction worth $X
        (r'transaction\s*(?:worth|valued|for)?\s*\$?(\d+\.?\d*)\s*(?:million|billion|M|B)?', True),
        (r'acquisition\s*(?:worth|valued|for)?\s*\$?(\d+\.?\d*)\s*(?:million|billion|M|B)?', True),
        (r'merger\s*(?:worth|valued|for)?\s*\$?(\d+\.?\d*)\s*(?:million|billion|M|B)?', True),
    ]
    
    for pattern, has_multiplier in amount_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                value = float(match.group(1).replace(',', ''))
                
                # Apply multiplier if needed
                if has_multiplier:
                    if 'billion' in text_lower or 'B' in text.upper():
                        value *= 1_000_000_000
                    elif 'million' in text_lower or 'M' in text.upper():
                        value *= 1_000_000
                
                # Sanity check: amounts should be reasonable
                if 1_000 <= value <= 10_000_000_000_000:  # $1K to $10T
                    return value
            except (ValueError, AttributeError):
                continue
    
    # Try to extract range and return average
    range_match = re.search(r'\$?(\d+\.?\d*)\s*[-–—]\s*\$?(\d+\.?\d*)\s*(?:million|billion|M|B)?', text, re.IGNORECASE)
    if range_match:
        try:
            val1 = float(range_match.group(1).replace(',', ''))
            val2 = float(range_match.group(2).replace(',', ''))
            
            if 'billion' in text_lower or 'B' in text.upper():
                val1 *= 1_000_000_000
                val2 *= 1_000_000_000
            elif 'million' in text_lower or 'M' in text.upper():
                val1 *= 1_000_000
                val2 *= 1_000_000
            
            avg = (val1 + val2) / 2
            if 1_000 <= avg <= 10_000_000_000_000:
                return avg
        except (ValueError, AttributeError):
            pass
    
    return None
