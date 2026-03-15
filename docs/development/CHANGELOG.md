# Changelog (Legacy Archive)

> Status: Archived legacy changelog for early versions.
>
> Canonical release changelogs now live at project root (for example: `CHANGELOG_v0.4.2Beta.md`, `CHANGELOG_v0.4.1Beta.md`, `CHANGELOG_v0.4.0.md`).

**Project:** Project RawHorse  
**Format:** Keep a Changelog v1.0.0  
**Versioning:** Semantic Versioning 2.0.0

---

## [Unreleased]

### To Implement
- Award contribution backend endpoint
- FOIA Target contribution backend endpoint
- D3.js network visualizations
- Advanced filtering and search
- Unit test suite
- Cross-platform executable builds

---

## [0.1.0-alpha] - 2025-11-11

### Added
- ✨ Compact display formatting (currency abbreviations, year-only dates)
- ✨ Award contribution form (frontend)
- ✨ FOIA Target contribution form (frontend)
- ✨ Custom icon support system (create_icon.py, VBS launcher, desktop entry)
- ✨ SPA routing support for React Router
- ✨ Dependency injection system (backend/dependencies.py)
- 📖 Comprehensive bug fix documentation (5 detailed guides)
- 📖 Feature documentation
- 📖 Organized docs folder structure

### Fixed
- 🐛 TypeScript unused import error in LegalDisclaimer
- 🐛 Config path resolution (PROJECT_ROOT implementation)
- 🐛 Database dependency injection across routers
- 🐛 Circular import between main.py and routers
- 🐛 404 errors on client-side routes

### Changed
- 🔄 Standardized database name to `prh.db`
- 🔄 Updated data_loader.py to use project_root parameter
- 🔄 Refactored router imports to use dependencies module
- 🔄 Reorganized docs into categorical folders
- 🔄 Dashboard displays compact metrics

---

## [0.0.1-dev] - 2025-11-06 to 2025-11-10

### Added
- 🎉 Initial project setup
- 📦 Backend with FastAPI and SQLite
- ⚛️ Frontend with React and TypeScript
- 🗄️ Database schema (5 tables: Entity, Award, MoneyFlow, Relationship, FOIATarget)
- 📊 Data refactoring (74 → 48 organized files)
- 🎨 Light/dark mode theming (purple & gold)
- 📝 PRD with complete roadmap
- ⚙️ 1-click installation scripts
- 🚀 Quick launch scripts
- 📖 Comprehensive documentation
- 🔐 Legal disclaimer system
- 🌐 Complete REST API (17 endpoints)
- 📤 Export functionality (CSV, JSON, PDF)
- 🤝 GitHub contribution workflow (Entity, Money Flow)
- 🎨 Custom branding (PRHLogo)
- 📱 Responsive UI design

### Data Organization
- Created organized directory structure
  - data/entities/
  - data/financial/
  - data/foia/
  - data/reference/
  - data/evidence/
  - data/visualizations/
  - data/scripts/
  - data/docs/
- Unified naming convention
- Archive system for old files
- Git LFS configuration

---

## Version History

| Version | Date | Status | Description |
|---------|------|--------|-------------|
| 0.1.0-alpha | 2025-11-11 | Current | Bug fixes, expanded features, docs organization |
| 0.0.1-dev | 2025-11-06 | Released | Initial development version |

---

## Categories

- **Added:** New features
- **Changed:** Changes in existing functionality
- **Deprecated:** Soon-to-be removed features
- **Removed:** Removed features
- **Fixed:** Bug fixes
- **Security:** Vulnerability fixes

---

## Commit Types

We follow Conventional Commits:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `style:` - Formatting, missing semicolons, etc
- `refactor:` - Code change that neither fixes bug nor adds feature
- `test:` - Adding tests
- `chore:` - Maintenance tasks

---

## Notable Changes by Category

### UI/UX
- Dashboard compact formatting (0.1.0-alpha)
- Light/dark mode theming (0.0.1-dev)
- Contribution page expansion (0.1.0-alpha)

### Backend
- Database standardization to prh.db (0.1.0-alpha)
- SPA routing support (0.1.0-alpha)
- Dependency injection system (0.1.0-alpha)
- FastAPI REST API (0.0.1-dev)

### Infrastructure
- 1-click installation (0.0.1-dev)
- Custom icon support (0.1.0-alpha)
- Git LFS setup (0.0.1-dev)

### Documentation
- Organized docs folder (0.1.0-alpha)
- 5 bug fix guides (0.1.0-alpha)
- Comprehensive PRD (0.0.1-dev)

---

## Upgrade Guide

### From 0.0.1-dev to 0.1.0-alpha

1. **Pull latest changes:**
   ```bash
   git pull origin main
   ```

2. **Rebuild frontend:**
   ```bash
   cd frontend
   npm install
   npm run build
   xcopy /E /I /Y dist ..\backend\static
   ```

3. **Delete old database:**
   ```bash
   rm data/uap_explorer.db  # Old name
   # prh.db will be created automatically
   ```

4. **Restart application:**
   ```bash
   cd backend
   python main.py
   ```

---

## Breaking Changes

### 0.1.0-alpha
- Database name changed from `uap_explorer.db` to `prh.db`
  - Action: Delete old database file, new one will be created
- Docs folder reorganized
  - Action: Update any links to docs files

### 0.0.1-dev
- Initial version, no breaking changes

---

## Known Issues

### Current (0.1.0-alpha)
- Award contribution backend not implemented
- FOIA Target contribution backend not implemented
- Network visualizations pending
- No unit tests yet

### Resolved
- ✅ TypeScript build errors
- ✅ Path resolution issues
- ✅ Database dependency injection
- ✅ Circular imports
- ✅ SPA routing 404s

---

## Roadmap

See [PRD.md](../PRD.md) for detailed roadmap.

**Next Release (0.2.0-alpha):**
- Implement Award/FOIA contribution backends
- Add basic network visualization
- Enhanced search and filtering
- Statistical charts

**Future (0.3.0-alpha):**
- Comprehensive test suite
- Performance optimizations
- Advanced analysis features

**Release (1.0.0):**
- Complete feature set
- Full test coverage
- Production-ready executables
- Public launch

---

## Contributors

- Initial development and bug fixes
- Documentation and organization
- Feature implementation

---

## Links

- **Repository:** https://github.com/ConsciousEnergy/ProjectRawHorse
- **Issues:** https://github.com/ConsciousEnergy/ProjectRawHorse/issues
- **License:** GNU AGPL v3

---

**Last Updated:** 2025-11-11  
**Current Version:** 0.1.0-alpha

