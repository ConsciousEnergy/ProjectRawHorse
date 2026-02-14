# Project RawHorse - Quick Start Guide

## One-Click Installation (Recommended)

### Windows Users

**Option 1: Double-click START.bat** (Easiest)
1. Download and extract Project RawHorse
2. Double-click `START.bat`
3. If not installed, it will guide you through installation
4. Browser opens automatically at http://127.0.0.1:8000

**Option 2: Double-click LaunchRawHorse.vbs** (Supports custom icon)
1. Double-click `LaunchRawHorse.vbs`
2. Same as START.bat but allows creating shortcuts with custom icons
3. To create desktop shortcut: Right-click → Create Shortcut → move to Desktop

**Option 3: Full Installation**
1. Double-click `install.bat`
2. Wait 5-10 minutes for installation
3. Browser opens automatically when complete

**Uninstall:** Double-click `UNINSTALL.bat` to remove the app and free disk space (optional: keep database). Use `UNINSTALL.bat /force` to skip prompts.

### macOS/Linux Users

**Option 1: Run START.sh** (Easiest)
```bash
chmod +x START.sh
./START.sh
```

**Option 2: Full Installation**
```bash
chmod +x install.sh
./install.sh
```

**Uninstall:** Run `./UNINSTALL.sh` to remove the app and free disk space (optional: keep database). Use `./UNINSTALL.sh --force` to skip prompts. See [INSTALL_GUIDE.md](INSTALL_GUIDE.md) for details.

---

## Prerequisites

Before installation, you need:

### Windows
- **Python 3.10+**: Download from https://www.python.org/downloads/
  - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation!
- **Node.js 20+** (LTS): Download from https://nodejs.org/

### macOS
```bash
# Using Homebrew
brew install python3 node
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs
```

---

## For Developers

### Manual Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/ConsciousEnergy/ProjectRawHorse.git
cd ProjectRawHorse
```

2. **Set up backend**
```bash
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

3. **Set up frontend**
```bash
cd frontend
npm install
npm run build
```

4. **Copy frontend to backend**
```bash
# Windows:
xcopy /E /I /Y frontend\dist backend\static

# macOS/Linux:
cp -r frontend/dist backend/static
```

5. **Run the application**
```bash
cd backend
python main.py
```

### Development Mode (Hot Reload)

Run backend and frontend separately for development:

**Terminal 1 (Backend):**
```bash
cd backend
python main.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

Access:
- Frontend dev server: http://localhost:5173
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

---

## Project Structure

```
ProjectRawHorse/
├── backend/                # FastAPI backend
│   ├── routers/            # API endpoints
│   ├── services/           # GitHub integration
│   ├── models/             # Data models
│   ├── static/             # Built frontend (served by backend)
│   ├── database.py         # Database setup
│   ├── auth.py             # JWT authentication
│   └── main.py             # App entry point
├── frontend/               # React frontend
│   ├── src/
│   │   ├── pages/          # Main pages
│   │   ├── components/     # UI components
│   │   └── services/       # API client
├── data/                   # Data files
│   ├── entities/           # Entity CSV files
│   ├── financial/          # Money flow data
│   ├── foia/               # FOIA targets
│   └── scripts/            # Data enrichment scripts
├── docker/                 # Docker deployment files
├── START.bat               # Windows one-click launcher
├── START.sh                # macOS/Linux one-click launcher
├── install.bat             # Windows installer
├── install.sh              # macOS/Linux installer
├── RUN.bat                 # Windows quick launch
├── RUN.sh                  # macOS/Linux quick launch
├── LaunchRawHorse.vbs      # Windows launcher with icon support
├── config.yaml             # Configuration
└── docker-compose.yml      # Docker deployment
```

---

## Using the Application

### Dashboard
Overview statistics and quick access to features.

### Browse
Search and filter:
- **Entities**: Organizations, agencies, contractors
- **Money Flows**: Financial transactions and relationships
- **Awards**: Federal contracts and grants
- **FOIA Targets**: Suggested FOIA requests with quality scores

### Analysis
Interactive visualizations:
- **Network Graph**: Force-directed entity relationship graph
- **Sankey Diagram**: Financial flow visualization
- **Intelligence Stack Filter**: Filter by hierarchy level

### Export
Download data in CSV, JSON, or PDF formats.

### Contribute
Submit new data via automated GitHub pull requests.

---

## Troubleshooting

### Installation Issues

**"Python is not installed"**
- Install Python from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH"
- Restart your terminal/command prompt after installation

**"Node.js is not installed"**
- Install Node.js from https://nodejs.org/
- Choose the LTS version

**"Failed to create virtual environment"**
```bash
python -m pip install --upgrade pip virtualenv
```

### Runtime Issues

**Backend won't start**
- Check Python version: `python --version` (need 3.10+)
- Check port 8000 is not in use
- Try: `pip install -r backend/requirements.txt`

**Frontend build fails**
- Check Node version: `node --version` (need 20+)
- Delete node_modules and reinstall:
  ```bash
  cd frontend
  rm -rf node_modules
  npm install
  ```

**Database errors**
- Delete `data/prh.db` to force rebuild
- Application will recreate database on next start

**Browser doesn't open automatically**
- Manually navigate to http://127.0.0.1:8000

---

## Configuration

Edit `config.yaml` to customize:
- Server host and port
- Database location
- Data source directories
- GitHub repository URL

---

## Getting Help

- **Issues**: https://github.com/ConsciousEnergy/ProjectRawHorse/issues
- **Discussions**: https://github.com/ConsciousEnergy/ProjectRawHorse/discussions
- **Documentation**: See README.md

---

## License

GNU AGPL v3 - See LICENSE file

---

## Security & Privacy

- All processing is local - no external servers
- No telemetry or tracking
- GitHub tokens stored encrypted
- Open source for full transparency

---

**Ready to explore? Double-click START.bat (Windows) or run ./START.sh (macOS/Linux)!**
