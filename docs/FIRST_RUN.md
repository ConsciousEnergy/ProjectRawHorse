# First Run Walkthrough

**Version:** v0.4.0  
**Last Updated:** February 2026

This guide explains what happens when you run Project RawHorse for the first time and how to navigate the application.

---

## What Happens When You Double-Click START

### 1. Environment Check (30 seconds)

The launcher checks for Python and Node.js. If they're installed, it proceeds. If not, it tells you what to install and where to get it.

### 2. Virtual Environment Setup (1–2 minutes)

A Python virtual environment is created in the project directory. This isolates Project RawHorse's dependencies from your system Python. You'll see packages being downloaded and installed.

### 3. Frontend Build (2–5 minutes)

Node.js dependencies are installed (`npm install`) and the React frontend is compiled (`npm run build`). This is the longest step on the first run. Subsequent launches skip this if nothing changed.

### 4. Database Creation (10–30 seconds)

The SQLite database (`data/prh.db`) is created and populated from CSV data files. This includes all entities, money flows, federal awards, FOIA targets, and relationships.

### 5. Server Starts

The FastAPI backend starts on port 8000 (or the next available port). Your default browser opens automatically to `http://127.0.0.1:8000`.

---

## Navigating the Application

### Dashboard

The landing page. Shows:
- **Quick statistics**: Total entities, money flows, awards, and FOIA targets in the database
- **Quick-access cards**: Jump directly to Browse, Analysis, Export, or Contribute

### Browse

The data exploration hub. Four tabs:

| Tab | What It Shows |
|-----|--------------|
| **Entities** | Organizations, agencies, contractors, programs |
| **Money Flows** | Financial transactions and relationships between entities |
| **Awards** | Federal contracts and grants from USAspending.gov |
| **FOIA Targets** | Suggested FOIA requests with quality scoring |

**Tips:**
- Use the **search bar** at the top of each tab to filter results
- Click **column headers** to sort ascending/descending
- Use **pagination controls** at the bottom to navigate large datasets
- **Filter chips** show active filters — click the X to remove them

### Analysis

Interactive visualizations on dedicated full-page views:

| Visualization | Route | What It Shows |
|--------------|-------|---------------|
| **Network Graph** | `/analysis/network` | Force-directed graph of entity relationships. Drag nodes to rearrange, scroll to zoom, hover for details. |
| **Sankey Diagram** | `/analysis/sankey` | Financial flows between entities. Width of bands represents dollar amounts. |
| **Intelligence Pyramid** | `/analysis/pyramid` | L1–L6 hierarchy from Control Group at the top to Programs at the bottom. Click any entity for details. |

### Export

Download data for offline analysis:

| Format | Best For |
|--------|----------|
| **CSV** | Excel, Google Sheets, data analysis tools |
| **JSON** | Programmatic access, custom scripts |
| **PDF** | Reports, printing, sharing |

### Contribute

Submit new data to the community database:

1. Enter your **GitHub personal access token** (get one at https://github.com/settings/tokens)
2. Select the **contribution type** (Entity, Money Flow, Award, or FOIA Target)
3. Fill out the form with **source citations**
4. Click Submit — a GitHub pull request is automatically created for review

### About

Project information, data source attribution, and credits.

---

## Global Search

The **SearchBar** in the top navigation searches across all data types simultaneously:

- Start typing to see instant results (searches after 2+ characters)
- Results are grouped by type (Entity, Award, Money Flow, FOIA)
- Press **`/`** anywhere to focus the search bar
- Use **arrow keys** to navigate results, **Enter** to select, **Esc** to close
- Clicking a result takes you to the Browse tab with the matching row highlighted

**Suggestions dropdown** (when search is empty or < 2 chars):
- **Recent results**: Items you've clicked before
- **Recent searches**: Queries you've searched before
- **Clear history**: Removes all stored search history

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `/` | Focus the search bar |
| `Esc` | Close search dropdown or modal |
| `↑` / `↓` | Navigate search results |
| `Enter` | Select highlighted result |

---

## Where Your Data Lives

| Path | Contents |
|------|----------|
| `data/prh.db` | SQLite database (all loaded data) |
| `data/entities/` | Entity CSV source files |
| `data/financial/` | Money flow and award CSVs |
| `data/foia/` | FOIA target CSVs |
| `config.yaml` | Application settings |

The database is **rebuilt from CSVs** each time new data is loaded. You can safely delete `data/prh.db` and it will be recreated on the next startup.

---

## Subsequent Launches

After the first run, launches are much faster (30–60 seconds) because:
- The virtual environment already exists
- Node modules are already installed
- The frontend is already built (unless you changed frontend code)
- The database already exists (unless you deleted it)

---

## Uninstalling

If you decide to remove Project RawHorse:
- **Windows**: Double-click `UNINSTALL.bat`
- **macOS/Linux**: Run `./UNINSTALL.sh`

You'll be asked whether to keep your database. See [INSTALL_GUIDE.md](../INSTALL_GUIDE.md#uninstalling-project-rawhorse) for details.

---

## Need Help?

- **Troubleshooting**: See [README.md](../README.md#troubleshooting) or [INSTALL_GUIDE.md](../INSTALL_GUIDE.md)
- **Bugs**: [Report on GitHub](https://github.com/ConsciousEnergy/ProjectRawHorse/issues/new?template=bug_report.md)
- **Questions**: [GitHub Discussions](https://github.com/ConsciousEnergy/ProjectRawHorse/discussions)
