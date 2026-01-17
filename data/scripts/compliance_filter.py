#!/usr/bin/env python3
"""
Legal compliance filter for data scraping
Ensures all collected data is from public records and contains no restricted content
"""
from typing import List, Dict, Optional
import re


# Keywords that indicate restricted or classified information
RESTRICTED_KEYWORDS = [
    # Classification levels
    "classified", "secret", "top secret", "sci", "sar", "sci/fgi",
    "confidential", "controlled unclassified information", "cui",
    
    # Atomic Energy Act restrictions
    "restricted data", "formerly restricted data", "rd", "frd",
    "nuclear weapon design", "critical nuclear weapon design",
    "nuclear weapons", "atomic energy", "atomic secrets",
    
    # Export control
    "itar", "ear", "export controlled", "munitions list",
    
    # Intelligence sources and methods
    "sigint", "humint", "osint", "geoint", "masint",
    "sources and methods", "intelligence sources",
    "special access program", "sap", "compartment",
    "need to know", "codeword", "sci compartment",
    
    # Personnel/PII
    "personnel record", "social security number", "ssn",
    "personally identifiable information", "pii",
    
    # Ongoing investigations
    "ongoing investigation", "active investigation",
    "grand jury", "under investigation",
    
    # Operational security
    "operational security", "opsec", "tactics techniques procedures",
    "ttp", "force protection", "security posture",
]


def compliance_check(text: str, strict: bool = True) -> tuple[bool, List[str]]:
    """
    Check if text appears to contain restricted content
    
    Args:
        text: Text to check
        strict: If True, any match fails. If False, only multiple matches fail.
    
    Returns:
        Tuple of (is_compliant, list_of_restricted_keywords_found)
    """
    if not text:
        return True, []
    
    text_lower = text.lower()
    found_keywords = []
    
    for keyword in RESTRICTED_KEYWORDS:
        # Use word boundaries for better matching
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_keywords.append(keyword)
    
    if strict:
        is_compliant = len(found_keywords) == 0
    else:
        # Allow 1-2 matches (might be in context like "declassified" or "unclassified")
        is_compliant = len(found_keywords) <= 2
    
    return is_compliant, found_keywords


def filter_data_record(record: Dict, text_fields: List[str] = None) -> tuple[bool, Optional[str]]:
    """
    Filter a data record for compliance
    
    Args:
        record: Dictionary with data fields
        text_fields: List of field names to check (if None, checks all string values)
    
    Returns:
        Tuple of (is_compliant, reason_if_not_compliant)
    """
    if text_fields is None:
        # Check all string fields
        text_fields = [k for k, v in record.items() if isinstance(v, str)]
    
    for field in text_fields:
        if field in record and record[field]:
            is_compliant, keywords = compliance_check(str(record[field]))
            if not is_compliant:
                return False, f"Restricted keywords in {field}: {', '.join(keywords)}"
    
    return True, None


def is_public_source(url: str) -> bool:
    """
    Check if URL is from a known public source
    
    Args:
        url: URL to check
    
    Returns:
        True if URL is from a known public source
    """
    if not url:
        return False
    
    url_lower = url.lower()
    
    # Known public government sources
    public_domains = [
        '.gov', '.mil',
        'usaspending.gov',
        'sam.gov',
        'sec.gov',
        'fpds.gov',
        'congress.gov',
        'gao.gov',
        'courtlistener.com',  # RECAP (public court records)
        'pacer.gov',  # Public Access to Court Electronic Records
        'prnewswire.com',  # Press releases
        'businesswire.com',
        'globenewswire.com',
    ]
    
    return any(domain in url_lower for domain in public_domains)


def validate_record_for_storage(record: Dict) -> Dict[str, any]:
    """
    Validate and filter a record before storage
    
    Args:
        record: Dictionary with data fields
    
    Returns:
        Dictionary with validation results:
        - valid: bool
        - errors: List[str]
        - warnings: List[str]
        - filtered_record: Dict (None if invalid)
    """
    errors = []
    warnings = []
    
    # Check compliance
    is_compliant, reason = filter_data_record(record)
    if not is_compliant:
        errors.append(f"Compliance check failed: {reason}")
        return {
            'valid': False,
            'errors': errors,
            'warnings': warnings,
            'filtered_record': None
        }
    
    # Check source URL
    if 'source_citation' in record:
        if not is_public_source(record['source_citation']):
            warnings.append(f"Source URL may not be public: {record['source_citation']}")
    
    # Remove any None or empty fields that might cause issues
    filtered_record = {k: v for k, v in record.items() if v is not None and v != ''}
    
    return {
        'valid': True,
        'errors': errors,
        'warnings': warnings,
        'filtered_record': filtered_record
    }
