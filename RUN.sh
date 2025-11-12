#!/bin/bash
# Project RawHorse - Quick Launch (macOS/Linux)
# Run this after installation to start the application

echo "================================================================"
echo "Project RawHorse - Starting Application"
echo "================================================================"
echo ""

# Check if installed
if [ ! -d "venv" ]; then
    echo "ERROR: Project RawHorse is not installed yet!"
    echo ""
    echo "Please run './install.sh' first to install dependencies."
    echo ""
    exit 1
fi

echo "Starting server..."
echo "Your browser will open automatically."
echo ""
echo "Press Ctrl+C to stop the server when done."
echo ""

# Activate virtual environment and start
source venv/bin/activate
cd backend
python3 main.py
