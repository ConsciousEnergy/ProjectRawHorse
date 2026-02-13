# Installation Guide

**Date:** 2025-11-11  
**Status:** Active  
**Category:** Setup

Complete installation guide for Project RawHorse.

---

## 🚀 Quick Start

### Prerequisites

- **Python:** 3.10 or higher
- **Node.js:** 20 or higher (LTS)
- **Git:** Latest version

---

## 📦 Installation Methods

### Method 1: 1-Click Installation (Recommended)

**Windows:**
```batch
install.bat
```

**macOS/Linux:**
```bash
chmod +x install.sh
./install.sh
```

**What it does:**
1. Checks Python and Node.js versions
2. Creates Python virtual environment
3. Installs backend dependencies
4. Installs frontend dependencies
5. Builds frontend
6. Copies frontend to backend/static
7. Launches application

---

### Method 2: Manual Installation

#### Step 1: Backend Setup

```bash
# Navigate to project
cd project_rawhorse

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

#### Step 2: Frontend Setup

```bash
# From project root
cd frontend

# Install dependencies
npm install

# Build frontend
npm run build

# Copy to backend static folder
# Windows:
xcopy /E /I /Y dist ..\backend\static
# macOS/Linux:
cp -r dist/* ../backend/static/
```

#### Step 3: Run Application

```bash
# From project root
cd backend
python main.py
```

Browser will open automatically to http://127.0.0.1:8000

---

## 🔄 Quick Launch (After Installation)

**Windows:**
```batch
RUN.bat
```

**macOS/Linux:**
```bash
./RUN.sh
```

---

## ⚙️ Configuration

### config.yaml

Located in project root:

```yaml
app:
  name: "Project RawHorse"
  version: "1.0.0"

server:
  host: "127.0.0.1"
  port_range: [8000, 8100]
  auto_open_browser: true

database:
  path: "data/prh.db"

data_sources:
  entities_dir: "data/entities"
  financial_dir: "data/financial"
  foia_dir: "data/foia"
  reference_dir: "data/reference"
  evidence_dir: "data/evidence"
  visualizations_dir: "data/visualizations"
  scripts_dir: "data/scripts"
  docs_dir: "data/docs"

github:
  repository_url: "https://github.com/consciousenergy/UAPUFOData"
  branch_prefix: "contribution"
  enabled: true

features:
  github_integration: true
  advanced_analysis: true
  export_pdf: true
```

---

## 🐛 Troubleshooting

### Python Not Found

**Windows:**
```batch
# Install from python.org
# Add to PATH during installation
```

**macOS:**
```bash
brew install python@3.10
```

**Linux:**
```bash
sudo apt-get install python3.10
```

### Node.js Not Found

**Windows:**
Download from https://nodejs.org/

**macOS:**
```bash
brew install node
```

**Linux:**
```bash
sudo apt-get install nodejs npm
```

### Frontend Build Fails

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Backend Won't Start

```bash
# Check database
cd data
# If prh.db is corrupt:
rm prh.db
# Restart backend - it will recreate
```

### Port Already in Use

Edit `config.yaml` and change port_range:
```yaml
server:
  port_range: [8001, 8100]
```

### Database Errors

```bash
# Delete database to force rebuild
rm data/prh.db

# Restart application
cd backend
python main.py
```

---

## 📚 Dependencies

### Backend (Python)
- FastAPI - Web framework
- SQLAlchemy - Database ORM
- Uvicorn - ASGI server
- Pandas - Data processing
- PyYAML - Configuration
- PyGithub - GitHub API
- ReportLab - PDF generation

### Frontend (Node.js)
- React 18+ - UI framework
- TypeScript - Type safety
- Vite - Build tool
- React Router - Routing
- Lucide React - Icons
- Axios - HTTP client

---

## Cloning the Repository

```bash
git clone https://github.com/ConsciousEnergy/ProjectRawHorse.git
cd ProjectRawHorse
```

> **Note:** Git LFS is no longer required as of v0.4.0. All data files are stored directly in the repository.

---

## 🖥️ System Requirements

**Minimum:**
- CPU: Dual-core 2.0 GHz
- RAM: 4 GB
- Storage: 500 MB
- OS: Windows 10, macOS 10.15, Ubuntu 20.04

**Recommended:**
- CPU: Quad-core 2.5+ GHz
- RAM: 8+ GB
- Storage: 1+ GB
- OS: Windows 11, macOS 13+, Ubuntu 22.04+

---

## 📱 Tested Platforms

**Windows:**
- ✅ Windows 11
- ✅ Windows 10

**macOS:**
- ✅ macOS Ventura (13.x)
- ✅ macOS Monterey (12.x)

**Linux:**
- ✅ Ubuntu 22.04 LTS
- ✅ Ubuntu 20.04 LTS
- ✅ Fedora 38

---

## 🔧 Advanced Setup

### Development Mode

```bash
# Backend (hot reload)
cd backend
uvicorn main:app --reload

# Frontend (dev server)
cd frontend
npm run dev
```

### Production Build

```bash
# Build executable
python build_executable.py

# Output in dist/RawHorse/
```

---

## 📖 Next Steps

After installation:

1. **Browse Data:** Click "Browse" to explore entities
2. **View Stats:** Dashboard shows overview
3. **Export Data:** Download in various formats
4. **Contribute:** Submit new data via GitHub PR

---

## 💡 Tips

- Use virtual environment for clean dependencies
- Run `npm run build` after frontend changes
- Restart backend to reload data
- Check logs for errors
- Update dependencies periodically

---

## 🆘 Getting Help

If installation fails:

1. Check error messages carefully
2. Verify prerequisites installed
3. Review [BUGFIXES.md](../development/BUGFIXES.md)
4. Check GitHub issues
5. Open new issue with details

---

**Installation Time:** ~5-10 minutes (depending on internet speed)

**Status:** ✅ Tested and Working on Windows, macOS, and Linux

