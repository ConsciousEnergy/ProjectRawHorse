#!/usr/bin/env python3
"""
Entity recognition and matching utilities for flow extraction
"""
import re
from typing import List, Dict, Optional, Set, TYPE_CHECKING
from rapidfuzz import fuzz, process

if TYPE_CHECKING:
    from database import Entity

try:
    import spacy
    nlp = None
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("[WARNING] spaCy model not loaded. Install with: python -m spacy download en_core_web_sm")
except ImportError:
    nlp = None


def extract_entities_ner(text: str) -> List[str]:
    """Extract organization names using spaCy NER"""
    if not nlp:
        return []
    
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        if ent.label_ in ['ORG', 'PERSON']:  # Organization or Person
            entities.append(ent.text.strip())
    return entities


def extract_entities_patterns(text: str, source_entity: str) -> List[str]:
    """Extract target entities using pattern matching"""
    entities = []
    text_lower = text.lower()
    source_lower = source_entity.lower()
    
    # Pattern: "X acquires Y", "X to acquire Y"
    patterns = [
        rf'{re.escape(source_entity)}\s+(?:acquires?|acquired|to acquire|acquiring)\s+([A-Z][A-Za-z0-9\s&,.-]+?)(?:\s|,|\.|$)',
        rf'{re.escape(source_entity)}\s+(?:acquires?|acquired|to acquire|acquiring)\s+([A-Z][A-Za-z0-9\s&,.-]+?)(?:\s+for|\s+in|\s+at|$)',
    ]
    
    # Pattern: "X contract with Y", "X awarded to Y"
    patterns.extend([
        rf'{re.escape(source_entity)}\s+contract\s+(?:with|to|for)\s+([A-Z][A-Za-z0-9\s&,.-]+?)(?:\s|,|\.|$)',
        rf'{re.escape(source_entity)}\s+award(?:ed)?\s+(?:to|for)\s+([A-Z][A-Za-z0-9\s&,.-]+?)(?:\s|,|\.|$)',
    ])
    
    # Pattern: "X partnership with Y", "X invests in Y"
    patterns.extend([
        rf'{re.escape(source_entity)}\s+partnership\s+(?:with|between)\s+([A-Z][A-Za-z0-9\s&,.-]+?)(?:\s|,|\.|$)',
        rf'{re.escape(source_entity)}\s+invests?\s+(?:in|into)\s+([A-Z][A-Za-z0-9\s&,.-]+?)(?:\s|,|\.|$)',
    ])
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            entity = match.group(1).strip()
            # Clean up entity name
            entity = re.sub(r'\s+', ' ', entity)  # Normalize whitespace
            entity = re.sub(r'[,.]$', '', entity)  # Remove trailing punctuation
            # Filter out common non-entity words
            if entity and len(entity) > 2 and entity.lower() not in ['the', 'a', 'an', 'and', 'or']:
                entities.append(entity)
    
    return entities


def find_entities_near_keywords(text: str, keywords: List[str], window: int = 10) -> List[str]:
    """Find capitalized entities near financial keywords"""
    entities = []
    words = text.split()
    
    for i, word in enumerate(words):
        word_lower = word.lower().strip('.,;:!?')
        if any(kw in word_lower for kw in keywords):
            # Look for capitalized words in window around keyword
            start = max(0, i - window)
            end = min(len(words), i + window)
            
            for j in range(start, end):
                if j == i:
                    continue
                candidate = words[j].strip('.,;:!?()[]{}')
                # Check if it looks like an entity name
                if (candidate and 
                    len(candidate) > 2 and 
                    candidate[0].isupper() and
                    candidate.lower() not in ['the', 'a', 'an', 'and', 'or', 'of', 'in', 'on', 'at', 'to', 'for']):
                    entities.append(candidate)
    
    return list(set(entities))  # Remove duplicates


def match_entity_to_database(entity_name: str, database_entities: Dict[str, 'Entity'], threshold: int = 85) -> Optional[str]:
    """Match extracted entity name to database entities using fuzzy matching"""
    if not entity_name or len(entity_name) < 3:
        return None
    
    # Exact match first
    normalized = entity_name.upper().strip()
    for db_name, db_entity in database_entities.items():
        if normalized == db_name.upper():
            return db_entity.display_name
    
    # Fuzzy match
    entity_names = [e.display_name for e in database_entities.values()]
    result = process.extractOne(entity_name, entity_names, scorer=fuzz.token_sort_ratio)
    
    if result and result[1] >= threshold:
        return result[0]
    
    return None


def extract_target_entity(text: str, source_entity: str, database_entities: Dict[str, 'Entity']) -> Optional[str]:
    """
    Extract target entity from text using multiple methods
    Returns matched entity name from database or None
    """
    # Method 1: Pattern-based extraction
    pattern_entities = extract_entities_patterns(text, source_entity)
    for entity in pattern_entities:
        matched = match_entity_to_database(entity, database_entities)
        if matched:
            return matched
    
    # Method 2: NER extraction
    if nlp:
        ner_entities = extract_entities_ner(text)
        for entity in ner_entities:
            # Skip if it's the source entity
            if entity.lower() == source_entity.lower():
                continue
            matched = match_entity_to_database(entity, database_entities)
            if matched:
                return matched
    
    # Method 3: Context window around keywords
    financial_keywords = ['acquires', 'acquired', 'contract', 'award', 'partnership', 'invests', 'merger']
    context_entities = find_entities_near_keywords(text, financial_keywords)
    for entity in context_entities:
        if entity.lower() == source_entity.lower():
            continue
        matched = match_entity_to_database(entity, database_entities)
        if matched:
            return matched
    
    return None
