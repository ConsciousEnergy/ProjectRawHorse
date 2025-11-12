# USAspending (Weighted) + Integrated Pipeline

Generated: 2025-11-09T17:57:46.907981 UTC

## Weighted USAspending
```bash
python scripts/fetch_usaspending_weighted.py   --endpoint_base https://api.usaspending.gov   --keywords_file lookups/keywords_deduped.txt   --weights_file lookups/keyword_weights.csv   --out_dir external/usaspending_weighted   --min_action_date 2019-01-01 --base_pages 2 --max_pages 8

python scripts/normalize_usaspending_weighted.py   --in_dir external/usaspending_weighted   --out_csv processed/awards_from_usaspending_weighted.csv
```

## Integrated scoring & joins (incl. ARPA-E)
```bash
python scripts/score_join_integrated.py   --entities processed/entities.csv   --sbir processed/sbir_awards_doe.csv   --research_outputs processed/research_outputs.csv   --arpae_projects processed/arpae_projects.csv   --forecast processed/solicitations_doe_forecast.csv   --out_dir processed/integrated
```

Outputs:
- `processed/integrated/sbir_scored.csv`
- `processed/integrated/research_outputs_scored.csv`
- `processed/integrated/arpae_projects_scored.csv`
- `processed/integrated/pipeline_candidates.csv`

## Dashboard (React)
Component saved at:
- `apps/viz/doe_pipeline_dashboard.tsx`

Load your CSVs via the UI to browse candidates, scored SBIR/OSTI/ARPA-E rows, and a NAICS summary.
