"""
Extract entities, FOIA targets, and relationships from UAPGerb's "The Hidden Wing" transcript
US Air Force UFO Reverse Engineering Programs (2026)

Source: https://www.youtube.com/watch?v=-IXSZe4xVv4
"""
import re
import csv
from pathlib import Path
from typing import List, Dict

# Intelligence Stack Levels for categorization
INTEL_STACK_LEVELS = {
    1: "Control Group",      # MITRE/JASON, NSC, Executive Branch
    2: "Administrators",     # NRO, NGA, CIA DS&T, DIA, NSA, OUSD
    3: "FFRDCs",            # MITRE, Battelle, Sandia, LANL, LLNL, Oak Ridge
    4: "Prime Contractors", # Lockheed Martin, Northrop Grumman, Raytheon
    5: "Facilities",        # Area 51, S4, Edwards AFB, Tonopah, Dugway
    6: "Programs",          # Immaculate Constellation, Kona Blue, etc.
}

# New entities from "The Hidden Wing" transcript - Air Force organizational structure
HIDDEN_WING_ENTITIES = {
    # Department of Air Force (DAF) Structure
    'DAF': {
        'display_name': 'Department of the Air Force',
        'normalized_name': 'DAF',
        'entity_type': 'Government Agency',
        'description': 'Overarching entity encompassing the US Air Force and Space Force, led by Secretary of the Air Force',
        'aliases': 'DAF, Department of Air Force',
        'intel_stack_level': 2
    },
    'HALF': {
        'display_name': 'Headquarters Air Force',
        'normalized_name': 'HALF',
        'entity_type': 'Government Agency',
        'description': 'Top-level Air Force military staff supporting Secretary of the Air Force and Air Force Chief of Staff',
        'aliases': 'HALF, HAF, Headquarters of the Air Force',
        'intel_stack_level': 2
    },
    
    # Air Force Secretariat - SAF Hierarchy
    'SAF-AQ': {
        'display_name': 'Air Force Acquisition (SAF-AQ)',
        'normalized_name': 'SAF-AQ',
        'entity_type': 'Government Agency',
        'description': 'Air Force Secretariat Acquisition - vast majority of Air Force UFO legacy program operations reside here. Controls cutting-edge acquisition, RDT&E, and S&T',
        'aliases': 'SAF-AQ, SAFAQ, Air Force Acquisition',
        'intel_stack_level': 2
    },
    'SAF-AQL': {
        'display_name': 'Air Force Special Programs (SAF-AQL)',
        'normalized_name': 'SAF-AQL',
        'entity_type': 'Government Agency',
        'description': 'Directorate under SAF-AQ - integrates SAP and non-SAP RDT&E, S&T planning activities. Interfaces with AFRL Technology Executive Officers',
        'aliases': 'SAF-AQL, SAFAQL, Air Force Special Programs',
        'intel_stack_level': 2
    },
    'SAF-AQX': {
        'display_name': 'Air Force Acquisition Integration (SAF-AQX)',
        'normalized_name': 'SAF-AQX',
        'entity_type': 'Government Agency',
        'description': 'Acquisition Integration directorate under SAF-AQ',
        'aliases': 'SAF-AQX, SAFAQX, Acquisition Integration',
        'intel_stack_level': 2
    },
    'SAF-AQR': {
        'display_name': 'Air Force Science, Technology and Engineering (SAF-AQR)',
        'normalized_name': 'SAF-AQR',
        'entity_type': 'Government Agency',
        'description': 'Science, Technology and Engineering directorate under SAF-AQ. Works closely with SAF-AQL on advanced technology development',
        'aliases': 'SAF-AQR, SAFAQR, Science Technology Engineering',
        'intel_stack_level': 2
    },
    'RCO': {
        'display_name': 'Air Force Rapid Capabilities Office',
        'normalized_name': 'RCO',
        'entity_type': 'Government Agency',
        'description': 'Accelerated acquisition office praised for developing and fielding critical combat capabilities. Operates in gray area with minimal oversight and near-limitless funding. Controlling entity for Air Force legacy program oversight',
        'aliases': 'RCO, Rapid Capabilities Office, AF RCO',
        'intel_stack_level': 2
    },
    
    # Administrative Assistant to SecAF offices
    'SAF-AA': {
        'display_name': 'Administrative Assistant to Secretary of Air Force',
        'normalized_name': 'SAF-AA',
        'entity_type': 'Government Agency',
        'description': 'Administrative Assistant to the Secretary of the Air Force within Headquarters Air Force',
        'aliases': 'SAF-AA, SAFAA',
        'intel_stack_level': 2
    },
    'SAF-AAH': {
        'display_name': 'Air Force Sensitive Activities (SAF-AAH)',
        'normalized_name': 'SAF-AAH',
        'entity_type': 'Government Agency',
        'description': 'Sensitive Activities directorate under SAF-AA. OPR for addressing combat Air Force and combat support agency mission needs involving sensitive activities per DODI S-5210.36',
        'aliases': 'SAF-AAH, SAFAAH, Sensitive Activities',
        'intel_stack_level': 2
    },
    'SAF-AAZ': {
        'display_name': 'Air Force Security/Special Programs Oversight (SAF-AAZ)',
        'normalized_name': 'SAF-AAZ',
        'entity_type': 'Government Agency',
        'description': 'Security, Special Programs Oversight, and Information Protection directorate under SAF-AA',
        'aliases': 'SAF-AAZ, SAFAAZ, Special Programs Oversight',
        'intel_stack_level': 2
    },
    
    # Air Force Test and Evaluation
    'AFTE': {
        'display_name': 'Air Force Test and Evaluation',
        'normalized_name': 'AFTE',
        'entity_type': 'Government Agency',
        'description': 'Air Staff compliance element for Test and Evaluation. Actual RDT&E of exotic vehicles and derivative technologies conducted here',
        'aliases': 'AFTE, AF T&E, Air Force Test and Evaluation',
        'intel_stack_level': 2
    },
    'AFTEP': {
        'display_name': 'Air Force T&E Policy and Programs (AFTEP)',
        'normalized_name': 'AFTEP',
        'entity_type': 'Government Agency',
        'description': 'Policy and Programs subordinate under Air Force Test and Evaluation',
        'aliases': 'AFTEP',
        'intel_stack_level': 2
    },
    'AFTER': {
        'display_name': 'Air Force T&E Resource Integration (AFTER)',
        'normalized_name': 'AFTER',
        'entity_type': 'Government Agency',
        'description': 'Resource Integration subordinate under Air Force Test and Evaluation',
        'aliases': 'AFTER',
        'intel_stack_level': 2
    },
    'AFTEZ': {
        'display_name': 'Air Force T&E Special Programs (AFTEZ)',
        'normalized_name': 'AFTEZ',
        'entity_type': 'Government Agency',
        'description': 'Special Programs subordinate under Air Force Test and Evaluation',
        'aliases': 'AFTEZ',
        'intel_stack_level': 2
    },
    
    # Major Commands and Research Labs
    'AFMC': {
        'display_name': 'Air Force Materiel Command',
        'normalized_name': 'AFMC',
        'entity_type': 'Government Agency',
        'description': 'Major Command (MAJCOM) - research, development, test, evaluation, and sustainment of weapon systems',
        'aliases': 'AFMC, Air Force Materiel Command',
        'intel_stack_level': 2
    },
    'AFRL': {
        'display_name': 'Air Force Research Laboratory',
        'normalized_name': 'AFRL',
        'entity_type': 'Research Institution',
        'description': 'Air Force Research Lab under AFMC. Technology Executive Officers interface with SAF-AQL for all Air Force S&T Programs',
        'aliases': 'AFRL, Air Force Research Lab, AF Research Laboratory',
        'intel_stack_level': 3
    },
    
    # Test Wings and Facilities
    '412th_Test_Wing': {
        'display_name': '412th Test Wing',
        'normalized_name': '412th Test Wing',
        'entity_type': 'Government Agency',
        'description': 'Edwards Air Force Base test wing. Operates manned flights at Area 51. ARV (Alien Reproduction Vehicle) testing program conducted here per Lt Col testimony',
        'aliases': '412 Test Wing, 412th TW, Edwards Test Wing',
        'intel_stack_level': 5
    },
    
    # Office of Secretary of Defense connections
    'USD-ANS': {
        'display_name': 'Under Secretary of Defense for Acquisition and Sustainment',
        'normalized_name': 'USD-ANS',
        'entity_type': 'Government Agency',
        'description': 'Department under OSD. Integral administrator to NRO UFO legacy programs. Partners with SAF-AQL for technology transfer and potentially hiding materials/budget',
        'aliases': 'USD-ANS, USD(A&S), OUSD A&S, OUSDAT',
        'intel_stack_level': 2
    },
    'OSD': {
        'display_name': 'Office of Secretary of Defense',
        'normalized_name': 'OSD',
        'entity_type': 'Government Agency',
        'description': 'Office of the Secretary of Defense - SAF-AQL and AFRL work closely with OSD Funding and Program Management Structure',
        'aliases': 'OSD, Office of Secretary of Defense',
        'intel_stack_level': 2
    },
    
    # National Security Council
    'NSC': {
        'display_name': 'National Security Council',
        'normalized_name': 'NSC',
        'entity_type': 'Government Agency',
        'description': 'US National Security Council within executive branch. May utilize partnerships between USD-ANS and SAF-AQ for clandestine UFO-related purposes',
        'aliases': 'NSC, National Security Council',
        'intel_stack_level': 1
    },
    
    # Jason Advisory Panel
    'JASON': {
        'display_name': 'JASON Advisory Panel',
        'normalized_name': 'JASON',
        'entity_type': 'Research Institution',
        'description': 'Secretive scientific think tank run out of MITRE Corporation. Part of UFO control group with consensus understanding of legacy programs',
        'aliases': 'JASON, Jason Panel, Jason Advisory Group',
        'intel_stack_level': 1
    },
    
    # Key Individuals mentioned
    'David_Grusch': {
        'display_name': 'David Grusch',
        'normalized_name': 'David Grusch',
        'entity_type': 'Individual',
        'description': 'Provided 2023 testimony on UFO crash retrievals and reverse engineering programs',
        'aliases': 'David Grusch, Grusch',
        'intel_stack_level': None
    },
    'Ed': {
        'display_name': 'Ed (Air Force Acquisition Witness)',
        'normalized_name': 'Ed',
        'entity_type': 'Individual',
        'description': 'Witness who served in Air Force acquisition at Pentagon. Testified about misappropriation of funds within SAF-AQ as inflection point where funds go black',
        'aliases': 'Ed',
        'intel_stack_level': None
    },
    'Hal_Puthoff': {
        'display_name': 'Hal Puthoff',
        'normalized_name': 'Hal Puthoff',
        'entity_type': 'Individual',
        'description': 'Claims UFO legacy programs relegated to defense industrial base prime contractors to protect from FOIA',
        'aliases': 'Hal Puthoff, Harold Puthoff',
        'intel_stack_level': None
    },
    'Dick_Cheney': {
        'display_name': 'Dick Cheney',
        'normalized_name': 'Dick Cheney',
        'entity_type': 'Individual',
        'description': 'Late former Secretary of Defense. Powerful figure with ties to executive branch above Jason and UFO control group',
        'aliases': 'Dick Cheney, Richard Cheney',
        'intel_stack_level': 1
    },
    
    # Classification/Oversight Directives
    'DODI_S5210_36': {
        'display_name': 'DODI S-5210.36 Sensitive Support Directive',
        'normalized_name': 'DODI S-5210.36',
        'entity_type': 'Program',
        'description': 'Classified DOD directive (6 Nov 2008) - Provision of DOD sensitive support to DOD components and other US government agencies. Governs sensitive activities under SAF-AAH',
        'aliases': 'DODI S-5210.36, DOD Directive S-5210.36',
        'intel_stack_level': None
    },
}

# New relationships from Hidden Wing transcript - Air Force organizational hierarchy
HIDDEN_WING_RELATIONSHIPS = [
    # DAF Structure
    ('Department of the Air Force', 'Headquarters Air Force', 'Contains', 'DAF encompasses HALF as top-level military staff'),
    ('Headquarters Air Force', 'Air Force Acquisition (SAF-AQ)', 'Contains', 'HALF houses SAF-AQ within the Air Force Secretariat'),
    
    # SAF-AQ Hierarchy
    ('Air Force Acquisition (SAF-AQ)', 'Air Force Special Programs (SAF-AQL)', 'Directorate', 'SAF-AQL is directorate under SAF-AQ'),
    ('Air Force Acquisition (SAF-AQ)', 'Air Force Acquisition Integration (SAF-AQX)', 'Directorate', 'SAF-AQX is directorate under SAF-AQ'),
    ('Air Force Acquisition (SAF-AQ)', 'Air Force Science, Technology and Engineering (SAF-AQR)', 'Directorate', 'SAF-AQR is directorate under SAF-AQ'),
    ('Air Force Acquisition (SAF-AQ)', 'Air Force Rapid Capabilities Office', 'Oversight', 'RCO operates under SAF-AQ oversight with near-limitless funding'),
    
    # SAF-AA Hierarchy
    ('Administrative Assistant to Secretary of Air Force', 'Air Force Sensitive Activities (SAF-AAH)', 'Directorate', 'SAF-AAH falls under SAF-AA'),
    ('Administrative Assistant to Secretary of Air Force', 'Air Force Security/Special Programs Oversight (SAF-AAZ)', 'Directorate', 'SAF-AAZ falls under SAF-AA'),
    ('Headquarters Air Force', 'Administrative Assistant to Secretary of Air Force', 'Contains', 'SAF-AA within HALF'),
    
    # Test and Evaluation
    ('Headquarters Air Force', 'Air Force Test and Evaluation', 'Air Staff', 'AFTE is Air Staff compliance element'),
    ('Air Force Test and Evaluation', 'Air Force T&E Policy and Programs (AFTEP)', 'Subordinate', 'AFTEP under AFTE'),
    ('Air Force Test and Evaluation', 'Air Force T&E Resource Integration (AFTER)', 'Subordinate', 'AFTER under AFTE'),
    ('Air Force Test and Evaluation', 'Air Force T&E Special Programs (AFTEZ)', 'Subordinate', 'AFTEZ under AFTE'),
    
    # Research Lab Chain
    ('Air Force Materiel Command', 'Air Force Research Laboratory', 'Contains', 'AFRL under AFMC'),
    ('Air Force Special Programs (SAF-AQL)', 'Air Force Research Laboratory', 'Interfaces With', 'SAF-AQL interfaces with AFRL Technology Executive Officers for all AF S&T Programs'),
    ('Air Force Special Programs (SAF-AQL)', 'Air Force Science, Technology and Engineering (SAF-AQR)', 'Coordinates With', 'SAF-AQL works closely with SAF-AQR on SAP and non-SAP RDT&E'),
    
    # OSD Partnerships
    ('Air Force Special Programs (SAF-AQL)', 'Under Secretary of Defense for Acquisition and Sustainment', 'Partnership', 'USD-ANS partners with SAF-AQL. NSC may use this for clandestine UFO purposes'),
    ('Under Secretary of Defense for Acquisition and Sustainment', 'Office of Secretary of Defense', 'Under', 'USD-ANS is department under OSD'),
    ('Air Force Special Programs (SAF-AQL)', 'Office of Secretary of Defense', 'Works With', 'SAF-AQL and AFRL work closely with OSD Funding and Program Management'),
    
    # Test Facilities
    ('412th Test Wing', 'Edwards Air Force Base', 'Based At', '412th Test Wing based at Edwards AFB'),
    ('412th Test Wing', 'Area 51', 'Operates At', '412th Test Wing operates manned flights at Area 51'),
    ('Air Force Rapid Capabilities Office', '412th Test Wing', 'Oversight', 'RCO has oversight of test wing operations'),
    
    # Control Group Connections
    ('JASON Advisory Panel', 'MITRE Corporation', 'Run Out Of', 'Jason Advisory Panel run out of MITRE Corporation'),
    ('JASON Advisory Panel', 'National Security Council', 'Below', 'Jason and UFO control group below powerful NSC figures'),
    ('Dick Cheney', 'National Security Council', 'Ties To', 'Former SecDef with ties to executive branch'),
    
    # Sensitive Activities
    ('Air Force Sensitive Activities (SAF-AAH)', 'DODI S-5210.36 Sensitive Support Directive', 'Governed By', 'SAF-AAH sensitive activities defined by DODI S-5210.36'),
    
    # Witness Testimony Connections
    ('Ed (Air Force Acquisition Witness)', 'Air Force Acquisition (SAF-AQ)', 'Testified About', 'Ed testified SAF-AQ is inflection point where funds go black'),
    ('David Grusch', 'Department of the Air Force', 'Testified About', '2023 testimony on UFO crash retrievals'),
]

# FOIA Targets specific to Hidden Wing transcript
HIDDEN_WING_FOIA_TARGETS = [
    {
        'agency': 'SAF-AQ',
        'record_request': 'Air Force Acquisition budget records, misappropriation of funds documentation, black budget inflection points',
        'timeframe': '2000-present',
        'relevance': 'Per testimony, SAF-AQ is where funds "go black" for legacy programs',
        'notes': 'Ed testified specifically about SAF-AQ as inflection point for fund misappropriation'
    },
    {
        'agency': 'SAF-AQL',
        'record_request': 'Special Access Program integration records, S&T planning activities with AFRL, technology transfer vessel documentation',
        'timeframe': '1990s-present',
        'relevance': 'SAF-AQL integrates SAP and non-SAP RDT&E, interfaces with AFRL for all AF S&T Programs',
        'notes': 'USD-ANS and NSC may use SAF-AQL partnership for clandestine purposes'
    },
    {
        'agency': 'RCO',
        'record_request': 'Rapid Capabilities Office program records, accelerated acquisition documentation, funding sources',
        'timeframe': '2003-present',
        'relevance': 'RCO is controlling entity for Air Force legacy program oversight with near-limitless funding',
        'notes': 'Operates in gray area with minimal bureaucratic oversight'
    },
    {
        'agency': 'SAF-AAH',
        'record_request': 'Sensitive Activities records per DODI S-5210.36, combat support agency mission documentation',
        'timeframe': '2008-present',
        'relevance': 'SAF-AAH is OPR for sensitive activities involving non-DOD federal agencies',
        'notes': 'Very little publicly available. DODI S-5210.36 classified directive governs scope'
    },
    {
        'agency': 'SAF-AAZ',
        'record_request': 'Special Programs Oversight records, security and information protection documentation',
        'timeframe': '2000-present',
        'relevance': 'SAF-AAZ handles special programs oversight within HALF',
        'notes': 'Security mechanisms for Air Force legacy programs'
    },
    {
        'agency': 'AFTE',
        'record_request': 'Air Force Test and Evaluation records for exotic vehicle and derivative technology RDT&E',
        'timeframe': '1990s-present',
        'relevance': 'Actual RDT&E of exotic vehicles conducted under AFTE per transcript theory',
        'notes': 'Includes AFTEP, AFTER, AFTEZ subordinate records'
    },
    {
        'agency': '412th Test Wing',
        'record_request': 'Edwards Test Wing records for Area 51 manned flight operations, ARV testing program documentation',
        'timeframe': '1998-2007',
        'relevance': 'Lt Col testimony of running ARV testing program at Edwards',
        'notes': 'Electronics warfare group director ran alien reproduction vehicle testing'
    },
    {
        'agency': 'JASON',
        'record_request': 'JASON Advisory Panel records related to UFO/UAP scientific assessments, MITRE-hosted meetings',
        'timeframe': '1960s-present',
        'relevance': 'JASON is part of UFO control group with consensus understanding of legacy programs',
        'notes': 'Secretive think tank run out of MITRE Corporation'
    },
]


def generate_entity_id(display_name: str) -> str:
    """Generate entity ID from display name"""
    entity_id = display_name.lower()
    entity_id = re.sub(r'[^a-z0-9]+', '_', entity_id)
    entity_id = re.sub(r'_+', '_', entity_id)
    entity_id = entity_id.strip('_')
    return f"hidden_wing_{entity_id}"


def extract_entities() -> List[Dict]:
    """Extract entities from predefined list"""
    entities = []
    for key, info in HIDDEN_WING_ENTITIES.items():
        entity_id = generate_entity_id(info['display_name'])
        entities.append({
            'entity_id': entity_id,
            'display_name': info['display_name'],
            'normalized_name': info['normalized_name'],
            'entity_type': info['entity_type'],
            'description': info['description'],
            'aliases': info.get('aliases', ''),
            'intel_stack_level': info.get('intel_stack_level', ''),
            'source': 'UAPGerb - Hidden Wing (2026)'
        })
    return entities


def write_entities_csv(output_path: Path) -> int:
    """Write entities to CSV file"""
    entities = extract_entities()
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['entity_id', 'display_name', 'normalized_name', 'entity_type', 
                      'description', 'aliases', 'intel_stack_level', 'source']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entities)
    
    print(f"[OK] Written {len(entities)} entities to {output_path}")
    return len(entities)


def write_relationships_csv(output_path: Path) -> int:
    """Write relationships to CSV file"""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['source', 'target', 'label', 'notes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rel in HIDDEN_WING_RELATIONSHIPS:
            writer.writerow({
                'source': rel[0],
                'target': rel[1],
                'label': rel[2],
                'notes': rel[3] if len(rel) > 3 else ''
            })
    
    print(f"[OK] Written {len(HIDDEN_WING_RELATIONSHIPS)} relationships to {output_path}")
    return len(HIDDEN_WING_RELATIONSHIPS)


def write_foia_targets_csv(output_path: Path) -> int:
    """Write FOIA targets to CSV file"""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['agency', 'record_request', 'timeframe', 'relevance', 'notes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(HIDDEN_WING_FOIA_TARGETS)
    
    print(f"[OK] Written {len(HIDDEN_WING_FOIA_TARGETS)} FOIA targets to {output_path}")
    return len(HIDDEN_WING_FOIA_TARGETS)


def main():
    """Main extraction function"""
    project_root = Path(__file__).parent.parent.parent
    entities_dir = project_root / 'data' / 'entities'
    foia_dir = project_root / 'data' / 'foia'
    
    # Create directories if needed
    entities_dir.mkdir(parents=True, exist_ok=True)
    foia_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("Extracting data from UAPGerb's 'The Hidden Wing' transcript")
    print("US Air Force UFO Reverse Engineering Programs (2026)")
    print("Source: https://www.youtube.com/watch?v=-IXSZe4xVv4")
    print("=" * 70)
    
    # Generate CSV files
    entities_count = write_entities_csv(entities_dir / 'hidden_wing_entities.csv')
    relationships_count = write_relationships_csv(entities_dir / 'hidden_wing_relationships.csv')
    foia_count = write_foia_targets_csv(foia_dir / 'hidden_wing_foia_targets.csv')
    
    print("=" * 70)
    print(f"\nSummary:")
    print(f"  New Entities: {entities_count}")
    print(f"  New Relationships: {relationships_count}")
    print(f"  New FOIA Targets: {foia_count}")
    print("\n[OK] Extraction complete!")
    print("\nTo load into database, run:")
    print("  python reload_database.py")


if __name__ == '__main__':
    main()
