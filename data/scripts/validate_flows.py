#!/usr/bin/env python3
"""
Validation utilities for financial flows
"""
import re
from typing import Dict, List, Optional
from rapidfuzz import fuzz


def calculate_specificity_score(result: Dict) -> int:
    """
    Calculate specificity score for search result
    Higher score = more specific transaction, lower = generic list page
    """
    score = 0
    text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()
    url = result.get('url', '').lower()
    
    # Positive indicators (specific transaction)
    if re.search(r'\$\d+', text): score += 2  # Has amount
    if re.search(r'\d{4}', text): score += 1  # Has year
    if 'announced' in text: score += 1
    if 'completed' in text: score += 1
    if 'signed' in text: score += 1
    if 'deal' in text and 'value' in text: score += 1
    if 'transaction' in text: score += 1
    
    # Negative indicators (generic page)
    if 'list of' in text: score -= 3
    if 'all acquisitions' in text: score -= 3
    if 'history of' in text: score -= 2
    if 'complete list' in text: score -= 3
    if 'all deals' in text: score -= 2
    if '/list' in url or '/all' in url: score -= 2
    if 'index' in url or 'category' in url: score -= 1
    
    return score


def validate_flow(flow: Dict, existing_flows: List[Dict] = None) -> Dict:
    """
    Validate a flow for quality and completeness
    Returns validation result with errors and warnings
    """
    import re
    errors = []
    warnings = []
    
    # Required fields
    if not flow.get('source'):
        errors.append("Missing source")
    
    # Allow Unknown target if we have amount or date (can be filled in later)
    if flow.get('target') == 'Unknown':
        if not flow.get('amount_usd') and not flow.get('start_date'):
            errors.append("Unknown target (and no amount/date)")
        else:
            warnings.append("Unknown target (has amount/date)")
    
    if not flow.get('source_citation'):
        warnings.append("No citation URL")
    
    # Quality checks
    if not flow.get('amount_usd'):
        warnings.append("No amount specified")
    if not flow.get('start_date'):
        warnings.append("No date specified")
    
    # Citation validation
    citation = flow.get('source_citation', '')
    if citation:
        if not (citation.startswith('http://') or citation.startswith('https://')):
            warnings.append("Invalid citation URL format")
    
    # Duplicate check
    if existing_flows:
        if is_duplicate(flow, existing_flows):
            errors.append("Duplicate flow")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'quality_score': _calculate_quality_score(flow, errors, warnings)
    }


def is_duplicate(flow: Dict, existing_flows: List[Dict]) -> bool:
    """Check if flow is a duplicate of existing flows"""
    source = flow.get('source', '').upper()
    target = flow.get('target', '').upper()
    relationship = flow.get('relationship', '').lower()
    
    for existing in existing_flows:
        existing_source = existing.get('source', '').upper()
        existing_target = existing.get('target', '').upper()
        existing_rel = existing.get('relationship', '').lower()
        
        # Exact match
        if (source == existing_source and 
            target == existing_target and 
            relationship == existing_rel):
            return True
        
        # Fuzzy match (high similarity)
        source_sim = fuzz.ratio(source, existing_source)
        target_sim = fuzz.ratio(target, existing_target)
        rel_sim = fuzz.ratio(relationship, existing_rel)
        
        if source_sim > 90 and target_sim > 90 and rel_sim > 80:
            return True
    
    return False


def get_source_credibility_score(source_url: str) -> float:
    """
    Calculate source credibility score based on URL/domain
    
    Returns:
        Credibility score (0.0-1.0)
    """
    if not source_url:
        return 0.3  # Unknown source = low credibility
    
    url_lower = source_url.lower()
    
    # Tier 1: Highest credibility (0.9-1.0)
    # Official government sources
    tier1_domains = [
        'usaspending.gov', 'sam.gov', 'sec.gov', 'fpds.gov',
        'congress.gov', 'gao.gov', 'courtlistener.com',
        'pacer.gov', '.gov', '.mil',
    ]
    
    # Tier 2: High credibility (0.7-0.9)
    # Official announcements and major news
    tier2_domains = [
        'prnewswire.com', 'businesswire.com', 'globenewswire.com',
        'reuters.com', 'bloomberg.com', 'wsj.com',
        'defensenews.com', 'federalnewsnetwork.com',
    ]
    
    # Tier 3: Medium credibility (0.5-0.7)
    # News outlets and aggregators
    tier3_domains = [
        'orangeslices.ai', 'crunchbase.com', 'tracxn.com',
    ]
    
    # Tier 4: Lower credibility (0.3-0.5)
    # General web search, unknown sources
    # Default for unknown sources
    
    # Check tiers in order
    if any(domain in url_lower for domain in tier1_domains):
        return 0.95
    elif any(domain in url_lower for domain in tier2_domains):
        return 0.80
    elif any(domain in url_lower for domain in tier3_domains):
        return 0.60
    else:
        return 0.40  # Unknown source


def _calculate_quality_score(flow: Dict, errors: List[str], warnings: List[str]) -> float:
    """
    Calculate overall quality score (0-1) with source credibility weighting
    
    Returns:
        Weighted quality score (0.0-1.0)
    """
    base_score = 1.0
    
    # Deduct for errors
    base_score -= len(errors) * 0.3
    
    # Deduct for warnings
    base_score -= len(warnings) * 0.1
    
    # Bonus for complete data
    if flow.get('amount_usd'):
        base_score += 0.1
    if flow.get('start_date'):
        base_score += 0.1
    if flow.get('source_citation'):
        base_score += 0.1
    
    base_score = max(0.0, min(1.0, base_score))
    
    # Apply source credibility weighting
    source_credibility = get_source_credibility_score(flow.get('source_citation', ''))
    
    # Weighted average: 70% base score + 30% source credibility
    weighted_score = (base_score * 0.7) + (source_credibility * 0.3)
    
    return max(0.0, min(1.0, weighted_score))
