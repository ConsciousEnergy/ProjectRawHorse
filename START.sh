#!/bin/bash
# ================================================================
# Project RawHorse - One-Click Starter (macOS/Linux)
# Double-click or run this file to launch the application
# ================================================================

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
echo "           Starting Application - Please Wait"
echo "================================================================"
echo ""

# Find virtual environment
VENV_PATH=""

if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    VENV_PATH="$SCRIPT_DIR/venv"
    echo -e "${GREEN}[OK] Found virtual environment${NC}"
elif [ -f "$SCRIPT_DIR/../venv/bin/activate" ]; then
    VENV_PATH="$SCRIPT_DIR/../venv"
    echo -e "${GREEN}[OK] Found virtual environment${NC}"
else
    echo -e "${YELLOW}[!] Virtual environment not found.${NC}"
    echo ""
    echo "Would you like to install Project RawHorse now?"
    echo "This requires Python 3.10+ and Node.js 18+ to be installed."
    echo ""
    read -p "Install now? (y/n): " choice
    case "$choice" in
        y|Y )
            echo ""
            echo "Starting installation..."
            exec "$SCRIPT_DIR/install.sh"
            ;;
        * )
            echo ""
            echo "To install manually, run: ./install.sh"
            echo ""
            exit 1
            ;;
    esac
fi

# Check if backend exists
if [ ! -f "$SCRIPT_DIR/backend/main.py" ]; then
    echo -e "${RED}[ERROR] Backend not found at: $SCRIPT_DIR/backend${NC}"
    echo ""
    echo "Please ensure you're running this from the Project RawHorse directory."
    exit 1
fi

echo -e "${GREEN}[OK] Backend found${NC}"

# Check if static files exist (frontend build)
if [ ! -f "$SCRIPT_DIR/backend/static/index.html" ]; then
    echo -e "${YELLOW}[!] Frontend not built - building now...${NC}"
    echo ""
    if [ -f "$SCRIPT_DIR/frontend/package.json" ]; then
        source "$VENV_PATH/bin/activate"
        cd "$SCRIPT_DIR/frontend"
        npm install --silent 2>/dev/null || npm install
        npm run build 2>/dev/null || npm run build
        if [ -f "dist/index.html" ]; then
            rm -rf "$SCRIPT_DIR/backend/static"
            cp -r dist "$SCRIPT_DIR/backend/static"
            echo -e "${GREEN}[OK] Frontend built successfully${NC}"
        else
            echo -e "${YELLOW}[WARNING] Frontend build may have issues, continuing anyway...${NC}"
        fi
        cd "$SCRIPT_DIR"
    fi
fi

echo ""
echo "================================================================"
echo "Starting server at http://127.0.0.1:8000"
echo "Your browser will open automatically."
echo ""
echo "Press Ctrl+C to stop the server when done."
echo "================================================================"
echo ""

# Activate virtual environment and start backend
source "$VENV_PATH/bin/activate"
cd "$SCRIPT_DIR/backend"

# Use python3 if available, otherwise python
if command -v python3 &> /dev/null; then
    python3 main.py
else
    python main.py
fi
