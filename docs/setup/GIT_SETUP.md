# Git Setup and GitHub Push Commands

Follow these steps to initialize Git, setup LFS, and push to GitHub.

## Step 1: Install Git LFS (if not already installed)

**Windows (with Git for Windows):**
```bash
git lfs install
```

**macOS (with Homebrew):**
```bash
brew install git-lfs
git lfs install
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get install git-lfs
git lfs install
```

## Step 2: Navigate to Project Directory

```bash
cd "C:\Users\user\Project RaHorus\project_rawhorse"
```

## Step 3: Initialize Git Repository (if needed)

Check if Git is already initialized:
```bash
git status
```

If you see "fatal: not a git repository", initialize it:
```bash
git init
```

## Step 4: Setup Git LFS Tracking

The `.gitattributes` file is already created. Now track the patterns:

```bash
git lfs track "*.csv"
git lfs track "*.xlsx"
git lfs track "*.png"
git lfs track "*.jpg"
git lfs track "*.jpeg"
git lfs track "*.db"
git lfs track "*.sqlite"
```

Verify LFS is tracking:
```bash
git lfs track
```

## Step 5: Add GitHub Remote

```bash
git remote add origin https://github.com/ConsciousEnergy/ProjectRawHorse.git
```

If remote already exists, update it:
```bash
git remote set-url origin https://github.com/ConsciousEnergy/ProjectRawHorse.git
```

Verify remote:
```bash
git remote -v
```

## Step 6: Stage All Files

```bash
# Add .gitattributes first
git add .gitattributes

# Add everything else
git add .
```

Check what will be committed:
```bash
git status
```

## Step 7: Create Initial Commit

```bash
git commit -m "Initial commit: Project RawHorse - UAP research data explorer

- FastAPI backend with SQLite database (prh.db)
- React frontend with TypeScript
- Refactored data structure (48 organized files)
- 1-click installation for non-technical users
- Light/dark mode theming (purple & gold)
- Cross-platform support (Windows, macOS, Linux)
- GNU AGPL v3 license
- Git LFS for large data files
- Comprehensive PRD and documentation
- Standardized database naming"
```

## Step 8: Set Main Branch and Push

```bash
git branch -M main
git push -u origin main
```

## Troubleshooting

### If Git LFS objects are too large:
Git LFS should handle this automatically, but if you encounter issues:

```bash
# Check LFS objects
git lfs ls-files

# Check repository size
git count-objects -vH
```

### If push is rejected:
If the remote repository already has commits:

```bash
git pull origin main --rebase
git push -u origin main
```

### If you need to force push (use with caution):
```bash
git push -u origin main --force
```

**Note:** Only use force push if you're sure you want to overwrite remote history.

## What's Being Committed

**Included:**
- All source code (backend/, frontend/src/)
- Configuration files (config.yaml, package.json, requirements.txt)
- Documentation (README.md, PRD.md, DISCLAIMER.md, etc.)
- Installation scripts (install.bat, install.sh, RUN.bat, RUN.sh)
- Data files (via Git LFS)
  - data/entities/ (5 CSV files)
  - data/financial/ (9 CSV files)
  - data/foia/ (3 CSV files + 15 templates)
  - data/reference/ (7 files)
  - data/evidence/ (1 CSV file)
  - data/visualizations/ (8 PNG files)
  - data/scripts/ (11 Python files)
  - data/docs/ (5 Markdown files)
- License (LICENSE)
- Logo (PRHLogo.png, frontend/public/logo.png)

**Excluded (via .gitignore):**
- data/_archive/ (26 old files)
- data/prh.db (database - generated on first run)
- frontend/node_modules/
- venv/, env/
- __pycache__/
- frontend/dist/, frontend/build/
- *.log files

## Repository Size Estimate

- **Without LFS:** ~10-15 MB (code, docs, small files)
- **With LFS pointers:** ~10-15 MB (LFS creates small pointer files)
- **LFS Storage:** ~50-100 MB (actual data files stored in LFS)

Total GitHub repo size will appear small (~10-15 MB) because LFS data is stored separately.

## After Push - Verify

1. Visit: https://github.com/ConsciousEnergy/ProjectRawHorse
2. Check that files are visible
3. Look for LFS badge on large files (CSV, PNG)
4. Verify README.md renders correctly
5. Check that PRD.md is accessible in docs/

## Next Steps After Push

1. Configure repository settings on GitHub
2. Add repository description
3. Add topics/tags for discoverability
4. Enable Issues and Discussions (if desired)
5. Add collaborators (if needed)
6. Setup branch protection rules (optional)
7. Configure GitHub Actions for CI/CD (optional)

---

**Ready to push? Run the commands above in order!**

