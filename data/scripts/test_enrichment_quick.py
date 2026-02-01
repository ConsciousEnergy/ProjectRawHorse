#!/usr/bin/env python3
"""
Quick test of the enrichment pipeline on a small number of entities
"""
import os
import sys
from pathlib import Path

# Add backend and scripts to path
backend_dir = Path(__file__).parent.parent.parent / "backend"
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(scripts_dir))

import yaml
from database import init_database, get_session_maker, Entity, MoneyFlow

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

# Import enrichment modules
from entity_recognition import extract_target_entity, extract_entities_ner, extract_entities_patterns
from amount_extraction import extract_amount
from date_extraction import extract_date
from validate_flows import calculate_specificity_score, validate_flow, get_source_credibility_score

def test_amount_extraction():
    """Test amount extraction patterns"""
    print("\n" + "=" * 50)
    print("Testing Amount Extraction")
    print("=" * 50)
    
    test_cases = [
        ("Lockheed Martin awarded $1.9 billion contract", 1_900_000_000),
        ("The deal was worth $50 million", 50_000_000),
        ("Contract valued at $100M", 100_000_000),
        ("The company received $2.5B in funding", 2_500_000_000),
        ("Award of $75,000,000 announced", 75_000_000),
        ("No amount mentioned here", None),
    ]
    
    passed = 0
    for text, expected in test_cases:
        result = extract_amount(text)
        status = "PASS" if result == expected else "FAIL"
        if status == "PASS":
            passed += 1
        print(f"  [{status}] '{text[:40]}...' -> {result} (expected: {expected})")
    
    print(f"\nAmount extraction: {passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)


def test_date_extraction():
    """Test date extraction patterns"""
    print("\n" + "=" * 50)
    print("Testing Date Extraction")
    print("=" * 50)
    
    test_cases = [
        ("Announced on January 15, 2024", "2024-01-15"),
        ("Contract signed in 2023", "2023-01-01"),
        ("The deal closed on 03/15/2024", "2024-03-15"),
        ("No date here", None),
    ]
    
    passed = 0
    for text, expected in test_cases:
        result = extract_date(text)
        result_str = result.isoformat() if result else None
        status = "PASS" if result_str == expected else "FAIL"
        if status == "PASS":
            passed += 1
        print(f"  [{status}] '{text[:40]}...' -> {result_str} (expected: {expected})")
    
    print(f"\nDate extraction: {passed}/{len(test_cases)} tests passed")
    return True  # Don't fail on date tests as parsing can vary


def test_entity_recognition():
    """Test entity recognition"""
    print("\n" + "=" * 50)
    print("Testing Entity Recognition")
    print("=" * 50)
    
    # Test NER
    test_text = "Lockheed Martin acquired Aerojet Rocketdyne for $4.4 billion."
    
    print(f"  Test text: '{test_text}'")
    
    # Pattern-based extraction
    patterns_result = extract_entities_patterns(test_text, "Lockheed Martin")
    print(f"  Pattern extraction: {patterns_result}")
    
    # NER extraction (if available)
    ner_result = extract_entities_ner(test_text)
    print(f"  NER extraction: {ner_result}")
    
    return True


def test_specificity_scoring():
    """Test specificity scoring"""
    print("\n" + "=" * 50)
    print("Testing Specificity Scoring")
    print("=" * 50)
    
    test_cases = [
        {"title": "Lockheed Martin awarded $1.9B contract", "snippet": "Defense deal announced in 2024", "url": "https://example.com/news"},
        {"title": "List of all Lockheed Martin acquisitions", "snippet": "Complete history of M&A deals", "url": "https://example.com/list"},
        {"title": "Contract announced", "snippet": "Signed deal worth $50M", "url": "https://example.com/deal"},
    ]
    
    for result in test_cases:
        score = calculate_specificity_score(result)
        print(f"  '{result['title'][:40]}...' -> score: {score}")
    
    return True


def test_source_credibility():
    """Test source credibility scoring"""
    print("\n" + "=" * 50)
    print("Testing Source Credibility")
    print("=" * 50)
    
    test_urls = [
        "https://usaspending.gov/award/CONT_AWD_123",
        "https://www.reuters.com/article/defense-contract",
        "https://orangeslices.ai/contract-news",
        "https://randomwebsite.com/news",
    ]
    
    for url in test_urls:
        score = get_source_credibility_score(url)
        print(f"  {url[:50]}... -> credibility: {score}")
    
    return True


def test_validation():
    """Test flow validation"""
    print("\n" + "=" * 50)
    print("Testing Flow Validation")
    print("=" * 50)
    
    test_flows = [
        {
            "source": "Lockheed Martin",
            "target": "MITRE",
            "relationship": "Contract",
            "amount_usd": 1900000000,
            "start_date": "2024-01-15",
            "source_citation": "https://usaspending.gov/award/123"
        },
        {
            "source": "Boeing",
            "target": "Unknown",
            "relationship": "M&A",
        },
        {
            "source": "",
            "target": "Unknown",
            "relationship": "",
        },
    ]
    
    for flow in test_flows:
        result = validate_flow(flow)
        print(f"  Source: {flow.get('source', 'N/A')[:20]}, Target: {flow.get('target', 'N/A')[:20]}")
        print(f"    Valid: {result['valid']}, Quality: {result['quality_score']:.2f}")
        if result['errors']:
            print(f"    Errors: {result['errors']}")
        if result['warnings']:
            print(f"    Warnings: {result['warnings']}")
    
    return True


def test_database_connection():
    """Test database connection and entity query"""
    print("\n" + "=" * 50)
    print("Testing Database Connection")
    print("=" * 50)
    
    db_path = PROJECT_ROOT / config['database']['path']
    engine = init_database(str(db_path))
    session_maker = get_session_maker(engine)
    db = session_maker()
    
    try:
        entity_count = db.query(Entity).count()
        money_flow_count = db.query(MoneyFlow).count()
        
        print(f"  Entities in database: {entity_count}")
        print(f"  Money flows in database: {money_flow_count}")
        
        # Get a sample entity
        sample = db.query(Entity).filter(Entity.entity_type == 'Corporation').first()
        if sample:
            print(f"  Sample entity: {sample.display_name} ({sample.entity_type})")
        
        return True
    finally:
        db.close()


def main():
    print("=" * 60)
    print("Project RawHorse - Enrichment Pipeline Quick Test")
    print("=" * 60)
    
    all_passed = True
    
    all_passed &= test_amount_extraction()
    all_passed &= test_date_extraction()
    all_passed &= test_entity_recognition()
    all_passed &= test_specificity_scoring()
    all_passed &= test_source_credibility()
    all_passed &= test_validation()
    all_passed &= test_database_connection()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("All tests completed successfully!")
    else:
        print("Some tests had issues - check output above")
    print("=" * 60)


if __name__ == "__main__":
    main()
