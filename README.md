# Project RawHorse

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React 18+](https://img.shields.io/badge/react-18+-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![GitHub Release](https://img.shields.io/github/v/release/ConsciousEnergy/ProjectRawHorse?include_prereleases)](https://github.com/ConsciousEnergy/ProjectRawHorse/releases)
[![GitHub Stars](https://img.shields.io/github/stars/ConsciousEnergy/ProjectRawHorse)](https://github.com/ConsciousEnergy/ProjectRawHorse/stargazers)

A cross-platform, single-click desktop application for exploring and analyzing publicly available data related to Unidentified Anomalous Phenomena (UAP) research, federal contracting, and related entities.

> **OPINT** (Open Intelligence) is the practice of building transparent, publicly-auditable intelligence databases from open sources. Project RawHorse is an OPINT tool — every data point is sourced from public records, every algorithm is open source, and every conclusion is reproducible.

## What Can I Do With This?

- **Browse** UAP-related entities (agencies, contractors, programs) and their connections
- **Explore** federal award money flows with interactive Sankey diagrams
- **Visualize** the intelligence organizational pyramid (L1 Control Group → L6 Programs)
- **Search** across all data types with instant fuzzy-matched results
- **Export** data for your own research in CSV, JSON, or PDF format
- **Contribute** new data directly from the app — it creates a GitHub PR for review

## ⚡ Quick Start (Non-Technical Users)

### Windows
1. Download Project RawHorse
2. **Double-click** `START.bat` (guides you through everything!)
3. Wait for installation (5-10 minutes on first run)
4. Browser opens automatically at http://127.0.0.1:8000

### macOS/Linux
1. Download Project RawHorse
2. Open Terminal in the folder
3. Run: `chmod +x START.sh && ./START.sh`
4. Browser opens automatically!

**See [INSTALL_GUIDE.md](INSTALL_GUIDE.md) for detailed instructions**

### Uninstall
To remove Project RawHorse and free disk space: **Windows** — double-click `UNINSTALL.bat`; **macOS/Linux** — run `./UNINSTALL.sh` (or `./UNINSTALL.sh --force` to skip prompts). You can choose to keep or delete your database. See [INSTALL_GUIDE.md](INSTALL_GUIDE.md#uninstalling-project-rawhorse).

---
## Screenshots of Applications UI
<img width="1904" height="953" alt="PRHScreenshot_7" src="https://github.com/user-attachments/assets/71df00eb-2c17-42c1-b2f4-16212c8a507a" />

<img width="1906" height="952" alt="PRHScreenshot_1" src="https://github.com/user-attachments/assets/9b8c04a2-3dc2-4ac0-99a4-39385f314dda" />

<img width="1903" height="952" alt="PRHScreenshot_6" src="https://github.com/user-attachments/assets/3b6c65f8-a9ee-4db8-9cee-a8351cc08c17" />

<img width="1905" height="953" alt="PRHScreenshot_5" src="https://github.com/user-attachments/assets/bb8410f5-8be8-4d12-ac95-b5ff2fdf099b" />

<img width="1919" height="951" alt="PRHAnalysisScreenshot_1" src="https://github.com/user-attachments/assets/1f582c78-2bb5-407f-b359-b6a2f29aeca0" />

<img width="1900" height="948" alt="PRHIntelStackPyramidScreenshot_1" src="https://github.com/user-attachments/assets/4745091f-f60e-4921-90ee-fd847e152465" />

<img width="1904" height="946" alt="PRHIntelStackPyramidScreenshot_2" src="https://github.com/user-attachments/assets/6ebd4ca9-d345-499a-b31e-d22666105e97" />

<img width="1906" height="954" alt="PRHScreenshot_3" src="https://github.com/user-attachments/assets/138009a8-301b-4777-a880-321e3de28b8b" />


## Features

- **Local-First Architecture**: All data processing happens on your machine
- **Comprehensive Data Browsing**: Explore entities, money flows, federal awards, and FOIA targets
- **Interactive Analysis**: Visualize entity relationships and financial networks
- **Intelligence Stack Filter**: Filter entities by hierarchy level (Control Group → Programs)
- **Multiple Export Formats**: Download data in CSV, JSON, or PDF
- **Community Contributions**: Submit new data via automated GitHub pull requests
- **Cross-Platform**: Runs on Windows, macOS, and Linux
- **1-Click Installation**: Simple setup for non-technical users
- **Production-Ready**: Docker support for VPS deployment with PostgreSQL

## Technology Stack

- **Backend**: FastAPI (Python) with SQLite/PostgreSQL database support
- **Frontend**: React 18+ with TypeScript and Vite build system
- **Data Visualization**: D3.js, Recharts, react-force-graph-2d
- **NLP Processing**: spaCy for entity recognition and transcript extraction
- **Data Enrichment**: Web scraping (BeautifulSoup), DuckDuckGo search integration
- **Authentication**: JWT token-based auth for secure write operations
- **Caching**: Redis support for production deployments
- **Deployment**: Docker Compose with Caddy reverse proxy, multi-service architecture
- **GitHub Integration**: PyGithub for automated PR creation
- **Packaging**: PyInstaller for cross-platform executables

## Data Sources

All data is sourced from official public databases and open research:

**Government Sources:**
- **USAspending.gov**: Federal spending and contract data
- **SAM.gov**: Entity registrations and awards
- **Federal FOIA Reading Rooms**: Various agencies
- **DOE, NASA, DHS, NOAA, NIST, NSF**: Public databases
- **Agency Procurement Forecasts**: Solicitation data

**Research Attribution:**
- **[UAPGerb](https://www.youtube.com/@uapgerb)**: Entity relationships and organizational structures derived from transcript analysis
  - "The Hidden Wing" - US Air Force UFO Reverse Engineering Programs (2026)
  - Previous transcripts on NRO, CIA DS&T, FFRDCs, Office of Global Access

## Documentation

**For users:**
- **[INSTALL_GUIDE.md](INSTALL_GUIDE.md)** - Detailed installation instructions for non-technical users
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide
- **[FIRST_RUN.md](docs/FIRST_RUN.md)** - What to expect on your first run
- **[DISCLAIMER.md](DISCLAIMER.md)** - Legal disclaimer for data use

**For developers:**
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System overview, data flow, and design decisions
- **[DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)** - Setup, build, test, and contribute
- **[API_REFERENCE.md](docs/API_REFERENCE.md)** - All 45+ REST API endpoints documented
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Code style, PR process, and data guidelines
- **[PRD.md](docs/PRD.md)** - Product Requirements Document
- **[data/README.md](data/README.md)** - Data organization and CSV schema guide

## For Developers

### Development Setup

**Prerequisites:**
- Python 3.10+
- Node.js 20+ (LTS)
- Git

**Quick Start:**

```bash
# Clone repository
git clone https://github.com/ConsciousEnergy/ProjectRawHorse.git
cd ProjectRawHorse

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

- Frontend dev: http://localhost:5173 (Vite dev server, proxies API to 8000)
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

### Building an Executable

```bash
python build_executable.py
```

Output: `dist/RawHorse/RawHorse.exe` (or equivalent for your OS)

## Project Structure

```
ProjectRawHorse/
├── backend/                  # FastAPI backend
│   ├── routers/              # API endpoints
│   ├── services/             # GitHub integration
│   ├── models/               # Data models
│   ├── static/               # Built frontend (served by backend)
│   ├── auth.py               # JWT authentication
│   ├── database.py           # SQLite/PostgreSQL support
│   └── main.py               # Application entry
├── frontend/                 # React frontend
│   └── src/
│       ├── pages/            # Main pages (Dashboard, Analysis, etc.)
│       ├── components/       # UI components (NetworkGraph, Sankey, etc.)
│       └── services/         # API client
├── data/                     # Data files
│   ├── entities/             # Entity CSV files
│   ├── financial/            # Money flow data
│   ├── foia/                 # FOIA targets
│   └── scripts/              # Data enrichment pipeline
│       ├── entity_recognition.py
│       ├── enrich_entity_flows.py
│       └── combine_all_data.py
├── docker/                   # Docker deployment
│   ├── Caddyfile
│   └── init-db.sql
├── docs/                     # Documentation
├── START.bat                 # Windows guided launcher (recommended)
├── START.sh                  # macOS/Linux guided launcher
├── UNINSTALL.bat             # Windows one-click uninstaller
├── UNINSTALL.sh              # macOS/Linux uninstaller
├── install.bat               # Windows full installer
├── install.sh                # macOS/Linux full installer
├── RUN.bat                   # Windows quick launch
├── RUN.sh                    # macOS/Linux quick launch
├── LaunchRawHorse.vbs        # Windows launcher with icon support
├── docker-compose.yml        # Production deployment
└── config.yaml               # Application configuration
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
Visualize data through dedicated full-page views:
- **Network Graph** (`/analysis/network`): Interactive force-directed graph of entity relationships
- **Sankey Diagram** (`/analysis/sankey`): Financial flow visualization between entities
- **Intelligence Stack Filter**: Toggle visibility by hierarchy level (Control Group, Administrators, FFRDCs, Prime Contractors, Facilities, Programs)

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
- Ensure Node.js 20+ installed

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

**Completed in v0.4.0:**
- [x] Intelligence Stack hierarchy filter and Pyramid visualization
- [x] Separate visualization pages (network/sankey/pyramid)
- [x] Advanced search with suggestions, history, and row highlighting
- [x] One-click uninstall (Windows and macOS/Linux)
- [x] Docker deployment configuration
- [x] PostgreSQL database support
- [x] JWT authentication system
- [x] spaCy NLP entity extraction pipeline
- [x] Financial/materials flow enrichment algorithms
- [x] CI/CD workflow upgrades (GitHub Actions v4, caching, concurrency)

**Upcoming (v0.5.0):**
- [ ] UFO database enrichment (NUFORC, MUFON CMS, GEIPAN, and more)
- [ ] VPS deployment guide with one-click setup
- [ ] User authentication UI in frontend
- [ ] Timeline visualization for entity relationships
- [ ] Batch data import from CSV upload
- [ ] Redis caching for improved performance
- [ ] Plugin system for custom analysis

## OPINT Philosophy

Project RawHorse follows **Open Intelligence (OPINT)** principles:

1. **Transparency** — All data sources are cited, all algorithms are open source, all findings are reproducible.
2. **Public data only** — We never use, store, or process classified, proprietary, or personally identifiable information.
3. **Community verification** — Every data contribution goes through a public review process (GitHub PR).
4. **Tool neutrality** — The application presents data without editorial bias; users draw their own conclusions.
5. **Accessibility** — One-click install, no technical expertise required, runs on any modern computer.

We believe that open-source intelligence tools empower citizens, researchers, and journalists to independently verify claims about government programs and spending. If you share this vision, consider [contributing](CONTRIBUTING.md).

## Support

- **Issues**: [GitHub Issues](https://github.com/ConsciousEnergy/ProjectRawHorse/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ConsciousEnergy/ProjectRawHorse/discussions)
- **Documentation**: See `docs/` directory
- **Security**: See [SECURITY.md](SECURITY.md) for vulnerability reporting

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

### v0.4.0 (2026-02)
- **Data Enrichment**: 26 new entities from UAPGerb's "The Hidden Wing" transcript (Air Force SAF hierarchy)
- **Intelligence Stack Pyramid**: Hierarchical L1–L6 visualization with chain-of-command tracing
- **Advanced Search**: Suggestions, recent results/queries, visual row highlighting in Browse
- **One-Click Uninstall**: `UNINSTALL.bat` / `UNINSTALL.sh` with server detection and removal summary
- **CI/CD**: Upgraded GitHub Actions, npm/pip caching, concurrency, build hardening
- **Infrastructure**: Docker support, PostgreSQL, JWT auth, removed Git LFS
- See [CHANGELOG_v0.4.0.md](CHANGELOG_v0.4.0.md) for full details

### v0.3.0 (2025-12)
- Enhanced search functionality
- FOIA quality scoring
- Data versioning and refresh
- See [CHANGELOG_v0.3.0.md](CHANGELOG_v0.3.0.md)

### v0.2.1 (2025-11-11)
- Bug fixes and stability improvements
- See [docs/RELEASE_NOTES_v0.2.1.md](docs/RELEASE_NOTES_v0.2.1.md)

### v0.2.0 (2025-11-11)
- Initial public release
- Core browsing, analysis, and export features
- GitHub PR automation for contributions
- Cross-platform desktop application
- 1-click installation for non-technical users
- See [docs/RELEASE_NOTES_v0.2.0.md](docs/RELEASE_NOTES_v0.2.0.md)

---

**Built with transparency and accountability in mind.**

Licensed under GNU AGPL v3 | See DISCLAIMER.md for legal information

**Ready to explore? Download and double-click `START.bat` (Windows) or run `./START.sh` (Mac/Linux)!**
