#!/bin/bash
# Build frontend and deploy to backend/static so the running app serves the latest UI.
# Run this from the project root (folder that contains frontend and backend).

set -e
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Building frontend..."
cd frontend && npm run build && cd ..

echo "Deploying to backend/static..."
rm -rf backend/static/*
cp -r frontend/dist/* backend/static/
echo "Done. Restart the backend and hard-refresh the browser (Ctrl+Shift+R or Cmd+Shift+R)."
