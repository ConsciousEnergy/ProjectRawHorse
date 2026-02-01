#!/usr/bin/env python3
"""
Update FOIA targets in database with quality scores
"""
import sys
import yaml
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

sys.stdout.reconfigure(encoding='utf-8')

from database import init_database, get_session_maker, FOIATarget
import sys
import re
from pathlib import Path

# Import quality calculation functions directly
def calculate_specificity_score(record_request: str, timeframe: str, notes: str):
    """Calculate specificity score (0-1)"""
    score = 0.0
    notes_list = []
    
    text = f"{record_request} {timeframe} {notes}".lower()
    
    # Check for specific dates
    if re.search(r'\b(19|20)\d{2}\b', timeframe or ''):
        score += 0.3
        notes_list.append("Has specific date range")
    
    # Check for specific programs
    program_keywords = ['program', 'project', 'operation', 'initiative']
    if any(kw in text for kw in program_keywords):
        score += 0.3
        notes_list.append("References specific programs/projects")
    
    # Check for specific record types
    record_keywords = ['memo', 'contract', 'testimony', 'record', 'document', 'report', 'log']
    if any(kw in text for kw in record_keywords):
        score += 0.2
        notes_list.append("Specifies record types")
    
    # Check for specific amounts
    if re.search(r'\$[\d.,]+\s*(billion|million|thousand)', text):
        score += 0.1
        notes_list.append("References specific dollar amounts")
    
    # Check for specific personnel
    if re.search(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', record_request):
        score += 0.1
        notes_list.append("References specific personnel")
    
    # Penalize vague requests
    vague_terms = ['related to', 'concerning', 'about', 'various', 'general']
    vague_count = sum(1 for term in vague_terms if term in text)
    if vague_count > 2:
        score *= 0.7
        notes_list.append("Contains vague language")
    
    score = min(score, 1.0)
    return score, "; ".join(notes_list) if notes_list else "Standard specificity"


def calculate_likelihood_score(agency: str, timeframe: str, relevance: str):
    """Calculate likelihood of getting a response (0-1)"""
    AGENCY_LIKELIHOOD = {
        'NRO': 0.3, 'CIA': 0.2, 'CIA DS&T': 0.2, 'DOE': 0.4, 'DOE OICI': 0.3,
        'DOE NEST': 0.3, 'DARPA': 0.5, 'DARPA SID': 0.4, 'DHS': 0.6, 'DCSA': 0.5,
        'DoD': 0.5, 'AARO': 0.7, 'GSA': 0.8, 'NGA': 0.4, 'US Army': 0.5,
        'Sandia National Laboratories': 0.4, 'Oak Ridge National Laboratory': 0.4,
        'MITER Corporation': 0.3, 'Edwards 412 Test Wing': 0.3, 'OUSD': 0.4, 'DDNI ATNF': 0.3,
    }
    
    base_score = AGENCY_LIKELIHOOD.get(agency, 0.5)
    notes_list = []
    
    if timeframe:
        years = re.findall(r'\b(19|20)\d{2}\b', timeframe)
        if years:
            try:
                earliest_year = min([int(re.search(r'\b(19|20)\d{2}\b', timeframe).group()) for _ in [1]])
                if earliest_year < 2000:
                    base_score += 0.1
                    notes_list.append("Older records may have better release rates")
                elif 'present' in timeframe.lower():
                    base_score -= 0.1
                    notes_list.append("Current/ongoing records less likely to be released")
            except:
                pass
    
    relevance_lower = (relevance or '').lower()
    if any(term in relevance_lower for term in ['classified', 'sap', 'special access', 'legacy program']):
        base_score -= 0.2
        notes_list.append("High classification level reduces likelihood")
    elif 'public' in relevance_lower or 'declassified' in relevance_lower:
        base_score += 0.1
        notes_list.append("Public/declassified records more likely")
    
    score = max(0.0, min(1.0, base_score))
    return score, "; ".join(notes_list) if notes_list else "Standard likelihood"


def calculate_priority_score(relevance: str, notes: str):
    """Calculate priority/importance score (0-1)"""
    score = 0.0
    notes_list = []
    
    text = f"{relevance} {notes}".lower()
    
    if 'direct connection' in text:
        score += 0.3
        notes_list.append("Direct connection to legacy programs")
    if 'crash retrieval' in text:
        score += 0.3
        notes_list.append("Crash retrieval operations")
    if 'material transfer' in text or 'technology transfer' in text:
        score += 0.2
        notes_list.append("Material/technology transfer")
    if 'classification' in text:
        score += 0.1
        notes_list.append("Classification systems")
    if 'funding' in text or 'misappropriation' in text:
        score += 0.1
        notes_list.append("Funding mechanisms")
    if 'testimony' in text or 'verified' in text or 'mentioned in' in text:
        score += 0.1
        notes_list.append("Based on testimony/verified sources")
    
    score = min(score, 1.0)
    return score, "; ".join(notes_list) if notes_list else "Standard priority"

# Get project root
PROJECT_ROOT = Path(__file__).parent

# Load configuration
config_path = PROJECT_ROOT / "config.yaml"
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# Initialize database
db_path = PROJECT_ROOT / config['database']['path']
print(f"Updating FOIA quality scores in: {db_path}")
print("=" * 70)

# Initialize database connection
engine = init_database(str(db_path))
session_maker = get_session_maker(engine)
db = session_maker()

try:
    # Get all FOIA targets
    foia_targets = db.query(FOIATarget).all()
    print(f"\nFound {len(foia_targets)} FOIA targets")
    
    updated = 0
    for target in foia_targets:
        # Calculate scores
        specificity, spec_notes = calculate_specificity_score(
            target.record_request or '',
            target.timeframe or '',
            target.notes or ''
        )
        likelihood, like_notes = calculate_likelihood_score(
            target.agency or '',
            target.timeframe or '',
            target.relevance or ''
        )
        priority, pri_notes = calculate_priority_score(
            target.relevance or '',
            target.notes or ''
        )
        
        # Update scores
        target.specificity_score = round(specificity, 2)
        target.likelihood_score = round(likelihood, 2)
        target.priority_score = round(priority, 2)
        target.quality_notes = f"Specificity: {spec_notes} | Likelihood: {like_notes} | Priority: {pri_notes}"
        
        updated += 1
    
    db.commit()
    
    print(f"\nUpdated {updated} FOIA targets with quality scores")
    print("=" * 70)
    
    # Show summary
    high_priority = db.query(FOIATarget).filter(FOIATarget.priority_score >= 0.7).count()
    medium_priority = db.query(FOIATarget).filter(
        FOIATarget.priority_score >= 0.4,
        FOIATarget.priority_score < 0.7
    ).count()
    low_priority = db.query(FOIATarget).filter(FOIATarget.priority_score < 0.4).count()
    
    print(f"\nPriority Distribution:")
    print(f"  High (≥0.7): {high_priority}")
    print(f"  Medium (0.4-0.7): {medium_priority}")
    print(f"  Low (<0.4): {low_priority}")
    
    print("\n[OK] FOIA quality scores updated!")
    
finally:
    db.close()
