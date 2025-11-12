# Git Ignore Configuration

**Date:** 2025-11-11  
**Status:** Configured and Ready  
**Category:** Setup

Complete reference for what will be excluded from Git.

---

## 🎯 Archive Folders Excluded

The following patterns ensure **ALL** `_archive` folders are excluded from Git:

```gitignore
# Exclude all archive folders from Git
**/_archive/
*/_archive/
_archive/
```

### What This Excludes

**Currently in project:**
- ✅ `data/_archive/` (26 original data files)
- ✅ `docs/_archive/` (16 original documentation files)

**Future-proof:**
- ✅ Any `_archive/` folder at project root
- ✅ Any `_archive/` folder in any subdirectory
- ✅ All files and subfolders within archive folders

---

## 📦 What Gets Excluded

### Development Files
```gitignore
# Python
__pycache__/
*.pyc
venv/
*.egg-info/

# Node
node_modules/
frontend/dist/
frontend/build/

# IDE
.vscode/
.idea/
```

### Environment & Secrets
```gitignore
.env
.env.local
```

### Database Files
```gitignore
*.db
*.sqlite
*.sqlite3
```

### Build Artifacts
```gitignore
build/
dist/
*.spec
```

### Archives (NEW)
```gitignore
**/_archive/
*/_archive/
_archive/
```

---

## ✅ What Gets Included

### Source Code
- ✅ `backend/` - All Python source
- ✅ `frontend/src/` - All React/TypeScript source
- ✅ `frontend/public/` - Static assets

### Configuration
- ✅ `config.yaml`
- ✅ `package.json`
- ✅ `requirements.txt`
- ✅ `tsconfig.json`

### Data Files (via Git LFS)
- ✅ `data/entities/*.csv`
- ✅ `data/financial/*.csv`
- ✅ `data/foia/*.csv`
- ✅ All organized data files
- ❌ `data/_archive/` (EXCLUDED)

### Documentation
- ✅ `README.md`
- ✅ `LICENSE`
- ✅ `docs/README.md`
- ✅ `docs/PRD.md`
- ✅ All organized docs
- ❌ `docs/_archive/` (EXCLUDED)

### Scripts
- ✅ `install.bat` / `install.sh`
- ✅ `RUN.bat` / `RUN.sh`
- ✅ `build_executable.py`
- ✅ `create_icon.py`

### Launchers
- ✅ `LaunchRawHorse.vbs`
- ✅ `ProjectRawHorse.desktop`
- ✅ `PRHLogo.png` / `PRHLogo.ico`

---

## 🔍 Archive Contents (Excluded)

### data/_archive/
**26 files** - Original unrefactored data files from 2025-11-06
- Original entities, money flows, awards with date stamps
- Duplicates and redundant versions
- Pre-consolidation files

**Why excluded:** 
- Redundant (consolidated into organized files)
- Historical reference only
- Would bloat repository

### docs/_archive/
**16 files** - Original documentation before reorganization
- SESSION_PROGRESS.md
- SESSION_SUMMARY.md
- READY_FOR_GITHUB.md
- IMPLEMENTATION_COMPLETE.md
- NEXT_STEPS.md
- Multiple BUGFIX_*.md files
- FEATURE_*.md files
- Installation/runtime fix docs

**Why excluded:**
- Consolidated into organized docs
- Historical reference only
- Redundant information

---

## 📊 Repository Size Impact

### Without Archive Exclusion
- **Data:** ~15 MB (original + refactored)
- **Docs:** ~150 KB (original + organized)
- **Total archives:** ~15 MB

### With Archive Exclusion (Current)
- **Data:** ~8 MB (organized only)
- **Docs:** ~60 KB (organized only)
- **Savings:** ~7 MB + cleaner structure

---

## 🧪 Testing Gitignore

Once you initialize Git, test with:

```bash
# Check if a path is ignored
git check-ignore -v data/_archive/

# Check if a specific file is ignored
git check-ignore -v docs/_archive/SESSION_PROGRESS.md

# List all files that would be tracked
git status --ignored
```

**Expected output:**
- `data/_archive/` → Ignored
- `docs/_archive/` → Ignored
- All files within archives → Ignored

---

## 🔧 Gitignore Patterns Explained

### `**/_archive/`
- Matches `_archive/` at **any depth**
- Most powerful pattern
- Catches: `data/_archive/`, `docs/_archive/`, `foo/bar/_archive/`

### `*/_archive/`
- Matches `_archive/` in **any immediate subdirectory**
- One level deep
- Catches: `data/_archive/`, `docs/_archive/`

### `_archive/`
- Matches `_archive/` at **root only**
- Backup pattern
- Catches: `_archive/` (if at project root)

**Why three patterns?**
- Maximum compatibility across Git versions
- Ensures nothing slips through
- Future-proof for any new archives

---

## 📝 Best Practices

### Archive Management
1. **Keep archives locally** - For your reference
2. **Don't push to Git** - Bloats repository
3. **Document what's archived** - In README files
4. **Periodic cleanup** - Delete very old archives

### When to Archive
- ✅ Refactored/consolidated files
- ✅ Outdated documentation
- ✅ Superseded versions
- ✅ Historical reference material

### When NOT to Archive
- ❌ Active development files
- ❌ Current documentation
- ❌ Production data
- ❌ Configuration files

---

## 🚀 Before First Push

Verify your `.gitignore` is working:

```bash
# Initialize Git (if not done)
git init

# Check what will be staged
git status

# Verify archives are NOT listed
# Should see:
#   - backend/
#   - frontend/
#   - data/ (without _archive/)
#   - docs/ (without _archive/)
```

---

## 🛡️ Git LFS and Archives

**Note:** Archive folders are excluded via `.gitignore`, so they never reach Git LFS either.

**Data files included (via LFS):**
- `data/entities/*.csv`
- `data/financial/*.csv`
- `data/foia/*.csv`
- `data/visualizations/*.png`

**Data files excluded:**
- ❌ `data/_archive/*.csv` (gitignored)
- ❌ `prh.db` (gitignored via `*.db`)

---

## 📋 Verification Checklist

Before pushing to GitHub:

- [x] `.gitignore` includes archive patterns
- [x] Both `data/_archive/` and `docs/_archive/` exist locally
- [x] Archives contain 26 + 16 = 42 files
- [ ] Git initialized (run `git init`)
- [ ] Git LFS configured (run `git lfs install`)
- [ ] Verify archives not staged (run `git status`)
- [ ] Ready to push clean repository

---

## 🎯 Summary

✅ **Archive folders properly configured for exclusion**
- Pattern: `**/_archive/`
- Covers: All archive folders at any depth
- Impact: Cleaner, smaller repository
- Local: Archives preserved for reference

✅ **Repository will be clean and professional**
- Only organized, current files
- No redundant historical files
- Optimal size for Git LFS
- Easy for contributors

---

## 📞 Questions?

**"Will I lose the archived files?"**
No! They remain on your local machine, just not pushed to GitHub.

**"Can I access them later?"**
Yes! They're in `data/_archive/` and `docs/_archive/` locally.

**"What if I need to restore something?"**
Copy from your local `_archive/` folder to the appropriate location.

**"Can I push archives later if needed?"**
Yes, by removing the pattern from `.gitignore` and committing.

---

**Status:** ✅ READY - All archives will be excluded from Git push

**Next:** Follow `setup/GIT_SETUP.md` for first push!

