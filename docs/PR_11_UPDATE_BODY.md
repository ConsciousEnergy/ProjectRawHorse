# PR #11 Update: Description for Manual Edit

Use this content to update the PR description at https://github.com/ConsciousEnergy/ProjectRawHorse/pull/11

---

## New Section to Add: Search Quality Fixes (v0.4.0)

Add the following under "Future Enhancements" or as a new section "Search Quality Fixes (Implemented)":

### Search Quality Fixes

- **Multi-word search**: "National Geospatial" now finds NGA via tokenized AND conditions
- **Multi-scale amount search**: "223" searches $223, $223K, and $223M ranges plus text in descriptions
- **Always-on fuzzy matching**: WRatio scorer, lower cutoff (55) for short queries, TTL-cached name lists
- **"Did you mean?" suggestions**: Zero-result searches return top 3 suggestions from entity names
- **Browse multi-token highlighting**: "National Geospatial" highlights both words separately

### Updated Performance Metrics (expected)

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Search Success Rate | 50% | Improved | > 80% |
| Zero-Result Rate | 50% | Reduced | < 20% |

---

## Mark PR Ready for Review

Once CI passes, mark the PR as ready for review (out of draft) at:
https://github.com/ConsciousEnergy/ProjectRawHorse/pull/11

If `gh` CLI is installed and authenticated:
```
gh pr ready 11
```
