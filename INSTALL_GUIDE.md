# Project RawHorse - Installation Guide for Non-Technical Users

## 🚀 One-Click Installation

This guide helps you install and run Project RawHorse even if you've never used a command line before!

---

## Windows Users

### Prerequisites

Before running the installer, you need:

1. **Python 3.10 or higher**
   - Download from: https://www.python.org/downloads/
   - **IMPORTANT**: During installation, check the box "Add Python to PATH"!
   - After installing, restart your computer

2. **Node.js 18 or higher**
   - Download from: https://nodejs.org/
   - Choose the "LTS" (Long Term Support) version
   - After installing, restart your computer

### Installation Steps

1. **Download Project RawHorse**
   - Download the ZIP file
   - Extract it to a folder (e.g., `C:\RawHorse`)

2. **Run the Installer**
   - Find the file named `install.bat`
   - **Double-click** `install.bat`
   - Wait for installation to complete (5-10 minutes)
   - Your browser will open automatically

3. **Running Project RawHorse Later**
   - **Double-click** `RUN.bat` to start the application
   - Your browser opens automatically to the application

### Troubleshooting Windows

**"Python is not recognized"**
- Python is not installed or not in PATH
- Reinstall Python and check "Add Python to PATH"
- Restart your computer

**"Node is not recognized"**
- Node.js is not installed or not in PATH
- Reinstall Node.js
- Restart your computer

**"Access Denied" or "Permission Denied"**
- Right-click `install.bat` and choose "Run as Administrator"

---

## macOS Users

### Prerequisites

1. **Python 3** (usually pre-installed on macOS)
   - To verify, open Terminal and type: `python3 --version`
   - If not installed, get it from: https://www.python.org/downloads/

2. **Node.js 18 or higher**
   - Download from: https://nodejs.org/
   - Or install via Homebrew: `brew install node`

### Installation Steps

1. **Download Project RawHorse**
   - Download and extract the ZIP file
   - Move folder to a location like `~/RawHorse`

2. **Make Scripts Executable**
   - Open Terminal (Command + Space, type "Terminal")
   - Navigate to the folder:
     ```bash
     cd ~/RawHorse
     ```
   - Make scripts executable:
     ```bash
     chmod +x install.sh RUN.sh
     ```

3. **Run the Installer**
   - In Terminal, run:
     ```bash
     ./install.sh
     ```
   - Wait for installation (5-10 minutes)
   - Browser opens automatically

4. **Running Project RawHorse Later**
   - In Terminal:
     ```bash
     cd ~/RawHorse
     ./RUN.sh
     ```

### Troubleshooting macOS

**"Permission denied"**
- Run: `chmod +x install.sh RUN.sh`

**"Python3 not found"**
- Install Python: https://www.python.org/downloads/
- Or via Homebrew: `brew install python3`

**"Node not found"**
- Install Node.js: https://nodejs.org/
- Or via Homebrew: `brew install node`

---

## Linux Users

### Prerequisites

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nodejs npm
```

**Fedora:**
```bash
sudo dnf install python3 python3-pip nodejs npm
```

**Arch:**
```bash
sudo pacman -S python python-pip nodejs npm
```

### Installation Steps

1. **Download Project RawHorse**
   - Download and extract to a location like `~/RawHorse`

2. **Make Scripts Executable**
   ```bash
   cd ~/RawHorse
   chmod +x install.sh RUN.sh
   ```

3. **Run the Installer**
   ```bash
   ./install.sh
   ```

4. **Running Project RawHorse Later**
   ```bash
   cd ~/RawHorse
   ./RUN.sh
   ```

---

## What the Installer Does

1. ✅ Checks for Python and Node.js
2. ✅ Creates a Python virtual environment
3. ✅ Installs all required Python packages
4. ✅ Installs all required Node.js packages
5. ✅ Builds the frontend application
6. ✅ Starts the local server
7. ✅ Opens your browser automatically

## After Installation

- **Starting the app**: Just double-click `RUN.bat` (Windows) or run `./RUN.sh` (Mac/Linux)
- **Stopping the app**: Press `Ctrl+C` in the command window
- **Updates**: Download new version and run installer again

## System Requirements

- **Operating System**: Windows 10+, macOS 10.15+, or modern Linux
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 500MB for application + data
- **Internet**: Only needed for installation (app runs offline after)

## Getting Help

- **Cannot install Python/Node.js**: Ask a tech-savvy friend or check YouTube for installation tutorials
- **Installation fails**: Copy the error message and search online or ask for help
- **Application won't start**: Try running installer again

## Security Note

- All data processing happens on YOUR computer
- No data is sent to external servers
- Your information stays private and local

---

## Quick Reference

### Windows
- Install: Double-click `install.bat`
- Run: Double-click `RUN.bat`
- Stop: Press Ctrl+C

### macOS/Linux
- Install: `./install.sh`
- Run: `./RUN.sh`
- Stop: Press Ctrl+C

---

**Need help?** Check the README.md file or ask in the community discussions!
