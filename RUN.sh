#!/bin/bash
# ================================================================
# Project RawHorse - Quick Launch (macOS/Linux)
# Run this after installation to start the application
# ================================================================

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "================================================================"
echo "Project RawHorse - Starting Application"
echo "================================================================"
echo ""

# Find virtual environment
VENV_PATH=""

if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    VENV_PATH="$SCRIPT_DIR/venv"
elif [ -f "$SCRIPT_DIR/../venv/bin/activate" ]; then
    VENV_PATH="$SCRIPT_DIR/../venv"
else
    echo "ERROR: Project RawHorse is not installed yet!"
    echo ""
    echo "Please run './install.sh' first to install dependencies."
    echo "Or run './START.sh' for guided installation."
    echo ""
    exit 1
fi

echo "Starting server..."
echo "Your browser will open automatically."
echo ""
echo "Press Ctrl+C to stop the server when done."
echo ""

# Activate virtual environment and start
source "$VENV_PATH/bin/activate"
cd "$SCRIPT_DIR/backend"

# Use python3 if available, otherwise python
if command -v python3 &> /dev/null; then
    python3 main.py
else
    python main.py
fi
