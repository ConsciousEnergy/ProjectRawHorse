# UAP Data Integrity Profile
- Date: 2025-11-06
- Loaded files: uap_money_flows_veritas_peraton_v3.csv, uap_money_edges_v3.csv, uap_veritas_lps_v1.csv, uap_entity_edges.csv, uap_money_flows_veritas_peraton_v2.csv, uap_advisors_fees_scaffold_v1.csv, uap_foia_targets_v1.csv

## Source File Profiles
### uap_money_flows_veritas_peraton_v3.csv
- Rows: 25
- Columns: date, type, parties, amount_usd, summary, source, category, confidence, uap_relevance, source_type

### uap_money_edges_v3.csv
- Rows: 14
- Columns: source, target, amount_usd, date, type, source_link, summary

### uap_veritas_lps_v1.csv
- Rows: 3
- Columns: lp_name, fund, commitment_usd, decision_date, source, notes, confidence

### uap_entity_edges.csv
- Rows: 15
- Columns: source, target, label

### uap_money_flows_veritas_peraton_v2.csv
- Rows: 18
- Columns: date, type, parties, amount_usd, summary, source

### uap_advisors_fees_scaffold_v1.csv
- Rows: 5
- Columns: deal, close_date, buyer, seller, advisors_buyer, advisors_seller, reported_fees_usd, source, notes, confidence

### uap_foia_targets_v1.csv
- Rows: 5
- Columns: agency, record_request, timeframe, relevance, notes
