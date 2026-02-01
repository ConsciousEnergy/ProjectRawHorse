#!/usr/bin/env python3
"""
Review and validate enriched flow data for accuracy
"""
import sys
import csv
from pathlib import Path
from collections import defaultdict

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from database import init_database, get_session_maker, MoneyFlow, Entity
import yaml

# Configuration
PROJECT_ROOT = Path(__file__).parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"

# Load configuration
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

def normalize_name(name: str) -> str:
    """Normalize entity name for comparison"""
    return name.strip().upper().replace('"', '').replace("'", "").replace(' ', '')

def review_enriched_flows():
    """Review enriched flows for accuracy"""
    print("=" * 70)
    print("Enrichment Data Review - Accuracy Check")
    print("=" * 70)
    
    # Find test enrichment files
    test_files = list((PROJECT_ROOT / "data" / "financial").glob("test_enriched_flows_*.csv"))
    
    if not test_files:
        print("\n[ERROR] No test enrichment files found")
        return
    
    latest_file = max(test_files, key=lambda p: p.stat().st_mtime)
    print(f"\nReviewing: {latest_file.name}")
    
    # Load enriched flows
    enriched_flows = []
    with open(latest_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            enriched_flows.append(row)
    
    print(f"\nTotal enriched flows: {len(enriched_flows)}")
    
    if not enriched_flows:
        print("\n[WARNING] No flows found in enrichment file")
        return
    
    # Initialize database
    db_path = PROJECT_ROOT / config['database']['path']
    engine = init_database(str(db_path))
    session_maker = get_session_maker(engine)
    db = session_maker()
    
    try:
        # Get existing money flows for comparison
        existing_flows = db.query(MoneyFlow).all()
        existing_by_source = defaultdict(list)
        for flow in existing_flows:
            existing_by_source[normalize_name(flow.source)].append(flow)
        
        # Get all entities for validation
        entities = {normalize_name(e.display_name): e for e in db.query(Entity).all()}
        
        print("\n" + "=" * 70)
        print("DETAILED REVIEW")
        print("=" * 70)
        
        issues = []
        valid_flows = []
        
        for i, flow in enumerate(enriched_flows, 1):
            print(f"\n[{i}] Flow Review:")
            print(f"  Source: {flow['source']}")
            print(f"  Target: {flow['target']}")
            print(f"  Relationship: {flow['relationship']}")
            print(f"  Amount: {flow['amount_usd'] or 'Not specified'}")
            print(f"  Citation: {flow['source_citation'][:80]}..." if len(flow.get('source_citation', '')) > 80 else f"  Citation: {flow.get('source_citation', 'None')}")
            print(f"  Notes: {flow.get('notes', '')[:100]}..." if len(flow.get('notes', '')) > 100 else f"  Notes: {flow.get('notes', 'None')}")
            
            # Validation checks
            flow_issues = []
            
            # 1. Check if source entity exists
            source_norm = normalize_name(flow['source'])
            if source_norm not in entities:
                flow_issues.append(f"Source entity '{flow['source']}' not found in database")
                print(f"  [WARNING] Source entity not in database")
            else:
                print(f"  [OK] Source entity verified: {entities[source_norm].display_name}")
            
            # 2. Check if target is "Unknown"
            if flow['target'] == 'Unknown':
                flow_issues.append("Target entity is 'Unknown' - needs manual identification")
                print(f"  [WARNING] Target entity is 'Unknown' - requires manual research")
            else:
                target_norm = normalize_name(flow['target'])
                if target_norm in entities:
                    print(f"  [OK] Target entity verified: {entities[target_norm].display_name}")
                else:
                    flow_issues.append(f"Target entity '{flow['target']}' not found in database")
                    print(f"  [WARNING] Target entity not in database")
            
            # 3. Check for duplicates with existing flows
            source_existing = existing_by_source.get(source_norm, [])
            is_duplicate = False
            for existing in source_existing:
                target_norm_existing = normalize_name(existing.target)
                target_norm_new = normalize_name(flow['target'])
                if target_norm_existing == target_norm_new:
                    if existing.relationship and flow['relationship']:
                        if existing.relationship.lower() in flow['relationship'].lower() or \
                           flow['relationship'].lower() in existing.relationship.lower():
                            is_duplicate = True
                            print(f"  [DUPLICATE] Similar flow exists:")
                            print(f"    Existing: {existing.source} -> {existing.target}")
                            print(f"    Type: {existing.relationship}")
                            print(f"    Amount: ${existing.amount_usd:,.0f}" if existing.amount_usd else "    Amount: Not specified")
                            flow_issues.append(f"Potential duplicate with existing flow ID {existing.id}")
                            break
            
            if not is_duplicate:
                print(f"  [OK] No duplicate found")
            
            # 4. Check data completeness
            if not flow.get('amount_usd'):
                flow_issues.append("No amount specified")
                print(f"  [INFO] No amount extracted from search results")
            
            if not flow.get('start_date'):
                flow_issues.append("No date specified")
                print(f"  [INFO] No date extracted from search results")
            
            # 5. Validate citation URL
            citation = flow.get('source_citation', '')
            if citation and (citation.startswith('http://') or citation.startswith('https://')):
                print(f"  [OK] Valid citation URL")
            elif citation:
                flow_issues.append("Invalid citation URL format")
                print(f"  [WARNING] Citation URL format may be invalid")
            else:
                flow_issues.append("No citation URL")
                print(f"  [WARNING] No citation URL provided")
            
            if flow_issues:
                issues.append({
                    'flow': flow,
                    'issues': flow_issues
                })
            else:
                valid_flows.append(flow)
        
        # Summary
        print("\n" + "=" * 70)
        print("REVIEW SUMMARY")
        print("=" * 70)
        print(f"\nTotal flows reviewed: {len(enriched_flows)}")
        print(f"Valid flows (no issues): {len(valid_flows)}")
        print(f"Flows with issues: {len(issues)}")
        
        if issues:
            print("\nIssues found:")
            issue_types = defaultdict(int)
            for item in issues:
                for issue in item['issues']:
                    issue_type = issue.split(':')[0] if ':' in issue else issue.split('-')[0]
                    issue_types[issue_type] += 1
            
            for issue_type, count in sorted(issue_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  {issue_type}: {count}")
        
        # Recommendations
        print("\n" + "=" * 70)
        print("RECOMMENDATIONS")
        print("=" * 70)
        
        if len(valid_flows) == len(enriched_flows):
            print("\n[OK] All flows passed validation!")
            print("You can proceed to load these flows into the database.")
        else:
            print("\n[ACTION REQUIRED] Some flows need attention:")
            print("\n1. Manual Review Required:")
            print("   - Review flows with 'Unknown' targets")
            print("   - Verify citation URLs are accessible")
            print("   - Check for actual duplicates vs. similar but distinct flows")
            
            print("\n2. Data Enhancement Needed:")
            print("   - Add missing target entities to database if valid")
            print("   - Extract dates from citation sources if available")
            print("   - Extract amounts from citation sources if available")
            
            print("\n3. Before Loading to Database:")
            print("   - Manually edit the CSV file to fix issues")
            print("   - Remove or fix flows with critical issues")
            print("   - Add missing dates and amounts where possible")
        
        # Show specific recommendations for each flow with issues
        if issues:
            print("\n" + "=" * 70)
            print("DETAILED ISSUES")
            print("=" * 70)
            for i, item in enumerate(issues, 1):
                flow = item['flow']
                print(f"\n[{i}] {flow['source']} -> {flow['target']}")
                for issue in item['issues']:
                    print(f"   - {issue}")
        
    finally:
        db.close()

if __name__ == "__main__":
    review_enriched_flows()
