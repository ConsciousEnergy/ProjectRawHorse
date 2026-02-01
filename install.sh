#!/bin/bash
# ================================================================
# Project RawHorse - macOS/Linux 1-Click Installer
# This script automatically installs and runs Project RawHorse
# ================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo ""
echo "  ____            _           _     ____              _   _                     "
echo " |  _ \ _ __ ___ | | ___  ___| |_  |  _ \ __ ___      | | | | ___  _ __ ___  ___ "
echo " | |_) | '__/ _ \| |/ _ \/ __| __| | |_) / _\` \ \ /\ / / | |/ _ \| '__/ __|/ _ \\"
echo " |  __/| | | (_) | |  __/ (__| |_  |  _ < (_| |\ V  V /| | | (_) | |  \__ \  __/"
echo " |_|   |_|  \___/|_|\___|\___|\__| |_| \_\__,_| \_/\_/ |_|_|\___/|_|  |___/\___|"
echo ""
echo "================================================================"
echo "      Automated Installer for macOS/Linux"
echo "================================================================"
echo ""
echo "This will install dependencies and start the application."
echo "Installation typically takes 5-10 minutes on first run."
echo ""
read -p "Press Enter to continue..."

# ================================================================
# Step 1: Check Python
# ================================================================
echo ""
echo "[1/6] Checking Python installation..."

if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
elif command -v python &> /dev/null; then
    # Check if it's Python 3
    if python --version 2>&1 | grep -q "Python 3"; then
        PYTHON_CMD="python"
        PIP_CMD="pip"
    else
        echo -e "${RED}[ERROR] Python 3 is required but Python 2 was found${NC}"
        exit 1
    fi
else
    echo -e "${RED}[ERROR] Python 3 is not installed!${NC}"
    echo ""
    echo "Please install Python 3.10 or higher:"
    echo "  macOS:        brew install python3"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  Fedora:       sudo dnf install python3 python3-pip"
    echo ""
    exit 1
fi

PYVER=$($PYTHON_CMD --version 2>&1)
echo -e "       ${GREEN}$PYVER found [OK]${NC}"

# ================================================================
# Step 2: Check Node.js
# ================================================================
echo ""
echo "[2/6] Checking Node.js installation..."

if ! command -v node &> /dev/null; then
    echo -e "${RED}[ERROR] Node.js is not installed!${NC}"
    echo ""
    echo "Please install Node.js 18 or higher:"
    echo "  macOS:        brew install node"
    echo "  Ubuntu/Debian: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt install -y nodejs"
    echo "  Or visit:     https://nodejs.org/"
    echo ""
    exit 1
fi

NODEVER=$(node --version)
echo -e "       ${GREEN}Node.js $NODEVER found [OK]${NC}"

# ================================================================
# Step 3: Create Virtual Environment
# ================================================================
echo ""
echo "[3/6] Setting up Python virtual environment..."

VENV_PATH=""

# Check if venv already exists in current directory
if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    echo -e "       ${GREEN}Virtual environment already exists [OK]${NC}"
    VENV_PATH="$SCRIPT_DIR/venv"
# Check one level up (for some setups)
elif [ -f "$SCRIPT_DIR/../venv/bin/activate" ]; then
    echo -e "       ${GREEN}Found existing virtual environment [OK]${NC}"
    VENV_PATH="$SCRIPT_DIR/../venv"
else
    echo "       Creating new virtual environment..."
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] Failed to create virtual environment${NC}"
        echo "Try running: $PYTHON_CMD -m pip install --upgrade pip virtualenv"
        exit 1
    fi
    VENV_PATH="$SCRIPT_DIR/venv"
    echo -e "       ${GREEN}Virtual environment created [OK]${NC}"
fi

# ================================================================
# Step 4: Install Backend Dependencies
# ================================================================
echo ""
echo "[4/6] Installing backend dependencies..."
echo "       This may take a few minutes..."

source "$VENV_PATH/bin/activate"

cd "$SCRIPT_DIR/backend"
pip install --upgrade pip --quiet 2>/dev/null || true
pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Failed to install backend dependencies${NC}"
    exit 1
fi
echo -e "       ${GREEN}Backend dependencies installed [OK]${NC}"

# ================================================================
# Step 5: Install Frontend Dependencies
# ================================================================
echo ""
echo "[5/6] Installing frontend dependencies..."

cd "$SCRIPT_DIR/frontend"

if [ -d "node_modules" ]; then
    echo -e "       ${GREEN}Frontend dependencies already installed [OK]${NC}"
else
    echo "       Running npm install..."
    npm install --silent 2>/dev/null || npm install
    echo -e "       ${GREEN}Frontend dependencies installed [OK]${NC}"
fi

# ================================================================
# Step 6: Build Frontend
# ================================================================
echo ""
echo "[6/6] Building frontend..."

npm run build 2>/dev/null || npm run build

if [ -f "dist/index.html" ]; then
    echo -e "       ${GREEN}Frontend built [OK]${NC}"
    
    # Copy to backend static folder
    echo "       Copying to backend..."
    rm -rf "$SCRIPT_DIR/backend/static"
    cp -r dist "$SCRIPT_DIR/backend/static"
    echo -e "       ${GREEN}Frontend deployed [OK]${NC}"
else
    echo -e "${YELLOW}[WARNING] Frontend build incomplete - application may run in API-only mode${NC}"
fi

cd "$SCRIPT_DIR"

# ================================================================
# Installation Complete!
# ================================================================
echo ""
echo "================================================================"
echo "            Installation Complete!"
echo "================================================================"
echo ""
echo "You can now:"
echo "  - Run ./START.sh or ./RUN.sh to launch the application"
echo ""
echo "Starting Project RawHorse now..."
echo "Your browser will open automatically at http://127.0.0.1:8000"
echo ""
echo "Press Ctrl+C to stop the server when done."
echo "================================================================"
echo ""

# Start the application
cd "$SCRIPT_DIR/backend"
$PYTHON_CMD main.py
