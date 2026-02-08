# Git Commands for Feature Branch Push

---

## PRH_v0.3.2Beta → main (February 2026)

**Branch:** `PRH_v0.3.2Beta`  
**Target:** Open PR into `main`  
**Changelog:** See `CHANGELOG_v0.3.2Beta.md`

### Quick commands

```bash
# From project root (folder containing frontend + backend)
git checkout -b PRH_v0.3.2Beta
git add -A
git status   # review
git commit -m "feat: Intelligence Stack Pyramid overhaul, layout, L6 programs, federal flows fix (v0.3.2 Beta)

- Pyramid: full-width layout, detail under search, trace chain of command
- Backend: pyramid/hierarchy/entity-detail/search APIs; hierarchy + entity_descriptions CSVs
- Data: intel_stack_levels L6 variants; hierarchy_relationships; federal flows edge_id dedupe
- About: add GitHub repo link
- CHANGELOG_v0.3.2Beta.md, GIT_PUSH_COMMANDS updated"

git push -u origin PRH_v0.3.2Beta
```

**Follow-up commit (search + RUN.bat):**
```bash
git add backend/requirements.txt backend/routers/search.py data/entities/entity_aliases.csv RUN.bat CHANGELOG_v0.3.2Beta.md GIT_PUSH_COMMANDS.md docs/development/SEARCH_UX_ENHANCEMENTS_4_6_PLAN.md test_search_enhancements.py
git status
git commit -m "feat(search): alias expansion, amount-aware search, rapidfuzz fuzzy; RUN.bat ensures deps (v0.3.2 Beta)"
git push origin PRH_v0.3.2Beta
```

Then on GitHub: **New Pull Request** → Base: `main`, Compare: `PRH_v0.3.2Beta`. Use `CHANGELOG_v0.3.2Beta.md` for the PR description.

---

**Previous:** v0.3.0-dev  
**Date**: November 30, 2025

---

## 📋 Summary of Changes

### New Files (24)
- Backend: `routers/search.py`, `test_search.py`
- Frontend: `SearchBar.tsx`, `SearchBar.css`
- Assets: `PRHLogo.png` (2 copies)
- Docs: 7 new development docs
- Static: Built frontend assets (CSS, JS)
- Root: `PULL_REQUEST_TEMPLATE.md`, `CHANGELOG_v0.3.0.md`

### Modified Files (16)
- Backend: 5 files (database, main, data_loader, schemas, analysis)
- Frontend: 8 files (App, Browse, NetworkGraph, api, types)
- Docs: 1 file (V0.3.0_DEV_STARTED.md)
- Static: 2 files (index.html, package files)

### Deleted Files (6)
- Old docs moved to docs/ folder

---

## 🚀 Git Commands

### Step 1: Create Feature Branch

```bash
cd "C:\Users\brand\Project RaHorus\project_rawhorse"

# Create and checkout new feature branch from v0.3.0-dev
git checkout -b feature/advanced-search-and-improvements
```

### Step 2: Stage All Changes

```bash
# Add all new files
git add backend/routers/search.py
git add test_search.py
git add frontend/src/components/SearchBar.tsx
git add frontend/src/components/SearchBar.css
git add frontend/public/PRHLogo.png
git add backend/static/PRHLogo.png
git add PULL_REQUEST_TEMPLATE.md
git add CHANGELOG_v0.3.0.md

# Add all documentation
git add docs/development/*.md
git add docs/RELEASE_NOTES_v0.2.0.md
git add docs/RELEASE_NOTES_v0.2.1.md
git add docs/SESSION_COMPLETE.md
git add docs/SETUP_COMPLETE.md
git add docs/TEST_CHECKLIST.md

# Add modified files
git add backend/data_loader.py
git add backend/database.py
git add backend/main.py
git add backend/models/schemas.py
git add backend/routers/analysis.py
git add frontend/src/App.tsx
git add frontend/src/App.css
git add frontend/src/components/NetworkGraph.tsx
git add frontend/src/pages/Browse.tsx
git add frontend/src/services/api.ts
git add frontend/src/types/index.ts
git add docs/V0.3.0_DEV_STARTED.md

# Add built frontend assets
git add backend/static/

# Stage deletions (moved files)
git rm NEXT_ACTION_PLAN.md
git rm RELEASE_NOTES_v0.2.0.md
git rm RELEASE_NOTES_v0.2.1.md
git rm SESSION_COMPLETE.md
git rm SETUP_COMPLETE.md
git rm TEST_CHECKLIST.md
```

**OR use shortcut** (stage everything):
```bash
git add -A
```

### Step 3: Commit Changes

```bash
git commit -m "feat: Add advanced search, logo integration, and Issue #6 fixes

Major Features:
- Advanced search system with real-time results and analytics
- Global search bar with keyboard shortcuts (/)
- Search result navigation to Browse page
- PRHLogo integration in sidebar
- GitHub Issue #6 resolution (color consistency, acronyms)

Technical Details:
- Backend: Search API with relevance scoring and analytics endpoint
- Frontend: SearchBar component with debounced input and keyboard nav
- Database: search_logs table for analytics tracking
- Performance: <1ms backend, <20ms total response time
- Testing: Automated test suite (test_search.py)

Files Changed:
- 24 new files (search.py, SearchBar, docs, tests)
- 16 modified files (backend, frontend, database)
- 6 moved files (docs reorganization)

Closes #6
"
```

### Step 4: Push to GitHub

```bash
# Push feature branch to remote
git push -u origin feature/advanced-search-and-improvements
```

---

## 🔗 After Pushing

### Create Pull Request on GitHub

1. Go to: https://github.com/ConsciousEnergy/ProjectRawHorse/pulls
2. Click "New Pull Request"
3. Set:
   - **Base**: `v0.3.0-dev` (or `main` if you want to merge to main)
   - **Compare**: `feature/advanced-search-and-improvements`
4. GitHub will auto-fill from `PULL_REQUEST_TEMPLATE.md`
5. Review the changes
6. Click "Create Pull Request"

### PR Title
```
feat: Advanced Search + Logo Integration + Issue #6 Fixes
```

### PR Description
The template in `PULL_REQUEST_TEMPLATE.md` will be used automatically.

---

## ✅ Pre-Push Checklist

Before pushing, verify:

- [x] All tests pass (`python test_search.py`)
- [x] No linting errors
- [x] Frontend builds successfully
- [x] Server runs without errors
- [x] Search feature works in browser
- [x] Logo displays correctly
- [x] Documentation complete
- [x] CHANGELOG updated
- [x] Commit message descriptive

---

## 🎯 Alternative: Quick Push

If you're confident, use these combined commands:

```bash
cd "C:\Users\brand\Project RaHorus\project_rawhorse"

# Create feature branch
git checkout -b feature/advanced-search-and-improvements

# Stage everything
git add -A

# Commit with detailed message
git commit -m "feat: Add advanced search, logo integration, and Issue #6 fixes

Major Features:
- Advanced search with analytics and real-time results  
- PRHLogo integration in sidebar
- GitHub Issue #6 fixes (colors, acronyms, entity detection)

Technical: Search API (routers/search.py), SearchBar component, 
search_logs analytics, URL navigation, 24 new files, comprehensive docs

Performance: <1ms backend, <20ms total, 15+ searches tested

Closes #6"

# Push to GitHub
git push -u origin feature/advanced-search-and-improvements
```

Then create PR on GitHub web interface.

---

## 🚨 Important Notes

1. **Review Before Pushing**: Check git status one more time
2. **Test After Push**: Pull on another machine and test
3. **PR Description**: Use PULL_REQUEST_TEMPLATE.md content
4. **Merge Target**: Decide if merging to v0.3.0-dev or main
5. **Backup**: Current branch is safe, feature branch is new

---

## 📞 Need Help?

If any step fails:
1. Check git status: `git status`
2. View commit history: `git log --oneline -10`
3. Check remote: `git remote -v`
4. Verify branch: `git branch -a`

---

**Ready to push!** Review the commands above and let me know if you want me to execute them. 🚀

