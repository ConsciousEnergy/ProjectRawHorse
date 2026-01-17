# MITRE Corporation Contract Added

## Summary

Added the $1.9B US Air Force contract awarded to MITRE Corporation to the money flows dataset.

## Contract Details

- **Source**: US Air Force
- **Target**: MITRE Corporation  
- **Relationship**: Contract
- **Amount**: $1,884,824,707.00 (approximately $1.9 billion)
- **Start Date**: 2025-10-01
- **End Date**: 2028-09-30
- **Contract Type**: National Security Engineering Center (NSEC) Services
- **Award ID**: FA870225CB001
- **Funding Agency**: Department of the Air Force
- **Funding Office**: AFRL RYD
- **Citation**: https://orangeslices.ai/mitre-awarded-1-9b-us-air-force-national-security-engineering-center-nsec-services-contract/

## Data Added

The contract has been added to `data/financial/money_flows.csv` with:
- Edge ID: `62ddc5e72a685019`
- Normalized source: `US AIR FORCE`
- Normalized target: `MITRE CORPORATION`
- Source file: `manual_addition.csv`

## Notes

- This is a 3-year contract covering National Security Engineering Center services
- Contract was awarded in August 2025
- MITRE Corporation is a not-for-profit organization operating federally funded R&D centers
- The contract leverages MITRE's expertise in defense, cybersecurity, and homeland security

## Next Steps

To load this data into the database:
1. The data is already in the CSV file
2. Run the data loader to import it: `python combine_all_data.py`
3. Or use the backend API to load money flows
