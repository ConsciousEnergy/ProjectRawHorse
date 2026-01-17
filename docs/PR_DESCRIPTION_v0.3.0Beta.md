# Pull Request: v0.3.0 Beta - Data Scraping Infrastructure & Sankey Visualization

## Summary

This PR introduces comprehensive data scraping infrastructure, new visualizations, and significant enhancements to data quality and management systems for Project RawHorse v0.3.0 Beta.

## New Features

### Data Scraping Infrastructure
- **SEC EDGAR Scraper**: Fetches 8-K, 10-K, 10-Q, DEF 14A, and Form 4 filings for financial flow discovery
- **FOIA Reading Room Scraper**: Scrapes 6 major agency FOIA libraries (DoD, DOE, NASA, DHS, NRO, NGA)
- **Congressional Records Fetcher**: Searches GAO reports and Congressional hearing transcripts
- **Press Release Aggregator**: Collects announcements from PR Newswire and Business Wire
- **Court Records Fetcher**: Uses RECAP/CourtListener for bid protests and contractor disputes
- **State Corporate Filings Template**: Framework for DE, VA, MD, NV corporate data
- **Legal Compliance Filter**: 20+ restricted keyword detection for classified/restricted content

### Visualizations
- **Interactive Sankey Diagram**: D3.js-based visualization for financial and material flows
  - Filtering and highlighting capabilities
  - Zoom and pan functionality
  - Integrated into Analysis page

### Data Quality Systems
- **FOIA Quality Scoring**: Specificity, likelihood, and priority scoring for FOIA targets
- **Source Credibility Weighting**: 4-tier system (0.9-1.0 for .gov/.mil, 0.7-0.9 for major news, etc.)
- **Entity Flow Enrichment Pipeline**: 
  - Named Entity Recognition (spaCy)
  - Improved amount and date extraction
  - Specificity filtering and quality gates

### Infrastructure
- **Data Versioning System**: Tracks data changes and triggers frontend refreshes
- **MaterialsFlow Database Model**: Tracks non-financial transfers (technology, equipment, IP)
- **Improved Data Loader**: Duplicate detection and enhanced entity loading

## Breaking Changes

None. All changes are backward compatible.

## Testing Performed

- ✅ Compliance filter tested with restricted keywords
- ✅ Source credibility scoring verified (USAspending.gov = 0.95)
- ✅ Database models accessible and functional
- ✅ All scrapers include compliance checks
- ✅ Frontend build assets updated and tested

## Files Changed

### New Files (30+)
- 7 data scraper modules (`data/scripts/fetch_*.py`)
- Compliance filter (`data/scripts/compliance_filter.py`)
- Enrichment pipeline modules (4 files)
- Sankey diagram component and styles
- Data context and refresh button components
- 21 documentation files

### Modified Files
- Database schema (`backend/database.py`)
- Data loader (`backend/data_loader.py`)
- API routers (`backend/routers/data.py`, `backend/routers/analysis.py`)
- Frontend pages and components
- Frontend build assets

## Documentation

Comprehensive documentation added:
- Scraping implementation summary and quick start guide
- Enrichment guides and improvement plans
- FOIA quality system documentation
- Verification reports and progress tracking

## Next Steps

1. Review and test all new scrapers
2. Verify compliance filter effectiveness
3. Test Sankey diagram with production data
4. Monitor data refresh system performance
5. Plan for production deployment

## Related Issues

- Implements data scraping expansion plan
- Addresses need for automated data collection
- Enhances visualization capabilities
- Improves data quality assessment

---

**Ready for Review**: This PR is ready for code review and testing before merging to main.
