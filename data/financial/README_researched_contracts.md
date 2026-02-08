# Researched FFRDC / Prime Contract Flows

`researched_contracts_ffrdc_primes.csv` is loaded by the data pipeline as money flows. It contains targeted research on contracts for key entities from the Enrichment plan:

- **IDA (Institute for Defense Analyses)**: DoD FFRDC; $180M modification (Jan 2024), contract ceiling ~$1.13B (Defense.gov, GovCon Wire).
- **RAND Corporation**: DoD policy research; search USAspending.gov and RAND Annual Report for amounts.
- **Aerospace Corporation**: FFRDC support to Space Force/NRO; see NSF FFRDC R&D Survey, Aerospace.org annual report.
- **Battelle / Oak Ridge, Sandia**: DOE M&O contracts; see DOE and lab websites.
- **SAIC**: Legacy contracts post-Leidos split; USAspending.gov.

To add or update rows: use the same columns as `money_flows.csv` (source, target, relationship, amount_usd, start_date, end_date, source_citation, edge_id). Run **Data refresh** in the app or reload the database to ingest changes.
