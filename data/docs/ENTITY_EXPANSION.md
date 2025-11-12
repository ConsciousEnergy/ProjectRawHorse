# Entity Expansion Beyond DOE

Generated: 2025-11-09T18:28:48.070285 UTC

## New outputs & tools
- Consolidated seeds → `processed/entities_seeds_extended.csv`
- Agency targets → `lookups/agency_targets.json`
- Multi-agency USAspending fetcher/normalizer → `scripts/fetch_usaspending_multiagency.py`, `scripts/normalize_usaspending_multiagency.py`
- Bulk SAM entity fetcher → `scripts/fetch_sam_entities_bulk.py`

## Usage
```bash
# Pull awards across many agencies using your keyword list
python scripts/fetch_usaspending_multiagency.py \
  --endpoint_base https://api.usaspending.gov \
  --keywords_file lookups/keywords_deduped.txt \
  --agencies_json lookups/agency_targets.json \
  --out_dir external/usaspending_multiagency \
  --min_action_date 2019-01-01 --pages 2

python scripts/normalize_usaspending_multiagency.py \
  --in_dir external/usaspending_multiagency \
  --out_csv processed/awards_multiagency.csv

# (Optional) SAM entity enrichment by name (requires SAM_API_KEY)
cut -d, -f1 processed/entities_seeds_extended.csv > lookups/entity_names.csv
python scripts/fetch_sam_entities_bulk.py \
  --api_base https://api.sam.gov/entity-information/v2 \
  --api_key "$SAM_API_KEY" \
  --names_csv lookups/entity_names.csv \
  --out_dir external/sam_bulk --pages 1
```

## Next steps
- Map SAM entity fields → `processed/entities.csv` for stronger joins.
- Feed `awards_multiagency.csv` into the existing scorers to expand beyond DOE.
- Add IARPA/DARPA/NSF/NIH SBIR pulls for dual-use signals.
