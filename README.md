# Project RawHorse

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React 18+](https://img.shields.io/badge/react-18+-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![GitHub Release](https://img.shields.io/github/v/release/ConsciousEnergy/ProjectRawHorse?include_prereleases)](https://github.com/ConsciousEnergy/ProjectRawHorse/releases)
[![GitHub Stars](https://img.shields.io/github/stars/ConsciousEnergy/ProjectRawHorse)](https://github.com/ConsciousEnergy/ProjectRawHorse/stargazers)

A cross-platform, single-click desktop application for exploring and analyzing publicly available data related to Unidentified Anomalous Phenomena (UAP) research, federal contracting, and related entities.

## ⚡ Quick Start (Non-Technical Users)

### Windows
1. Download Project RawHorse
2. **Double-click** `install.bat` 
3. Wait for installation (5-10 minutes)
4. Browser opens automatically!

### macOS/Linux
1. Download Project RawHorse
2. Open Terminal in the folder
3. Run: `./install.sh`
4. Browser opens automatically!

**See [INSTALL_GUIDE.md](INSTALL_GUIDE.md) for detailed instructions**

---

## Features

- **Local-First Architecture**: All data processing happens on your machine
- **Comprehensive Data Browsing**: Explore entities, money flows, federal awards, and FOIA targets
- **Interactive Analysis**: Visualize entity relationships and financial networks
- **Multiple Export Formats**: Download data in CSV, JSON, or PDF
- **Community Contributions**: Submit new data via automated GitHub pull requests
- **Cross-Platform**: Runs on Windows, macOS, and Linux
- **1-Click Installation**: Simple setup for non-technical users

## Technology Stack

- **Backend**: FastAPI (Python) with SQLite database
- **Frontend**: React with TypeScript
- **Data Visualization**: D3.js, Recharts
- **GitHub Integration**: PyGithub for automated PR creation
- **Packaging**: PyInstaller for cross-platform executables

## Data Sources

All data is sourced from official public databases:

- **USAspending.gov**: Federal spending and contract data
- **SAM.gov**: Entity registrations and awards
- **Federal FOIA Reading Rooms**: Various agencies
- **DOE, NASA, DHS, NOAA, NIST, NSF**: Public databases
- **Agency Procurement Forecasts**: Solicitation data

## Documentation

- **[PRD.md](PRD.md)** - Comprehensive Product Requirements Document with architecture, roadmap, and specifications
- **[DISCLAIMER.md](DISCLAIMER.md)** - Legal disclaimer for data use
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Guidelines for contributing
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide
- **[INSTALL_GUIDE.md](INSTALL_GUIDE.md)** - Detailed installation instructions for non-technical users
- **[data/README.md](data/README.md)** - Comprehensive data organization guide

## For Developers

### Development Setup

**Prerequisites:**
- Python 3.10+
- Node.js 18+
- Git
- **Git LFS** (required for large data files)

**Important:** This repository uses Git LFS to manage large data files (CSV, PNG, XLSX). You must have Git LFS installed before cloning:

```bash
# Install Git LFS (if not already installed)
# Windows (with Git for Windows):
git lfs install

# macOS (with Homebrew):
brew install git-lfs
git lfs install

# Linux (Debian/Ubuntu):
sudo apt-get install git-lfs
git lfs install
```

**Quick Start:**

```bash
# Clone repository
git clone https://github.com/consciousenergy/projectrawhorse.git
cd project-rawhorse

# Windows: Run installer
install.bat

# macOS/Linux: Run installer
chmod +x install.sh
./install.sh
```

**Manual Setup:**

```bash
# Backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
cd backend
pip install -r requirements.txt

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

- Frontend dev: http://localhost:3000
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

### Building an Executable

```bash
python build_executable.py
```

Output: `dist/RawHorse/RawHorse.exe` (or equivalent for your OS)

## Project Structure

```
project-rawhorse/
├── backend/              # FastAPI backend
│   ├── routers/          # API endpoints
│   ├── services/         # GitHub integration
│   ├── models/           # Data models
│   └── main.py           # Application entry
├── frontend/             # React frontend
│   ├── src/
│   │   ├── pages/        # Main pages
│   │   ├── components/   # UI components
│   │   └── services/     # API client
├── install.bat           # Windows 1-click installer
├── install.sh            # Mac/Linux 1-click installer
├── RUN.bat               # Windows quick launch
├── RUN.sh                # Mac/Linux quick launch
└── INSTALL_GUIDE.md      # Detailed user guide
```

## Usage

### Dashboard
View overview statistics and quick access to features.

### Browse
Search and filter:
- **Entities**: Organizations, agencies, contractors
- **Money Flows**: Financial transactions and relationships
- **Awards**: Federal contracts and grants
- **FOIA Targets**: Suggested FOIA requests

### Analysis
Visualize data through:
- Network graphs of entity relationships
- Financial flow analysis (top recipients/sources)
- Transaction timelines

### Export
Download data in multiple formats:
- **CSV**: For Excel and spreadsheets
- **JSON**: For programmatic access
- **PDF**: Formatted reports

### Contribute
Submit new data to the community:
1. Provide GitHub personal access token
2. Fill out contribution form
3. Automated PR created for review

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Ways to Contribute:**
- **Data**: Submit new entities, money flows, or awards
- **Code**: Fix bugs, add features, improve documentation
- **Issues**: Report problems or suggest enhancements
- **Documentation**: Improve guides and tutorials

## License

**GNU Affero General Public License v3.0 (AGPL-3.0)**

The AGPL ensures:
- Software remains free and open source
- Modifications must be made available
- Network services must provide source code

See [LICENSE](LICENSE) for full details.

## Legal Disclaimer

**IMPORTANT**: This application uses only publicly available data from official government sources. 

**Users are responsible for:**
- Verifying data accuracy
- Compliance with export controls (ITAR, EAR)
- Following proper FOIA procedures
- Respecting classification guidelines

See [DISCLAIMER.md](DISCLAIMER.md) for complete terms.

## Security & Privacy

- **No Telemetry**: No analytics or user tracking
- **Local Processing**: All data stays on your machine
- **No External Servers**: Application runs entirely locally
- **Encrypted Storage**: GitHub tokens stored encrypted
- **Open Source**: Full transparency

## System Requirements

- **OS**: Windows 10+, macOS 10.15+, or modern Linux
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 500MB for application + data
- **Internet**: Only needed for installation and GitHub contributions

## Troubleshooting

### Installation Issues

**Windows:**
- Install Python from https://www.python.org/ (check "Add to PATH")
- Install Node.js from https://nodejs.org/
- Run `install.bat` as Administrator if needed

**macOS/Linux:**
- Install Python: `brew install python3` or use package manager
- Install Node.js: `brew install node` or use package manager
- Make scripts executable: `chmod +x install.sh RUN.sh`

### Runtime Issues

**Backend won't start:**
- Check port 8000 is not in use
- Verify Python 3.10+ installed
- Check all dependencies installed

**Frontend build fails:**
- Delete `node_modules` and run `npm install` again
- Ensure Node.js 18+ installed

**Database errors:**
- Delete `data/prh.db` to force rebuild
- Check CSV files exist in data source directory

## FAQ

**Q: Is this affiliated with any government agency?**  
A: No, this is an independent open-source project using public data.

**Q: Can I use this data for research?**  
A: Yes, but verify accuracy independently and cite your sources.

**Q: How often is data updated?**  
A: Download new releases as they become available. Data reflects the version date.

**Q: Can I modify the application?**  
A: Yes! It's open source under AGPL v3. Modifications must also be open source.

**Q: Do I need internet after installation?**  
A: No, except for GitHub contributions. All other features work offline.

## Roadmap

- [ ] Enhanced D3.js force-directed network graphs
- [ ] Advanced filtering and query builder UI
- [ ] Batch data import from multiple sources
- [ ] Automated data updates from public APIs
- [ ] Additional export formats (Excel, GraphML)
- [ ] Plugin system for custom analysis

## Support

- **Issues**: [GitHub Issues](https://github.com/consciousenergy/project-rawhorse/issues)
- **Discussions**: [GitHub Discussions](https://github.com/consciousenergy/project-rawhorse/discussions)
- **Documentation**: See docs/ directory

## 💝 Support This Project

Project RawHorse is a labor of love for transparency and open research. If you find this project valuable, please consider supporting its development:

### Ways to Support

**🌟 Star this Repository**  
Give us a star on GitHub! It helps others discover the project.

**🔗 Share with Others**  
Spread the word about open UAP research and data transparency.

**💰 Financial Support**

Help us continue development and expand our research:

- **Donate via Website**: [conscious.energy/donations](https://conscious.energy/donations/)
- **Support ICCF25 Campaign**: [GoFundMe - ICCF25](https://www.gofundme.com/f/iccf25-conscious-energy)
- **Bitcoin**: Available on our [donations page](https://conscious.energy/donations/)
- **GitHub Sponsors**: Coming soon!

Your support helps us:
- Maintain and improve the application
- Add new features and visualizations
- Expand data coverage
- Host community resources
- Continue independent research (Project Proteus and more)

Every contribution, no matter the size, makes a difference! 🙏

## Acknowledgments

Built on publicly available data from:
- U.S. federal government open data initiatives
- Transparency and accountability efforts
- Open source community contributions

## Version History

### v1.0.0 (2025-11-11)
- Initial release
- Core browsing, analysis, and export features
- GitHub PR automation for contributions
- Cross-platform desktop application
- 1-click installation for non-technical users

---

**Built with transparency and accountability in mind.**

Licensed under GNU AGPL v3 | See DISCLAIMER.md for legal information

**Ready to explore? Download and run install.bat (Windows) or install.sh (Mac/Linux)!**
