# Data Enrichment Improvement Plan

## Financial Flows and Materials Transfer Extraction

### Overview

This plan outlines improvements to the entity data enrichment system based on test results and accuracy analysis. The goal is to improve extraction algorithms to produce production-quality financial flow and materials transfer data.

---

## Current State Assessment

### Database Statistics
- **Entities**: 91
- **Money Flows**: 28
- **Unique Entities in Flows**: 33

### Test Results (January 2025)
- **Flows Discovered**: 1
- **Quality Score**: 40%
- **Issues**: Target extraction failed, amounts missing, dates missing

### Key Weaknesses Identified
1. Target entity extraction fails for generic list pages
2. Amount extraction patterns too limited
3. Date extraction not implemented
4. No specificity filtering for list vs. specific transaction pages
5. No quality gates before database import

---

## Improvement Plan

### Phase 1: Enhanced Target Entity Extraction

**Goal**: Improve target entity identification from 0% to >80%

**Tasks**:

1. **Implement Named Entity Recognition (NER)**
   - Use spaCy or similar NLP library for entity extraction
   - Identify organization names in search snippets
   - Match extracted names against existing entity database

2. **Pattern-Based Entity Detection**
   - Add patterns: "{source} acquires {target}", "{source} to acquire {target}"
   - Add patterns: "{source} contract with {target}", "{source} awarded to {target}"
   - Add patterns: "{source} partnership with {target}", "{source} invests in {target}"

3. **Context Window Analysis**
   - Look for entity names within N words of financial keywords
   - Prioritize capitalized multi-word phrases
   - Filter out common non-entity words (Inc., Corp., LLC, etc.)

4. **Entity Database Matching**
   - Cross-reference extracted names with existing entities
   - Use fuzzy matching for partial name matches
   - Flag potential new entities for review

**Files to Modify**:
- `data/scripts/enrich_entity_flows.py` - Add NER and pattern extraction

**New Dependencies**:
- `spacy` - NLP library for entity recognition
- `fuzzywuzzy` or `rapidfuzz` - Fuzzy string matching

---

### Phase 2: Improved Amount Extraction

**Goal**: Extract dollar amounts from >50% of financial flows

**Tasks**:

1. **Expand Regex Patterns**
   ```python
   amount_patterns = [
       # Standard formats
       r'\$(\d+\.?\d*)\s*(?:million|billion|M|B)',
       r'(\d+\.?\d*)\s*(?:million|billion)\s*(?:dollar|USD)',
       r'\$(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
       # Written formats
       r'(\d+\.?\d*)\s*(?:million|billion)\s*deal',
       r'valued\s*at\s*\$?(\d+\.?\d*)\s*(?:million|billion)?',
       r'worth\s*\$?(\d+\.?\d*)\s*(?:million|billion)?',
       r'for\s*\$?(\d+\.?\d*)\s*(?:million|billion)?',
       # Contract values
       r'contract\s*(?:value|worth)?\s*\$?(\d+\.?\d*)\s*(?:million|billion)?',
       r'award(?:ed)?\s*\$?(\d+\.?\d*)\s*(?:million|billion)?',
   ]
   ```

2. **Handle Multiple Currencies**
   - USD, EUR, GBP conversion
   - Store original currency and converted USD value

3. **Range Handling**
   - Parse "$100-200 million" as average or range
   - Handle "up to $X" and "at least $X"

4. **Validation**
   - Sanity check extracted amounts (not too small, not too large)
   - Flag suspicious amounts for review

**Files to Modify**:
- `data/scripts/enrich_entity_flows.py` - Expand amount extraction

---

### Phase 3: Date Extraction

**Goal**: Extract dates from >50% of flows

**Tasks**:

1. **Date Pattern Recognition**
   ```python
   date_patterns = [
       # Full dates
       r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
       r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
       r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})',
       # Year only
       r'in\s+(\d{4})',
       r'during\s+(\d{4})',
       # Relative dates
       r'(last\s+(?:year|month|week))',
       r'(this\s+(?:year|month))',
   ]
   ```

2. **Date Normalization**
   - Convert all dates to ISO format (YYYY-MM-DD)
   - Handle partial dates (year only → January 1 of that year)
   - Handle relative dates based on article publication date

3. **Date Range Handling**
   - Parse "2020-2023" as start_date and end_date
   - Handle fiscal years (FY2023 → 2022-10-01 to 2023-09-30)

**Files to Modify**:
- `data/scripts/enrich_entity_flows.py` - Add date extraction

**New Dependencies**:
- `dateparser` - Flexible date parsing library

---

### Phase 4: Specificity Filtering

**Goal**: Filter out generic list pages, focus on specific transactions

**Tasks**:

1. **List Page Detection**
   - Detect URLs containing "list", "all", "complete", "history"
   - Detect snippets with "list of", "all acquisitions", "complete history"
   - Skip results that are category/index pages

2. **Transaction Specificity Scoring**
   ```python
   def calculate_specificity_score(result):
       score = 0
       text = result['snippet'].lower()
       
       # Positive indicators (specific transaction)
       if re.search(r'\$\d+', text): score += 2  # Has amount
       if re.search(r'\d{4}', text): score += 1  # Has year
       if 'announced' in text: score += 1
       if 'completed' in text: score += 1
       if 'signed' in text: score += 1
       
       # Negative indicators (generic page)
       if 'list of' in text: score -= 3
       if 'all acquisitions' in text: score -= 3
       if 'history of' in text: score -= 2
       if 'complete list' in text: score -= 3
       
       return score
   ```

3. **Minimum Specificity Threshold**
   - Only process results with specificity score > 0
   - Log skipped results for review

**Files to Modify**:
- `data/scripts/enrich_entity_flows.py` - Add specificity filtering

---

### Phase 5: Quality Gates and Validation

**Goal**: Ensure only quality data enters the database

**Tasks**:

1. **Pre-Import Validation**
   ```python
   def validate_flow(flow):
       errors = []
       warnings = []
       
       # Required fields
       if not flow.get('source'): errors.append("Missing source")
       if flow.get('target') == 'Unknown': errors.append("Unknown target")
       
       # Quality checks
       if not flow.get('amount_usd'): warnings.append("No amount")
       if not flow.get('start_date'): warnings.append("No date")
       if not flow.get('source_citation'): warnings.append("No citation")
       
       # Duplicate check
       if is_duplicate(flow): errors.append("Duplicate flow")
       
       return {
           'valid': len(errors) == 0,
           'errors': errors,
           'warnings': warnings
       }
   ```

2. **Duplicate Detection**
   - Check against existing database flows
   - Use fuzzy matching for similar but not identical flows
   - Flag potential duplicates for manual review

3. **Citation Validation**
   - Verify URL is accessible
   - Check URL domain is reputable source
   - Store archive.org backup link

4. **Human Review Queue**
   - Flows with warnings go to review queue
   - Flows with errors are rejected
   - Clean flows can be auto-imported

**Files to Create**:
- `data/scripts/validate_flows.py` - Validation module
- `data/scripts/review_queue.py` - Human review interface

---

### Phase 6: Enhanced Search Strategies

**Goal**: Improve search result quality and coverage

**Tasks**:

1. **Multi-Source Search**
   - Primary: DuckDuckGo HTML search
   - Secondary: News-specific searches
   - Tertiary: Government contract databases (USAspending, SAM.gov)

2. **Search Query Optimization**
   ```python
   search_queries = [
       # Specific transaction queries
       f'"{entity_name}" acquisition announcement',
       f'"{entity_name}" contract award news',
       f'"{entity_name}" merger deal value',
       
       # Government contract queries
       f'"{entity_name}" USAspending contract',
       f'"{entity_name}" federal award',
       
       # News queries
       f'"{entity_name}" M&A news',
       f'"{entity_name}" investment announcement',
   ]
   ```

3. **Result Deduplication**
   - Remove duplicate URLs across queries
   - Merge information from multiple results about same transaction

4. **Source Prioritization**
   - Prioritize official announcements (SEC filings, press releases)
   - Secondary: News articles from reputable sources
   - Tertiary: Aggregator sites (Tracxn, Crunchbase, etc.)

**Files to Modify**:
- `data/scripts/enrich_entity_flows.py` - Enhance search strategies

---

### Phase 7: Materials Transfer Tracking

**Goal**: Extend system to track non-financial flows (materials, technology, personnel)

**Tasks**:

1. **Materials Transfer Keywords**
   ```python
   materials_keywords = [
       'technology transfer', 'material transfer', 'equipment',
       'prototype', 'hardware', 'software', 'license',
       'patent', 'intellectual property', 'IP transfer',
       'subcontract', 'supply agreement', 'procurement'
   ]
   ```

2. **New Relationship Types**
   - Technology Transfer
   - Material Supply
   - Equipment Procurement
   - IP Licensing
   - Subcontract

3. **Materials Flow Schema**
   ```python
   class MaterialsFlow:
       source: str
       target: str
       material_type: str  # technology, equipment, IP, etc.
       description: str
       date: date
       source_citation: str
   ```

4. **Database Schema Update**
   - Add `materials_flows` table
   - Or extend `money_flows` with `flow_type` field

**Files to Create**:
- `data/scripts/extract_materials_flows.py` - Materials extraction
- Update `backend/database.py` - Add materials flow model

---

## Implementation Timeline

### Week 1: Foundation
- [ ] Phase 1: Enhanced Target Entity Extraction
- [ ] Install NLP dependencies (spaCy)
- [ ] Implement pattern-based extraction
- [ ] Test on sample entities

### Week 2: Data Quality
- [ ] Phase 2: Improved Amount Extraction
- [ ] Phase 3: Date Extraction
- [ ] Install date parsing dependencies
- [ ] Test extraction accuracy

### Week 3: Filtering & Validation
- [ ] Phase 4: Specificity Filtering
- [ ] Phase 5: Quality Gates
- [ ] Create validation module
- [ ] Test quality gates

### Week 4: Enhancement
- [ ] Phase 6: Enhanced Search Strategies
- [ ] Phase 7: Materials Transfer Tracking
- [ ] Full system testing
- [ ] Production deployment

---

## Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Target Entity Identification | 0% | >80% | % of flows with valid target |
| Amount Extraction | 0% | >50% | % of flows with amount |
| Date Extraction | 0% | >50% | % of flows with date |
| Overall Quality Score | 40% | >80% | Combined validation score |
| Duplicate Rate | N/A | <5% | % of flows that are duplicates |
| False Positive Rate | N/A | <10% | % of flows that are incorrect |

---

## Dependencies to Install

```bash
pip install spacy
python -m spacy download en_core_web_sm
pip install rapidfuzz
pip install dateparser
pip install validators
```

---

## File Structure After Implementation

```
data/scripts/
├── enrich_entity_flows.py      # Main enrichment script (enhanced)
├── extract_materials_flows.py  # Materials transfer extraction
├── validate_flows.py           # Validation module
├── review_queue.py             # Human review interface
├── entity_recognition.py       # NER and entity matching
├── amount_extraction.py        # Amount parsing utilities
├── date_extraction.py          # Date parsing utilities
└── .cache/                     # Search result cache
```

---

## Risk Mitigation

1. **Rate Limiting**: Implement exponential backoff for search requests
2. **Data Quality**: Always require human review for first batch
3. **Duplicates**: Check against database before any import
4. **False Positives**: Conservative extraction (prefer missing data over wrong data)
5. **API Changes**: Abstract search providers for easy switching

---

## Next Steps

1. Review and approve this plan
2. Install required dependencies
3. Implement Phase 1 (Target Entity Extraction)
4. Test on sample entities
5. Iterate based on results
6. Proceed to subsequent phases

---

## Appendix: Test Commands

```bash
# Run enrichment test
python test_enrichment.py

# Review results
python review_enrichment.py

# Check existing flows
python check_existing_flows.py

# Full enrichment (after improvements)
python run_enrichment.py
```
