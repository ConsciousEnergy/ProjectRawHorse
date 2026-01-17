# Date Range Calculation Fix

## Issue
The dashboard was only showing date ranges from 2004-2023, but the dataset includes:
- FOIA targets with timeframes going back to 1949
- Historical programs and events
- Future/present date ranges

## Solution
Updated the date range calculation in `/api/stats` to include:

1. **Money Flows**: `start_date` field (2004-2023)
2. **Awards**: `action_date` field (when available)
3. **FOIA Targets**: Parsed from `timeframe` field

### FOIA Timeframe Parsing
The system now extracts years from FOIA target timeframes in various formats:
- **"1949-1951"** → Extracts 1949 and 1951
- **"2003-present"** → Extracts 2003
- **"1980s-present"** → Extracts 1980
- **"1990s-2000s"** → Extracts earliest year

### Implementation
The date range calculation:
1. Queries all date fields from money flows and awards
2. Parses years from FOIA target timeframes using regex
3. Combines all dates to find the overall min/max range
4. Displays the full range on the dashboard

## Result
The dashboard now shows the complete date range covering all data sources, including historical FOIA targets dating back to 1949.

## Testing
To verify the date range:
```bash
python check_date_ranges.py
```

This will show:
- Date ranges from each data source
- Combined overall date range
- Total records per source
