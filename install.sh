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

# Parse --offline flag
OFFLINE=""
for arg in "$@"; do
    [ "$arg" = "--offline" ] && OFFLINE=1 && break
done

# ================================================================
# Step 1: Check Python
# ================================================================
echo ""
echo "[1/7] Checking Python installation..."

if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
elif command -v python &> /dev/null; then
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
    echo "  https://www.python.org/downloads/"
    echo "  macOS: brew install python3"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

PYVER=$($PYTHON_CMD --version 2>&1)
PY_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)' 2>/dev/null || echo "0")
PY_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)' 2>/dev/null || echo "0")
if [ "$PY_MAJOR" -ne 3 ] || [ "$PY_MINOR" -lt 10 ]; then
    echo -e "${RED}[ERROR] Python 3.10+ required (you have $PYVER). Download: https://www.python.org/downloads/${NC}"
    exit 1
fi
echo -e "       ${GREEN}$PYVER found [OK]${NC}"

# ================================================================
# Step 2: Check Node.js
# ================================================================
echo ""
echo "[2/7] Checking Node.js installation..."

if ! command -v node &> /dev/null; then
    echo -e "${RED}[ERROR] Node.js is not installed!${NC}"
    echo ""
    echo "Please install Node.js 18 or higher: https://nodejs.org/"
    exit 1
fi

NODEVER=$(node --version)
NODE_MAJOR=$(node -p "process.version.split('.')[0].slice(1)" 2>/dev/null || echo "0")
if [ "$NODE_MAJOR" -lt 18 ]; then
    echo -e "${RED}[ERROR] Node.js 18+ required (you have $NODEVER). Download: https://nodejs.org/${NC}"
    exit 1
fi
echo -e "       ${GREEN}Node.js $NODEVER found [OK]${NC}"

# ================================================================
# Step 3: Create Virtual Environment
# ================================================================
echo ""
echo "[3/7] Setting up Python virtual environment..."

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
echo "[4/7] Installing backend dependencies..."
echo "       This may take a few minutes..."

source "$VENV_PATH/bin/activate"

cd "$SCRIPT_DIR/backend"
pip install --upgrade pip --quiet 2>/dev/null || true
PIP_RETRIES=0
while true; do
    pip install -r requirements.txt --quiet 2>/dev/null && break
    PIP_RETRIES=$((PIP_RETRIES + 1))
    [ $PIP_RETRIES -ge 3 ] && echo -e "${RED}[ERROR] Failed to install backend dependencies after 3 attempts${NC}" && exit 1
    echo "       Retry $PIP_RETRIES/3..."
done
echo -e "       ${GREEN}Backend dependencies installed [OK]${NC}"

# ================================================================
# Step 5: Install Frontend Dependencies
# ================================================================
echo ""
echo "[5/7] Installing frontend dependencies..."

cd "$SCRIPT_DIR/frontend"

if [ -d "node_modules" ]; then
    echo -e "       ${GREEN}Frontend dependencies already installed [OK]${NC}"
else
    NPM_RETRIES=0
    while true; do
        echo "       Running npm install (attempt $((NPM_RETRIES+1))/3)..."
        npm install --silent 2>/dev/null || npm install
        [ $? -eq 0 ] && break
        NPM_RETRIES=$((NPM_RETRIES + 1))
        [ $NPM_RETRIES -ge 3 ] && echo -e "${YELLOW}[WARNING] npm install had issues after 3 attempts - continuing${NC}" && break
    done
    echo -e "       ${GREEN}Frontend dependencies installed [OK]${NC}"
fi

# ================================================================
# Step 6: Build Frontend
# ================================================================
echo ""
echo "[6/7] Building frontend..."

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
# Step 7: Generate .env with SECRET_KEY if missing
# ================================================================
echo ""
echo "[7/7] Checking environment..."

if [ ! -f ".env" ]; then
    echo "       Generating .env with secure SECRET_KEY..."
    source "$VENV_PATH/bin/activate"
    python3 -c "import secrets; open('.env','w').write('SECRET_KEY=' + secrets.token_urlsafe(32) + '\nAUTH_ENABLED=false\n')"
    echo -e "       ${GREEN}.env created [OK]${NC}"
else
    echo -e "       ${GREEN}.env exists [OK]${NC}"
fi

echo "       Verifying backend imports..."
cd "$SCRIPT_DIR/backend"
$PYTHON_CMD -c "from database import init_database; from data_loader import load_all_data; print('OK')" 2>/dev/null && echo -e "       ${GREEN}Backend OK${NC}" || echo -e "${YELLOW}[WARNING] Backend import check failed - app may still run${NC}"
cd "$SCRIPT_DIR"
[ -f "backend/static/index.html" ] && echo -e "       ${GREEN}Frontend build present [OK]${NC}" || echo -e "${YELLOW}[WARNING] Frontend static files missing - run install again or build frontend manually${NC}"

echo "       Checking for known vulnerabilities (optional)..."
(pip show pip-audit >/dev/null 2>&1 && pip-audit -r "$SCRIPT_DIR/backend/requirements.txt" 2>/dev/null) || true
(cd "$SCRIPT_DIR/frontend" && npm audit --audit-level=high 2>/dev/null) || true

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
