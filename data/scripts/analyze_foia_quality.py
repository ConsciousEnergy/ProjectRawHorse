#!/usr/bin/env python3
"""
Analyze and weight FOIA targets based on:
- Specificity: How specific is the request? (specific records, dates, programs)
- Likelihood: Probability of getting a response (agency, timeframe, classification level)
- Priority: Overall importance for research
"""
import csv
import re
import sys
from pathlib import Path
from typing import Dict, Tuple

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
FOIA_CSV = PROJECT_ROOT / "data" / "foia" / "uap_gerb_transcript_foia_targets.csv"

# Agency response likelihood scores (based on historical FOIA response rates)
AGENCY_LIKELIHOOD = {
    'NRO': 0.3,  # Very low - highly classified
    'CIA': 0.2,  # Very low - highly classified
    'CIA DS&T': 0.2,
    'DOE': 0.4,  # Low - nuclear classification
    'DOE OICI': 0.3,
    'DOE NEST': 0.3,
    'DARPA': 0.5,  # Medium
    'DARPA SID': 0.4,
    'DHS': 0.6,  # Medium-high
    'DCSA': 0.5,
    'DoD': 0.5,
    'AARO': 0.7,  # High - public-facing office
    'GSA': 0.8,  # High - public records
    'NGA': 0.4,
    'US Army': 0.5,
    'Sandia National Laboratories': 0.4,
    'Oak Ridge National Laboratory': 0.4,
    'MITER Corporation': 0.3,  # FFRDC - low transparency
    'Edwards 412 Test Wing': 0.3,
    'OUSD': 0.4,
    'DDNI ATNF': 0.3,
}

# Specificity indicators (higher score = more specific)
SPECIFICITY_INDICATORS = {
    'specific dates': 0.3,  # "1949-1951", "2010"
    'specific programs': 0.3,  # "Program B", "Kona Blue", "Project Twinkle"
    'specific records': 0.2,  # "decision memos", "contracts", "testimony"
    'specific amounts': 0.1,  # "$3.2 billion"
    'specific personnel': 0.1,  # Named individuals
}

# Priority indicators (higher score = more important)
PRIORITY_INDICATORS = {
    'direct connection': 0.3,  # "Direct connection to UFO legacy programs"
    'crash retrieval': 0.3,  # Crash retrieval operations
    'material transfer': 0.2,  # Technology/material transfer
    'classification': 0.1,  # Classification systems
    'funding': 0.1,  # Funding mechanisms
}


def calculate_specificity_score(record_request: str, timeframe: str, notes: str) -> Tuple[float, str]:
    """Calculate specificity score (0-1)"""
    score = 0.0
    notes_list = []
    
    text = f"{record_request} {timeframe} {notes}".lower()
    
    # Check for specific dates
    if re.search(r'\b(19|20)\d{2}\b', timeframe or ''):
        score += SPECIFICITY_INDICATORS['specific dates']
        notes_list.append("Has specific date range")
    
    # Check for specific programs
    program_keywords = ['program', 'project', 'operation', 'initiative']
    if any(kw in text for kw in program_keywords):
        score += SPECIFICITY_INDICATORS['specific programs']
        notes_list.append("References specific programs/projects")
    
    # Check for specific record types
    record_keywords = ['memo', 'contract', 'testimony', 'record', 'document', 'report', 'log']
    if any(kw in text for kw in record_keywords):
        score += SPECIFICITY_INDICATORS['specific records']
        notes_list.append("Specifies record types")
    
    # Check for specific amounts
    if re.search(r'\$[\d.,]+\s*(billion|million|thousand)', text):
        score += SPECIFICITY_INDICATORS['specific amounts']
        notes_list.append("References specific dollar amounts")
    
    # Check for specific personnel
    if re.search(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', record_request):
        score += SPECIFICITY_INDICATORS['specific personnel']
        notes_list.append("References specific personnel")
    
    # Penalize vague requests
    vague_terms = ['related to', 'concerning', 'about', 'various', 'general']
    vague_count = sum(1 for term in vague_terms if term in text)
    if vague_count > 2:
        score *= 0.7  # Reduce score for vague requests
        notes_list.append("Contains vague language")
    
    # Cap at 1.0
    score = min(score, 1.0)
    
    return score, "; ".join(notes_list) if notes_list else "Standard specificity"


def calculate_likelihood_score(agency: str, timeframe: str, relevance: str) -> Tuple[float, str]:
    """Calculate likelihood of getting a response (0-1)"""
    base_score = AGENCY_LIKELIHOOD.get(agency, 0.5)  # Default to medium
    notes_list = []
    
    # Adjust based on timeframe
    if timeframe:
        # Older records (pre-2000) may be more likely to be released
        years = re.findall(r'\b(19|20)\d{2}\b', timeframe)
        if years:
            try:
                earliest_year = min([int(re.search(r'\b(19|20)\d{2}\b', timeframe).group()) for _ in [1]])
                if earliest_year < 2000:
                    base_score += 0.1  # Older records slightly more likely
                    notes_list.append("Older records may have better release rates")
                elif 'present' in timeframe.lower():
                    base_score -= 0.1  # Current records less likely
                    notes_list.append("Current/ongoing records less likely to be released")
            except:
                pass
    
    # Adjust based on classification level (from relevance/notes)
    relevance_lower = (relevance or '').lower()
    if any(term in relevance_lower for term in ['classified', 'sap', 'special access', 'legacy program']):
        base_score -= 0.2
        notes_list.append("High classification level reduces likelihood")
    elif 'public' in relevance_lower or 'declassified' in relevance_lower:
        base_score += 0.1
        notes_list.append("Public/declassified records more likely")
    
    # Cap at 1.0 and floor at 0.0
    score = max(0.0, min(1.0, base_score))
    
    return score, "; ".join(notes_list) if notes_list else "Standard likelihood"


def calculate_priority_score(relevance: str, notes: str) -> Tuple[float, str]:
    """Calculate priority/importance score (0-1)"""
    score = 0.0
    notes_list = []
    
    text = f"{relevance} {notes}".lower()
    
    # Check for priority indicators
    if 'direct connection' in text:
        score += PRIORITY_INDICATORS['direct connection']
        notes_list.append("Direct connection to legacy programs")
    
    if 'crash retrieval' in text:
        score += PRIORITY_INDICATORS['crash retrieval']
        notes_list.append("Crash retrieval operations")
    
    if 'material transfer' in text or 'technology transfer' in text:
        score += PRIORITY_INDICATORS['material transfer']
        notes_list.append("Material/technology transfer")
    
    if 'classification' in text:
        score += PRIORITY_INDICATORS['classification']
        notes_list.append("Classification systems")
    
    if 'funding' in text or 'misappropriation' in text:
        score += PRIORITY_INDICATORS['funding']
        notes_list.append("Funding mechanisms")
    
    # Boost for verified/testimony-based requests
    if 'testimony' in text or 'verified' in text or 'mentioned in' in text:
        score += 0.1
        notes_list.append("Based on testimony/verified sources")
    
    # Cap at 1.0
    score = min(score, 1.0)
    
    return score, "; ".join(notes_list) if notes_list else "Standard priority"


def analyze_foia_targets(csv_path: Path) -> None:
    """Analyze FOIA targets and add quality scores"""
    if not csv_path.exists():
        print(f"ERROR: FOIA targets file not found: {csv_path}")
        return
    
    results = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            agency = row.get('agency', '').strip()
            record_request = row.get('record_request', '').strip()
            timeframe = row.get('timeframe', '').strip()
            relevance = row.get('relevance', '').strip()
            notes = row.get('notes', '').strip()
            
            # Calculate scores
            specificity, spec_notes = calculate_specificity_score(record_request, timeframe, notes)
            likelihood, like_notes = calculate_likelihood_score(agency, timeframe, relevance)
            priority, pri_notes = calculate_priority_score(relevance, notes)
            
            # Combine quality notes
            quality_notes = f"Specificity: {spec_notes} | Likelihood: {like_notes} | Priority: {pri_notes}"
            
            results.append({
                'agency': agency,
                'record_request': record_request,
                'timeframe': timeframe,
                'relevance': relevance,
                'notes': notes,
                'specificity_score': round(specificity, 2),
                'likelihood_score': round(likelihood, 2),
                'priority_score': round(priority, 2),
                'quality_notes': quality_notes
            })
    
    # Print summary
    print("=" * 70)
    print("FOIA Target Quality Analysis")
    print("=" * 70)
    print(f"\nTotal FOIA Targets: {len(results)}")
    
    # Sort by priority score
    results_sorted = sorted(results, key=lambda x: x['priority_score'], reverse=True)
    
    print("\n" + "=" * 70)
    print("Top 10 Priority FOIA Targets:")
    print("=" * 70)
    for i, result in enumerate(results_sorted[:10], 1):
        print(f"\n{i}. {result['agency']}")
        print(f"   Priority: {result['priority_score']:.2f} | Specificity: {result['specificity_score']:.2f} | Likelihood: {result['likelihood_score']:.2f}")
        print(f"   Request: {result['record_request'][:80]}...")
    
    print("\n" + "=" * 70)
    print("Quality Score Distribution:")
    print("=" * 70)
    
    high_priority = sum(1 for r in results if r['priority_score'] >= 0.7)
    medium_priority = sum(1 for r in results if 0.4 <= r['priority_score'] < 0.7)
    low_priority = sum(1 for r in results if r['priority_score'] < 0.4)
    
    high_specificity = sum(1 for r in results if r['specificity_score'] >= 0.7)
    medium_specificity = sum(1 for r in results if 0.4 <= r['specificity_score'] < 0.7)
    low_specificity = sum(1 for r in results if r['specificity_score'] < 0.4)
    
    high_likelihood = sum(1 for r in results if r['likelihood_score'] >= 0.6)
    medium_likelihood = sum(1 for r in results if 0.3 <= r['likelihood_score'] < 0.6)
    low_likelihood = sum(1 for r in results if r['likelihood_score'] < 0.3)
    
    print(f"\nPriority Scores:")
    print(f"  High (≥0.7): {high_priority}")
    print(f"  Medium (0.4-0.7): {medium_priority}")
    print(f"  Low (<0.4): {low_priority}")
    
    print(f"\nSpecificity Scores:")
    print(f"  High (≥0.7): {high_specificity}")
    print(f"  Medium (0.4-0.7): {medium_specificity}")
    print(f"  Low (<0.4): {low_specificity}")
    
    print(f"\nLikelihood Scores:")
    print(f"  High (≥0.6): {high_likelihood}")
    print(f"  Medium (0.3-0.6): {medium_likelihood}")
    print(f"  Low (<0.3): {low_likelihood}")
    
    # Save results to new CSV with scores
    output_path = csv_path.parent / f"{csv_path.stem}_with_scores.csv"
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['agency', 'record_request', 'timeframe', 'relevance', 'notes', 
                     'specificity_score', 'likelihood_score', 'priority_score', 'quality_notes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n" + "=" * 70)
    print(f"Results saved to: {output_path.name}")
    print("=" * 70)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    analyze_foia_targets(FOIA_CSV)
