# Data Refactoring Plan

**Date:** 2025-11-11  
**Objective:** Consolidate redundant data files into unified, clean structure

## Identified Redundancies

### 1. Entities Folder (7 files → 5 files)

**Current Issues:**
- `entities.csv` (11 lines) vs `uap_entities_master_2025-11-06.csv` (31 lines) - Different schemas
- Multiple identifier files with overlapping data
- Dates in filenames make versioning unclear

**Consolidation Plan:**
```
KEEP (Consolidated):
✅ entities_master.csv           [Merge: entities.csv + uap_entities_master_2025-11-06.csv]
✅ entity_identifiers.csv         [Merge: uap_entity_identifiers_2025-11-06.csv + enriched2]
✅ entity_relationships.csv       [Rename: uap_entity_edges.csv]
✅ entities_seeds.csv             [Rename: entities_seeds_extended.csv]
✅ entities_orphaned.csv          [Rename: uap_orphan_entities_2025-11-06.csv]

ARCHIVE:
📦 entities.csv                   [Merged into entities_master.csv]
📦 uap_entities_master_2025-11-06.csv [Merged into entities_master.csv]
📦 uap_entity_identifiers_2025-11-06.csv [Merged]
📦 uap_entity_identifiers_enriched2_2025-11-06.csv [Merged]
📦 uap_entity_edges.csv          [Renamed]
📦 uap_orphan_entities_2025-11-06.csv [Renamed]
```

### 2. Financial Folder (15 files → 9 files)

**Current Issues:**
- Multiple award files with overlapping data
- 4 versions of money_edges (v3, clean, new, new_conf) - confusing
- Dated filenames throughout

**Consolidation Plan:**
```
KEEP (Consolidated):
✅ awards_master.csv              [Use: awards_enriched.csv - most complete]
✅ awards_usaspending.csv         [Merge: usaspending files]
✅ solicitations.csv               [Keep as-is]
✅ money_flows.csv                 [Use: uap_money_edges_clean_2025-11-06.csv - most complete]
✅ money_flows_veritas_peraton.csv [Rename: uap_money_flows_veritas_peraton_v3.csv]
✅ federal_flows_by_agency.csv    [Rename: federal_flows_rollup_agency_total_2025-11-06.csv]
✅ federal_flows_by_recipient.csv [Rename: federal_flows_rollup_agency_recipient_fy_2025-11-06.csv]
✅ federal_agency_peraton.csv     [Rename: federal_edges_agency_to_peraton_2025-11-06.csv]
✅ fiscal_year_totals.csv         [Rename: fy_totals_2025-11-06.csv]

ARCHIVE:
📦 awards.csv                     [Basic version, superseded by enriched]
📦 awards_flat_2025-11-06.csv    [Superseded by awards_enriched]
📦 uap_money_edges_v3.csv        [Superseded by clean version]
📦 uap_money_edges_new_2025-11-06.csv [Older version]
📦 uap_money_edges_new_conf_2025-11-06.csv [Older version]
📦 usaspending_car_intake_master_2025-11-06.csv [Will merge]
📦 usaspending_car_intake_seeds_expanded_2025-11-06.csv [Will merge]
```

### 3. FOIA Folder (18 files → 16 files)

**Current Issues:**
- CSV and XLSX of same queue data
- Many template files (good, keep all)

**Consolidation Plan:**
```
KEEP:
✅ foia_queue.csv                 [Primary format - easier to process]
✅ foia_queue_top10.csv          [Rename: foia_queue_prefilled_top10.csv]
✅ foia_targets.csv               [Rename: uap_foia_targets_v1.csv]
✅ foia_templates/                [NEW: Move all 14 FOIA_*.txt files here]
   ├── advanced_ceramic_fibers.txt
   ├── aegis_technologies.txt
   ├── hypres.txt
   [etc... 14 templates total]
✅ foia_template_generic.txt     [Rename: foia_request_template_procurement_security.txt]

ARCHIVE:
📦 foia_queue_2025-11-06.xlsx    [Excel version - keep CSV only]
```

### 4. Reference Folder (7 files → 7 files)

**Current Status:** ✅ Already well-organized
- No redundancy found
- Clear naming conventions
- All files serve distinct purposes

**Keep as-is:**
```
✅ ffrdc_lookup_master.csv
✅ ffrdc_uarc_search_kits_full.csv
✅ keywords_deduped.txt
✅ keyword_weights.csv
✅ mission_rollup.csv             [Remove date: mission_rollup_2025-11-06.csv]
✅ advisors_fees.csv              [Rename: uap_advisors_fees_scaffold_v1.csv]
✅ veritas_lps.csv                [Rename: uap_veritas_lps_v1.csv]
```

### 5. Evidence Folder (2 files → 1 file)

**Current Issues:**
- CSV and XLSX of same data

**Consolidation Plan:**
```
KEEP:
✅ evidence_bundle.csv            [Primary format]

ARCHIVE:
📦 evidence_bundle_2025-11-06.xlsx [Excel version - keep CSV only]
```

## New Unified Structure

```
data/
├── entities/
│   ├── entities_master.csv          # All entities with full metadata
│   ├── entity_identifiers.csv       # UEI, DUNS, CAGE codes
│   ├── entity_relationships.csv     # Entity-to-entity edges
│   ├── entities_seeds.csv           # Seed data for expansion
│   └── entities_orphaned.csv        # Entities without connections
│
├── financial/
│   ├── awards_master.csv            # All awards (enriched with scoring)
│   ├── awards_usaspending.csv       # USAspending-specific data
│   ├── solicitations.csv            # Federal solicitations
│   ├── money_flows.csv              # All money flow edges
│   ├── money_flows_veritas_peraton.csv  # Specific flow analysis
│   ├── federal_flows_by_agency.csv  # Agency rollup
│   ├── federal_flows_by_recipient.csv   # Recipient rollup
│   ├── federal_agency_peraton.csv   # Agency-Peraton connections
│   └── fiscal_year_totals.csv      # FY summaries
│
├── foia/
│   ├── foia_queue.csv               # All FOIA requests in queue
│   ├── foia_queue_top10.csv        # Priority requests
│   ├── foia_targets.csv             # Target agencies/entities
│   ├── foia_template_generic.txt   # Generic template
│   └── templates/                   # 14 entity-specific templates
│       ├── advanced_ceramic_fibers.txt
│       ├── aegis_technologies.txt
│       └── ...
│
├── reference/
│   ├── ffrdc_lookup_master.csv
│   ├── ffrdc_uarc_search_kits_full.csv
│   ├── keywords_deduped.txt
│   ├── keyword_weights.csv
│   ├── mission_rollup.csv
│   ├── advisors_fees.csv
│   └── veritas_lps.csv
│
├── evidence/
│   └── evidence_bundle.csv          # Comprehensive evidence
│
├── visualizations/                   # No changes - all unique
├── scripts/                          # No changes - all unique
├── docs/                             # No changes - all unique
│
└── _archive/                         # OLD FILES MOVED HERE
    ├── 2025-11-06_migration/
    │   ├── entities/
    │   ├── financial/
    │   ├── foia/
    │   └── ...
    └── README.md                     # Archive documentation
```

## Benefits of Refactoring

### 1. Clarity
- ✅ No more version suffixes (v1, v2, v3)
- ✅ No more date stamps in filenames
- ✅ Clear, descriptive names
- ✅ One primary file per data type

### 2. Simplicity
- ✅ 74 files → ~48 active files
- ✅ 26 files archived (35% reduction)
- ✅ No duplicate formats (CSV only, no XLSX)
- ✅ Organized templates in subfolder

### 3. Maintainability
- ✅ Version control through Git, not filenames
- ✅ Clear upgrade path for data updates
- ✅ Easy to identify which file to use
- ✅ Consistent naming conventions

### 4. Application Integration
- ✅ Simplified data loader configuration
- ✅ Clear mapping to API endpoints
- ✅ Predictable file locations
- ✅ No confusion about "which version to use"

## Naming Conventions

### File Naming Rules
1. **Descriptive names:** `entities_master.csv` not `entities.csv`
2. **No dates:** Use Git for versioning, not filenames
3. **No versions:** Use Git tags, not v1/v2/v3
4. **Underscores:** Use `_` for word separation
5. **Lowercase:** All filenames lowercase
6. **CSV primary:** Use CSV as primary format, archive Excel files

### Examples
- ❌ `uap_entities_master_2025-11-06.csv`
- ✅ `entities_master.csv`

- ❌ `uap_money_edges_v3.csv`
- ✅ `money_flows.csv`

- ❌ `federal_flows_rollup_agency_total_2025-11-06.csv`
- ✅ `federal_flows_by_agency.csv`

## Implementation Steps

1. ✅ Create `_archive` directory
2. ✅ Create `foia/templates` subdirectory
3. ⏳ Consolidate entity files
4. ⏳ Consolidate financial files
5. ⏳ Organize FOIA templates
6. ⏳ Rename reference files
7. ⏳ Update config.yaml with new filenames
8. ⏳ Update data README.md
9. ⏳ Update data_loader.py to use new structure
10. ⏳ Test data loading with new structure
11. ⏳ Archive old files

## Data Integrity

### Validation Checklist
- ✅ All data preserved (no deletion, only archival)
- ⏳ Row counts verified pre/post consolidation
- ⏳ Schema compatibility checked
- ⏳ No data loss during merging
- ⏳ Archive contains all original files
- ⏳ Git history preserved

## Rollback Plan

If issues arise:
1. All original files preserved in `_archive/`
2. Git commit allows easy revert
3. Archive README documents original structure
4. Can restore from archive in < 5 minutes

## Timeline

- **Analysis:** ✅ Complete
- **Planning:** ✅ Complete
- **Implementation:** ⏳ In Progress (30 minutes est.)
- **Testing:** ⏳ Pending (15 minutes est.)
- **Documentation:** ⏳ Pending (10 minutes est.)

**Total Estimated Time:** ~1 hour

---

**Status:** 📋 PLAN COMPLETE - Ready for implementation
