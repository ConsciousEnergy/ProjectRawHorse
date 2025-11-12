# Credibility & Scoring Rubric

Generated: 2025-11-09T17:09:39.265453 UTC

We compute a **credibility_score** in [0,1] for contracts/awards and solicitations. It is **heuristic and transparent**.

## Awards
- +0.40 if source is official federal feed (USAspending/SAM/FPDS); +0.40 if .gov/.mil AARO; else +0.20
- +0.20 if PIID present; +0.05 if Mod also present
- +0.15 if Recipient UEI present; +0.10 if only DUNS/CAGE
- +0.10 if action_date is parseable
- +0.05 if value is numeric
- +min(0.05 * keyword_hits, 0.20) based on keyword matches in description

## Solicitations
- +0.30 if source is SAM/.gov
- +0.20 if posted_date present
- +0.10 each for NAICS, PSC/classification, and agency
- +min(0.05 * keyword_hits, 0.20)

These weights are tunable in code. They favor provenance and consistent identifiers.
