#!/usr/bin/env bash
# Project RawHorse - macOS/Linux Uninstaller
# Removes venv, node_modules, build artifacts, cache, and optionally the database.
set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# --force or -y: skip all prompts
FORCE=0
for arg in "$@"; do
  [[ "$arg" == "--force" || "$arg" == "-y" ]] && FORCE=1 && break
done

echo "============================================================"
echo "  Project RawHorse - Uninstaller"
echo "============================================================"
echo ""
echo "This will remove:"
echo "  - Python virtual environment (venv/ or ../venv/)"
echo "  - Node modules (frontend/node_modules/)"
echo "  - Compiled frontend (backend/static/, frontend/dist/)"
echo "  - Build artifacts (dist/, build/, rawhorse.spec)"
echo "  - Environment config (.env)"
echo "  - Cache and logs (data/scripts/.cache/, __pycache__/, logs/, *.log)"
echo "  - Enrichment outputs (enriched_flows_*.csv, test_*.csv, *.backup)"
echo ""

if [[ $FORCE -eq 0 ]]; then
  read -rp "Continue with uninstall? (y/n): " CONFIRM
  [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]] && echo "Cancelled." && exit 0
else
  echo "Running in force mode (no prompts)."
fi

# Check if port 8000 is in use (server running)
PORT_IN_USE=0
if command -v lsof >/dev/null 2>&1; then
  lsof -i :8000 -sTCP:LISTEN -t >/dev/null 2>&1 && PORT_IN_USE=1
elif command -v ss >/dev/null 2>&1; then
  ss -tlnp 2>/dev/null | grep -q ':8000 ' && PORT_IN_USE=1
fi
if [[ $PORT_IN_USE -eq 1 ]]; then
  echo ""
  echo "WARNING: A process is listening on port 8000 (Project RawHorse may be running)."
  if [[ $FORCE -eq 0 ]]; then
    read -rp "Stop the server first? (y/n): " KILL
    if [[ "$KILL" == "y" || "$KILL" == "Y" ]]; then
      if command -v lsof >/dev/null 2>&1; then
        PIDS=$(lsof -i :8000 -sTCP:LISTEN -t 2>/dev/null)
        [[ -n "$PIDS" ]] && echo "$PIDS" | xargs -r kill -9 2>/dev/null || true
      fi
    fi
  fi
  echo ""
fi

if [[ $FORCE -eq 0 ]]; then
  read -rp "Keep your database (data/prh.db) for future use? (y/n): " KEEPDB
else
  KEEPDB="n"
fi

echo ""
echo "Removing artifacts..."
echo ""

# Summary: R=removed, K=kept, N=not found
SUM_VENV="N"
SUM_NM="N"
SUM_DIST="N"
SUM_BUILD="N"
SUM_STATIC="N"
SUM_FDIST="N"
SUM_SPEC="N"
SUM_ENV="N"
SUM_DB="N"
SUM_CACHE="N"
SUM_PYC="N"
SUM_LOGS="N"
SUM_CSV="N"
SUM_BACKUP="N"
SUM_DESKTOP="N"
SUM_PYC="N"

# 1. venv/ or ../venv/
if [[ -d "$SCRIPT_DIR/venv" ]] && [[ -f "$SCRIPT_DIR/venv/bin/activate" ]]; then
  echo "Removing virtual environment (venv/)..."
  rm -rf "$SCRIPT_DIR/venv" 2>/dev/null || true
  SUM_VENV="R"
elif [[ -d "$SCRIPT_DIR/../venv" ]] && [[ -f "$SCRIPT_DIR/../venv/bin/activate" ]]; then
  echo "Removing virtual environment (../venv/)..."
  rm -rf "$SCRIPT_DIR/../venv" 2>/dev/null || true
  SUM_VENV="R"
fi

# 2. frontend/node_modules
if [[ -d "$SCRIPT_DIR/frontend/node_modules" ]]; then
  echo "Removing node_modules..."
  rm -rf "$SCRIPT_DIR/frontend/node_modules" 2>/dev/null || true
  SUM_NM="R"
fi

# 3. dist/, build/
if [[ -d "$SCRIPT_DIR/dist" ]]; then rm -rf "$SCRIPT_DIR/dist" 2>/dev/null || true; SUM_DIST="R"; fi
if [[ -d "$SCRIPT_DIR/build" ]]; then rm -rf "$SCRIPT_DIR/build" 2>/dev/null || true; SUM_BUILD="R"; fi

# 4. backend/static/, frontend/dist/
if [[ -d "$SCRIPT_DIR/backend/static" ]]; then
  echo "Removing backend/static/..."
  rm -rf "$SCRIPT_DIR/backend/static" 2>/dev/null || true
  SUM_STATIC="R"
fi
if [[ -d "$SCRIPT_DIR/frontend/dist" ]]; then
  echo "Removing frontend/dist/..."
  rm -rf "$SCRIPT_DIR/frontend/dist" 2>/dev/null || true
  SUM_FDIST="R"
fi

# 5. rawhorse.spec
if [[ -f "$SCRIPT_DIR/rawhorse.spec" ]]; then rm -f "$SCRIPT_DIR/rawhorse.spec" 2>/dev/null || true; SUM_SPEC="R"; fi

# 6. .env
if [[ -f "$SCRIPT_DIR/.env" ]]; then
  echo "Removing .env..."
  rm -f "$SCRIPT_DIR/.env" 2>/dev/null || true
  SUM_ENV="R"
fi

# 7. data/prh.db
if [[ "$KEEPDB" != "y" && "$KEEPDB" != "Y" ]]; then
  if [[ -f "$SCRIPT_DIR/data/prh.db" ]]; then
    echo "Removing database..."
    rm -f "$SCRIPT_DIR/data/prh.db" 2>/dev/null || true
    SUM_DB="R"
  fi
else
  [[ -f "$SCRIPT_DIR/data/prh.db" ]] && SUM_DB="K"
fi

# 8. data/scripts/.cache/
if [[ -d "$SCRIPT_DIR/data/scripts/.cache" ]]; then
  echo "Removing data/scripts/.cache/..."
  rm -rf "$SCRIPT_DIR/data/scripts/.cache" 2>/dev/null || true
  SUM_CACHE="R"
fi

# 9. __pycache__ in backend
if [[ -d "$SCRIPT_DIR/backend" ]]; then
  if find "$SCRIPT_DIR/backend" -type d -name "__pycache__" 2>/dev/null | grep -q .; then
    find "$SCRIPT_DIR/backend" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    SUM_PYC="R"
  fi
fi

# 10. logs/, *.log
if [[ -d "$SCRIPT_DIR/logs" ]]; then rm -rf "$SCRIPT_DIR/logs" 2>/dev/null || true; SUM_LOGS="R"; fi
rm -f "$SCRIPT_DIR"/*.log 2>/dev/null || true
[[ "$SUM_LOGS" != "R" ]] && SUM_LOGS="N"

# 11. data/financial enriched_flows_*.csv, test_*.csv
if [[ -d "$SCRIPT_DIR/data/financial" ]]; then
  rm -f "$SCRIPT_DIR/data/financial/enriched_flows_"*.csv 2>/dev/null || true
  rm -f "$SCRIPT_DIR/data/financial/test_"*.csv 2>/dev/null || true
  SUM_CSV="R"
fi

# 12. *.backup, *_backup.py, *_backup*.csv
rm -f "$SCRIPT_DIR"/*.backup "$SCRIPT_DIR"/*_backup.py "$SCRIPT_DIR"/*_backup*.csv 2>/dev/null || true
find "$SCRIPT_DIR/data" -maxdepth 3 -type f \( -name "*.backup" -o -name "*_backup*.csv" \) 2>/dev/null | while read -r f; do rm -f "$f" 2>/dev/null; done
SUM_BACKUP="R"

# 13. Linux desktop entry
DESKTOP_FILE="${HOME}/.local/share/applications/ProjectRawHorse.desktop"
if [[ -f "$DESKTOP_FILE" ]]; then
  if [[ $FORCE -eq 0 ]]; then
    read -rp "Remove Linux desktop entry? (y/n): " RMDESKTOP
    if [[ "$RMDESKTOP" == "y" || "$RMDESKTOP" == "Y" ]]; then
      rm -f "$DESKTOP_FILE" 2>/dev/null || true
      SUM_DESKTOP="R"
    else
      SUM_DESKTOP="K"
    fi
  else
    rm -f "$DESKTOP_FILE" 2>/dev/null || true
    SUM_DESKTOP="R"
  fi
fi

echo ""
echo "============================================================"
echo "  Removal summary"
echo "============================================================"
echo "  venv/ or ../venv/     : $SUM_VENV"
echo "  frontend/node_modules : $SUM_NM"
echo "  dist/                 : $SUM_DIST"
echo "  build/                : $SUM_BUILD"
echo "  backend/static/       : $SUM_STATIC"
echo "  frontend/dist/        : $SUM_FDIST"
echo "  rawhorse.spec         : $SUM_SPEC"
echo "  .env                  : $SUM_ENV"
echo "  data/prh.db           : $SUM_DB"
echo "  data/scripts/.cache/  : $SUM_CACHE"
echo "  __pycache__/          : $SUM_PYC"
echo "  logs, *.log           : $SUM_LOGS"
echo "  enrichment outputs    : $SUM_CSV"
echo "  backups               : $SUM_BACKUP"
echo "  Linux .desktop        : $SUM_DESKTOP"
echo "  R=removed  K=kept  N=not found"
echo "============================================================"
echo ""
echo "Uninstall complete. To finish, delete this project folder:"
echo "  $SCRIPT_DIR"
echo ""
