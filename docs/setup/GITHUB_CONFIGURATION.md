# GitHub Repository Configuration Guide

**Repository:** https://github.com/ConsciousEnergy/ProjectRawHorse  
**Date:** 2025-11-11  
**Status:** Step-by-step web interface configuration

---

## 🎯 Overview

This guide walks you through configuring your GitHub repository via the web interface for maximum visibility, collaboration, and professionalism.

**Time Required:** 10-15 minutes  
**Difficulty:** Easy (point and click)

---

## ✅ Configuration Checklist

Use this checklist as you complete each section:

- [ ] Add repository description
- [ ] Add topics/tags
- [ ] Enable Issues
- [ ] Enable Discussions
- [ ] Enable Wiki (optional)
- [ ] Configure About section
- [ ] Add social preview image
- [ ] Set up branch protection (optional)
- [ ] Create first release
- [ ] Verify everything displays correctly

---

## 📝 Step 1: Add Repository Description

### Instructions:

1. **Go to:** https://github.com/ConsciousEnergy/ProjectRawHorse
2. **Click:** The ⚙️ gear icon next to "About" (top right)
3. **In "Description" field, paste:**
   ```
   Open-source UAP/UFO research data explorer with FastAPI backend and React frontend. Features 1-click installation, light/dark mode, and comprehensive federal spending analysis.
   ```
4. **In "Website" field, enter:**
   ```
   https://conscious.energy
   ```
5. **Check these boxes:**
   - ☑️ Releases
   - ☑️ Packages (if using)
   - ☐ Deployments (not yet)
6. **Click:** "Save changes"

**Result:** Your repository now has a professional description visible to all visitors.

---

## 🏷️ Step 2: Add Topics/Tags

### Instructions:

**Still in the About settings (from Step 1):**

1. **In "Topics" field, add these tags one by one:**
   ```
   uap
   ufo
   disclosure
   research
   data-analysis
   transparency
   federal-spending
   fastapi
   react
   typescript
   python
   sqlite
   open-source
   data-visualization
   ```

2. **Click:** Enter after each topic
3. **Click:** "Save changes"

**Result:** Your repository is now discoverable via these topics. Users can find it by searching GitHub topics.

**Preview:** Topics appear as clickable tags below the description.

---

## 🐛 Step 3: Enable Issues

### Instructions:

1. **Go to:** Repository Settings (click ⚙️ Settings tab at top)
2. **Scroll down to:** "Features" section
3. **Check the box:** ☑️ Issues
4. **Optional configurations:**
   - Click "Set up templates" to create bug report/feature request templates
   - We'll create issue templates later

**Result:** Users can now report bugs and request features.

**Access Issues at:** https://github.com/ConsciousEnergy/ProjectRawHorse/issues

---

## 💬 Step 4: Enable Discussions

### Instructions:

**Still in Settings → Features:**

1. **Check the box:** ☑️ Discussions
2. **Click:** "Set up discussions" (appears after checking)
3. **GitHub will create default categories:**
   - 💬 General
   - 💡 Ideas
   - 🙏 Q&A
   - 📣 Announcements
   - 🙌 Show and tell

4. **Optional:** Customize categories later

**Result:** Community forum for your project.

**Access Discussions at:** https://github.com/ConsciousEnergy/ProjectRawHorse/discussions

**Suggested first discussion:**
- Title: "Welcome to Project RawHorse! 👋"
- Category: Announcements
- Content: Introduce the project, invite collaboration

---

## 📚 Step 5: Enable Wiki (Optional)

### Instructions:

**Still in Settings → Features:**

1. **Check the box:** ☑️ Wiki
2. **Optional:** Choose wiki restrictions
   - "Public" - anyone can edit
   - "Collaborators only" - restricted editing

**Result:** Wiki for additional documentation.

**Access Wiki at:** https://github.com/ConsciousEnergy/ProjectRawHorse/wiki

**Note:** Since you have comprehensive docs/ folder, Wiki is optional.

---

## 🖼️ Step 6: Add Social Preview Image

### Instructions:

1. **Go to:** Repository Settings
2. **Scroll down to:** "Social preview" section
3. **Click:** "Upload an image..."
4. **Upload:** Your project logo (PRHLogo.png)
   - **Recommended size:** 1280 x 640 px
   - **Format:** PNG or JPG
   - **Max size:** 1 MB

5. **Alternatively:** Create a custom banner with:
   - Project name "Project RawHorse"
   - Tagline "Open UAP Research Data Explorer"
   - Purple & gold color scheme
   - Dimensions: 1280 x 640 px

**Tools for creating banner:**
- Canva (free)
- Figma (free)
- Photoshop
- GIMP (free)

**Result:** Beautiful preview image when sharing repository links on social media.

---

## 🛡️ Step 7: Branch Protection (Optional but Recommended)

### Instructions:

1. **Go to:** Settings → Branches
2. **Click:** "Add branch protection rule"
3. **Branch name pattern:** `main`
4. **Recommended settings:**
   - ☑️ Require a pull request before merging
   - ☑️ Require approvals (1)
   - ☑️ Dismiss stale pull request approvals when new commits are pushed
   - ☐ Require status checks to pass (set up later with CI/CD)
   - ☑️ Require conversation resolution before merging
   - ☐ Require signed commits (optional, more secure)
   - ☑️ Include administrators (you can override if needed)

5. **Click:** "Create" or "Save changes"

**Result:** Protected main branch prevents accidental force pushes and requires reviews.

**Note:** If you're the only contributor initially, you can skip this and add it later.

---

## 🏆 Step 8: Create First Release (v0.1.0-alpha)

### Via Web Interface:

1. **Go to:** https://github.com/ConsciousEnergy/ProjectRawHorse/releases
2. **Click:** "Create a new release"
3. **Click:** "Choose a tag" → Type: `v0.1.0-alpha` → Click "Create new tag"
4. **Release title:** `Project RawHorse v0.1.0-alpha - Initial Release`
5. **Description - paste:**

```markdown
# 🎉 Project RawHorse - Initial Alpha Release

Open-source UAP/UFO research data explorer now available!

## ✨ Features

### Core Functionality
- 🗄️ **SQLite Database** - Fast, local data storage (prh.db)
- 🚀 **FastAPI Backend** - High-performance REST API
- ⚛️ **React Frontend** - Modern, responsive UI with TypeScript
- 🌓 **Light/Dark Mode** - Purple & gold themed interface
- 📊 **Data Visualization** - Entity relationships and financial flows

### Data Coverage
- **Entities:** 9 organizations tracked
- **Money Flows:** 28 financial relationships
- **Federal Awards:** 3 major contracts
- **FOIA Targets:** 5 prioritized requests
- **Date Range:** 2004 - 2023
- **Total Spending:** $33.29M tracked

### Installation
- ✅ **1-Click Install** - Automated setup for Windows, macOS, Linux
- ✅ **Quick Launch** - RUN.bat / RUN.sh scripts
- ✅ **Cross-Platform** - Works on all major operating systems

### Data Features
- 📂 48 organized CSV files (entities, financial, FOIA, reference)
- 📈 Refactored from 74 chaotic files (35% reduction)
- 🗂️ Clean categorical structure
- 📝 Comprehensive data documentation

## 📦 Installation

### Requirements
- Python 3.10+
- Node.js 18+
- Git with Git LFS

### Quick Start

**Windows:**
```batch
git clone https://github.com/ConsciousEnergy/ProjectRawHorse.git
cd ProjectRawHorse
install.bat
```

**macOS/Linux:**
```bash
git clone https://github.com/ConsciousEnergy/ProjectRawHorse.git
cd ProjectRawHorse
chmod +x install.sh && ./install.sh
```

After installation, use `RUN.bat` (Windows) or `RUN.sh` (macOS/Linux) for quick launch.

## 📖 Documentation

- **README:** Quick start and overview
- **PRD:** Complete product roadmap
- **Installation Guide:** Detailed setup instructions
- **Contribution Guide:** How to contribute data and code
- **API Documentation:** Available at `/docs` when running

## 🐛 Known Issues

- Award contribution backend endpoint not yet implemented
- FOIA Target contribution backend endpoint not yet implemented
- Network visualizations pending (D3.js integration planned)
- No unit tests yet (coming in next release)

## 🚀 Roadmap

### v0.2.0 (Next Release)
- Complete contribution workflow for all data types
- Basic network visualization with D3.js
- Enhanced search and filtering
- Statistical charts

### v1.0.0 (Future)
- Comprehensive test suite
- Cross-platform executables
- Advanced visualizations
- Community contributions integrated

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Data contribution via GitHub PRs
- Bug reports and feature requests
- Code contributions
- Documentation improvements

## 📜 License

GNU AGPL v3 - See [LICENSE](LICENSE) for details

## 🙏 Acknowledgments

- Data sourced from USASpending.gov, FOIA requests, and public records
- Built with FastAPI, React, SQLite, and love for transparency

## 📞 Contact

- **Organization:** Conscious Energy
- **Email:** support@conscious.energy
- **Website:** https://conscious.energy

---

**⚠️ ALPHA RELEASE DISCLAIMER**

This is an alpha release. Features may change, data may be incomplete, and bugs may exist. 
Use for research purposes. See DISCLAIMER.md for full legal notice.
```

6. **Check:** ☑️ "Set as a pre-release"
7. **Uncheck:** ☐ "Set as the latest release" (optional - your choice)
8. **Click:** "Publish release"

**Result:** First official release created! Users can download and install.

---

## 🎨 Step 9: Create Issue Templates

### Instructions:

1. **Go to:** Settings → Features → Issues
2. **Click:** "Set up templates"
3. **Add templates:**

**Bug Report Template:**
```yaml
name: Bug Report
about: Report a bug or issue
title: '[BUG] '
labels: bug
assignees: ''

---

**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g., Windows 11]
- Python Version: [e.g., 3.10]
- Node Version: [e.g., 18.0]

**Additional context**
Any other context about the problem.
```

**Feature Request Template:**
```yaml
name: Feature Request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: enhancement
assignees: ''

---

**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Other solutions or features you've considered.

**Additional context**
Any other context or screenshots about the feature request.
```

**Data Contribution Template:**
```yaml
name: Data Contribution
about: Submit new data or corrections
title: '[DATA] '
labels: data
assignees: ''

---

**Type of contribution:**
- [ ] New entity
- [ ] Money flow
- [ ] Federal award
- [ ] FOIA target
- [ ] Data correction

**Data details:**
[Provide the data in CSV format or structured text]

**Source/Citation:**
[Where did this data come from? Include links if possible]

**Verification:**
[How can this data be verified?]
```

---

## 📊 Step 10: Add README Badges (Optional but Cool!)

### Instructions:

Add these badges to your README.md (at the top):

```markdown
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React 18+](https://img.shields.io/badge/react-18+-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![GitHub issues](https://img.shields.io/github/issues/ConsciousEnergy/ProjectRawHorse)](https://github.com/ConsciousEnergy/ProjectRawHorse/issues)
[![GitHub stars](https://img.shields.io/github/stars/ConsciousEnergy/ProjectRawHorse)](https://github.com/ConsciousEnergy/ProjectRawHorse/stargazers)
```

---

## 🔍 Step 11: Verify Everything

### Checklist:

Visit your repository and verify:

- [ ] Description displays correctly
- [ ] Topics/tags are visible and clickable
- [ ] Website link works (conscious.energy)
- [ ] Issues tab is accessible
- [ ] Discussions tab is accessible
- [ ] Wiki tab is accessible (if enabled)
- [ ] Social preview image displays
- [ ] Release v0.1.0-alpha is visible
- [ ] README renders properly
- [ ] License shows as "AGPL-3.0"
- [ ] All docs/ files are accessible
- [ ] No _archive/ folders visible
- [ ] LFS badge shows on CSV/PNG files

---

## 📱 Step 12: Share Your Project

### Announcement Template:

**For social media / forums:**

```
🎉 Proud to announce Project RawHorse - an open-source UAP/UFO research data explorer!

✨ Features:
• FastAPI + React application
• 1-click installation
• $33M+ in federal spending tracked
• Entity relationship visualization
• Light/dark mode
• Cross-platform support

🔓 Fully open-source (GNU AGPL v3)
📊 48 organized data files
📖 Comprehensive documentation

Check it out: https://github.com/ConsciousEnergy/ProjectRawHorse

#UAP #UFO #OpenSource #DataTransparency #Python #React
```

### Where to share:
- Reddit: r/UFOs, r/UFOB, r/dataisbeautiful
- Twitter/X with hashtags
- LinkedIn
- Hacker News (Show HN)
- Product Hunt
- Discord communities
- UFO/UAP forums

---

## 🎯 Next Phase Tasks

After initial configuration:

### Immediate (This Week)
1. Create first Discussion post welcoming contributors
2. Star your own repo (it counts!)
3. Share on social media
4. Invite collaborators if you have them

### Short Term (This Month)
1. Implement remaining contribution backends
2. Add network visualizations
3. Create more releases as features are added
4. Respond to issues and discussions

### Long Term (Next Few Months)
1. Build community of contributors
2. Add comprehensive test suite
3. Create cross-platform executables
4. Set up GitHub Actions CI/CD
5. Consider GitHub Sponsors for sustainability

---

## 🏆 Success Metrics

Track your project's growth:

- **Stars:** Measure interest
- **Forks:** Measure active use
- **Issues:** Measure engagement
- **Pull Requests:** Measure contributions
- **Discussions:** Measure community
- **Traffic:** See in Insights → Traffic

**View stats at:** Repository → Insights

---

## 📞 Need Help?

- **GitHub Docs:** https://docs.github.com
- **GitHub Community:** https://github.community
- **Support:** support@conscious.energy

---

## ✅ Final Checklist

Before considering configuration complete:

- [ ] Repository configured (description, topics, website)
- [ ] Features enabled (Issues, Discussions, Wiki)
- [ ] Social preview image added
- [ ] First release created (v0.1.0-alpha)
- [ ] Issue templates created
- [ ] Branch protection considered
- [ ] README badges added (optional)
- [ ] Everything verified working
- [ ] Project shared with community
- [ ] Ready for collaboration!

---

**Configuration Status:** Ready to go live! 🚀

**Repository:** https://github.com/ConsciousEnergy/ProjectRawHorse

**Time to configure:** ~15 minutes of clicking through these steps!

