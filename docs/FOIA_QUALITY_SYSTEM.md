# FOIA Target Quality Scoring System

## Overview

The FOIA target quality scoring system evaluates each FOIA request based on three key metrics to help prioritize and assess the likelihood of successful responses.

## Quality Metrics

### 1. Specificity Score (0-1)
Measures how specific and well-defined the FOIA request is.

**Scoring Factors:**
- **Specific Dates** (+0.3): Request includes specific date ranges (e.g., "1949-1951", "2010")
- **Specific Programs** (+0.3): References named programs, projects, or operations
- **Specific Record Types** (+0.2): Specifies document types (memos, contracts, testimony, etc.)
- **Specific Amounts** (+0.1): References specific dollar amounts
- **Specific Personnel** (+0.1): Names specific individuals

**Penalties:**
- Vague language (multiple vague terms) reduces score by 30%

**Score Ranges:**
- High (≥0.7): Very specific, well-defined request
- Medium (0.4-0.7): Moderately specific
- Low (<0.4): Vague or overly broad request

### 2. Likelihood Score (0-1)
Estimates the probability of receiving a response based on agency and request characteristics.

**Base Scores by Agency:**
- **High Likelihood (≥0.6):**
  - AARO: 0.7 (public-facing office)
  - GSA: 0.8 (public records)
  
- **Medium Likelihood (0.3-0.6):**
  - DARPA: 0.5
  - DHS: 0.6
  - DCSA: 0.5
  - DoD: 0.5
  - US Army: 0.5
  - DOE: 0.4
  - NGA: 0.4
  
- **Low Likelihood (<0.3):**
  - NRO: 0.3 (highly classified)
  - CIA/CIA DS&T: 0.2 (highly classified)
  - DOE OICI/DOE NEST: 0.3
  - DARPA SID: 0.4
  - MITER Corporation: 0.3 (FFRDC)
  - OUSD/DDNI ATNF: 0.3-0.4

**Adjustments:**
- **Older Records** (+0.1): Records from before 2000 may have better release rates
- **Current Records** (-0.1): Ongoing or "present" records less likely to be released
- **High Classification** (-0.2): References to classified, SAP, or legacy programs
- **Public/Declassified** (+0.1): References to public or declassified records

**Score Ranges:**
- High (≥0.6): Good chance of response
- Medium (0.3-0.6): Moderate chance
- Low (<0.3): Low chance of response

### 3. Priority Score (0-1)
Measures the overall importance and research value of the request.

**Scoring Factors:**
- **Direct Connection** (+0.3): Direct connection to UFO legacy programs
- **Crash Retrieval** (+0.3): Related to crash retrieval operations
- **Material Transfer** (+0.2): Technology or material transfer
- **Classification Systems** (+0.1): Classification controls and oversight
- **Funding Mechanisms** (+0.1): Funding or misappropriation
- **Verified Sources** (+0.1): Based on testimony or verified sources

**Score Ranges:**
- High (≥0.7): Critical priority for research
- Medium (0.4-0.7): Important but not critical
- Low (<0.4): Lower priority

## Current Statistics

As of the latest analysis:
- **Total FOIA Targets**: 185
- **High Priority** (≥0.7): 12 targets
- **Medium Priority** (0.4-0.7): 0 targets
- **Low Priority** (<0.4): 173 targets

- **High Specificity** (≥0.7): 8 targets
- **Medium Specificity** (0.4-0.7): 6 targets
- **Low Specificity** (<0.4): 1 target

- **High Likelihood** (≥0.6): 0 targets
- **Medium Likelihood** (0.3-0.6): 7 targets
- **Low Likelihood** (<0.3): 8 targets

## Usage

### In Database
Quality scores are stored in the `foia_targets` table:
- `specificity_score`: Float (0-1)
- `likelihood_score`: Float (0-1)
- `priority_score`: Float (0-1)
- `quality_notes`: Text (explanation of scores)

### In Frontend
The Browse page displays quality scores as color-coded badges:
- **Green**: High score
- **Orange**: Medium score
- **Gray**: Low score

### Filtering
You can filter FOIA targets by:
- Priority score (high/medium/low)
- Specificity score
- Likelihood score

## Recommendations

1. **Focus on High Priority Targets**: Start with the 12 high-priority targets (priority ≥ 0.7)
2. **Improve Low Specificity Requests**: Refine vague requests to increase specificity scores
3. **Consider Likelihood**: Balance priority with likelihood - high priority but very low likelihood may need refinement
4. **Combine Related Requests**: Group related requests to increase specificity and likelihood

## Updating Scores

Scores can be recalculated by running:
```bash
python update_foia_scores.py
```

This will update all FOIA targets in the database with current quality scores based on their current data.
