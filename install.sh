#!/bin/bash
# Project RawHorse - macOS/Linux 1-Click Installer
# This script automatically installs and runs Project RawHorse

echo "================================================================"
echo "Project RawHorse - Automated Installer for macOS/Linux"
echo "================================================================"
echo ""
echo "This will install dependencies and start the application."
echo ""
read -p "Press Enter to continue..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo ""
    echo "Please install Python 3.10 or higher:"
    echo "  macOS: brew install python3"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    echo ""
    exit 1
fi

echo "[1/5] Python found!"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed!"
    echo ""
    echo "Please install Node.js 18 or higher:"
    echo "  macOS: brew install node"
    echo "  Ubuntu/Debian: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt install -y nodejs"
    echo "  Or visit: https://nodejs.org/"
    echo ""
    exit 1
fi

echo "[2/5] Node.js found!"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "[3/5] Creating Python virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
else
    echo "[3/5] Virtual environment already exists"
fi
echo ""

# Activate virtual environment and install backend dependencies
echo "[4/5] Installing backend dependencies..."
source venv/bin/activate
cd backend
pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install backend dependencies"
    exit 1
fi
cd ..

# Install frontend dependencies
echo "[5/5] Installing frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install frontend dependencies"
        exit 1
    fi
else
    echo "Frontend dependencies already installed"
fi

# Build frontend
echo ""
echo "Building frontend..."
npm run build
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to build frontend"
    exit 1
fi

# Copy frontend to backend static
echo ""
echo "Copying frontend to backend..."
rm -rf ../backend/static
cp -r dist ../backend/static

cd ..

echo ""
echo "================================================================"
echo "Installation Complete!"
echo "================================================================"
echo ""
echo "Starting Project RawHorse..."
echo "Your browser will open automatically."
echo ""
echo "Press Ctrl+C to stop the server when done."
echo ""

# Start the application
cd backend
python3 main.py
