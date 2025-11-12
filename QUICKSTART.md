# UAP Data Explorer - Quick Start Guide

## For End Users

### Option 1: Download Pre-built Executable (Recommended)

1. Go to the [Releases page](https://github.com/YOUR_ORG/uap-data-explorer/releases)
2. Download the latest release for your platform:
   - **Windows**: `UAP-Data-Explorer-Windows.zip`
   - **macOS**: `UAP-Data-Explorer-macOS.zip`
   - **Linux**: `UAP-Data-Explorer-Linux.tar.gz`
3. Extract the archive
4. Run the executable:
   - Windows: Double-click `UAP-Data-Explorer.exe`
   - macOS: Double-click `UAP-Data-Explorer.app`
   - Linux: `./UAP-Data-Explorer`
5. Accept the legal disclaimer
6. Start exploring!

## For Developers

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/consciousenergy/ProjectRawHorse.git
cd project_rawhorse
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
# In a new terminal
cd frontend
npm install
```

4. **Run development servers**

Terminal 1 (Backend):
```bash
cd backend
python main.py
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

5. **Access the application**
- Frontend dev server: http://localhost:3000
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

### Building an Executable

```bash
# Install build dependencies
pip install -r build_requirements.txt

# Run build script
python build_executable.py
```

The executable will be created in `dist/project_rawhorse/`

## Project Structure

```
project_rawhorse/
├── backend/                # FastAPI backend
│   ├── routers/            # API endpoints
│   ├── services/           # GitHub integration
│   ├── models/             # Data models
│   ├── database.py         # Database setup
│   └── main.py             # App entry point
├── frontend/               # React frontend
│   ├── src/
│   │   ├── pages/          # Main pages
│   │   ├── components/     # UI components
│   │   └── services/       # API client
├── .github/workflows/      # CI/CD
├── config.yaml             # Configuration
├── startup.py              # Executable entry
└── build_executable.py     # Build script
```

## Configuration

Edit `config.yaml` to customize:
- Server host and port
- Database location
- Data source directory
- GitHub repository URL

## Data Management

The application loads data from CSV files in:
```
../data/
```

On first run, data is loaded into a SQLite database at:
```
data/project_rawhorse.db
```

## Contributing Data

1. Navigate to the "Contribute" page
2. Generate a GitHub token: https://github.com/settings/tokens
   - Required scope: `repo`
3. Validate your token
4. Fill out the contribution form
5. Submit - an automated PR will be created!

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.10+)
- Verify all dependencies installed: `pip install -r backend/requirements.txt`
- Check port 8000 is not in use

### Frontend won't build
- Check Node version: `node --version` (need 18+)
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Clear build cache: `rm -rf dist`

### Database errors
- Delete `data/project_rawhorse.db` to force rebuild
- Ensure CSV files exist in data source directory
- Check file permissions

### GitHub contributions not working
- Verify token has `repo` scope
- Check repository URL in `config.yaml`
- Ensure you have write access (will fork automatically)

## Getting Help

- **Issues**: https://github.com/consciousenergy/projectrawhorse/issues
- **Discussions**: https://github.com/consciousenergy/projectrawhorse/discussions
- **Documentation**: See README.md and CONTRIBUTING.md

## License

GNU AGPL v3 - See LICENSE file

## Security

- All processing is local
- No telemetry or tracking
- GitHub token stored encrypted
- Open source for transparency

---

**Ready to explore UAP data? Get started now!**
