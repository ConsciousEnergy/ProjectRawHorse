# Project RawHorse v0.2.1-alpha Release Notes

**Release Date:** November 11, 2025  
**Version:** v0.2.1-alpha  
**Previous Version:** v0.2.0-alpha  
**Repository:** https://github.com/ConsciousEnergy/ProjectRawHorse

---

## 📊 Patch Release: Data Expansion

Quick patch release to expand the entity database with defense contractors and government agencies referenced in relationships.

---

## ✨ What's New

### 🗃️ Expanded Entity Database

**Entity Count:**
- **Before:** 9 entities
- **After:** 22 entities
- **Increase:** +144%

**New Entities Added (13):**

**Defense Contractors (8):**
- Lockheed Martin EIG
- The SI Organization
- QinetiQ North America SSG
- Vencore
- Perspecta
- Peraton
- Northrop Grumman Federal IT/MSS
- Arcfield

**Government Agencies (3):**
- NGA (National Geospatial-Intelligence Agency)
- DCSA (Defense Counterintelligence and Security Agency)
- TSA (Transportation Security Administration)

**Investment Firms (1):**
- Veritas Capital

**Individuals (1):**
- Robert Cardillo (Former NGA Director)

---

## 📈 Entity Type Distribution

| Entity Type | Count |
|-------------|-------|
| Corporation | 15 |
| Government Agency | 3 |
| Investment Firm | 1 |
| Individual | 1 |
| Organization | 1 |
| Research Institution | 1 |
| **Total** | **22** |

---

## 🎯 Why This Matters

### Data Completeness
- All entities referenced in relationships now exist in the database
- No more "orphan" references
- Proper entity type classification for all

### Network Visualization
- Graph still shows 13 nodes (entities with relationships)
- All graph nodes now have full entity records
- Accurate type inference and classification

### Future Growth
- Foundation for adding more UAP-related contractors
- Clear entity typing for analysis
- Ready for relationship expansion

---

## 🔧 Technical Details

### Files Modified
- `data/entities/entities_master.csv` - Added 13 new entities

### Database Changes
- Entity table: 9 → 22 rows (+144%)
- All entities now properly typed
- Source tracking: entity_relationships.csv

### No Breaking Changes
- Existing functionality unchanged
- Graph visualization works as before
- All API endpoints compatible

---

## 🚀 Upgrade Guide

### From v0.2.0-alpha to v0.2.1-alpha

**Automatic Upgrade:**
```bash
cd project_rawhorse
git pull origin main
del data\prh.db
.\RUN.bat
```

The database will automatically rebuild with 22 entities on first run.

**No code changes required!** This is purely a data expansion.

---

## 🎊 Combined v0.2.0 + v0.2.1 Achievements

Since v0.1.1-alpha, Project RawHorse now has:

**Features:**
- ✅ Interactive network visualization
- ✅ Advanced filtering (type, amount, date)
- ✅ Complete contribution system (4 types)
- ✅ 7 critical bug fixes

**Data:**
- ✅ 22 entities (+144% from v0.1.1)
- ✅ 6 entity types
- ✅ 15 relationships
- ✅ 100% entity classification

**Quality:**
- ✅ Professional UX
- ✅ Zero console errors
- ✅ Comprehensive documentation
- ✅ Production-ready code

---

## 📋 What's Next?

See `docs/NEXT_ACTION_PLAN.md` for detailed roadmap.

**v0.3.0-alpha priorities:**
1. Cross-platform executables (PyInstaller)
2. Financial flow visualizations
3. Timeline charts
4. Statistical dashboards

---

## 🙏 Acknowledgments

**Data Sources:**
- UAP research community
- Entity relationship analysis
- Federal procurement records

---

## 📞 Get Involved

**Repository:** https://github.com/ConsciousEnergy/ProjectRawHorse

**Support:**
- ⭐ Star us on GitHub
- 🐛 Report issues
- 💡 Suggest features
- 🤝 Contribute data
- 💰 Sponsor: https://conscious.energy/donations/

---

**For v0.2.0 features, see:** `RELEASE_NOTES_v0.2.0.md`

**Happy Researching!** 🎉  
*Project RawHorse v0.2.1-alpha*

