#!/usr/bin/env bash
# PostgreSQL restore script for Project RawHorse.
#
# Usage: ./restore.sh <backup_file>

set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <backup_file.sql.gz>"
  exit 1
fi

BACKUP_FILE="$1"
if [ ! -f "$BACKUP_FILE" ]; then
  echo "Error: Backup file not found: $BACKUP_FILE"
  exit 1
fi

DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${POSTGRES_USER:-prh}"
DB_NAME="${POSTGRES_DB:-rawhorse}"

echo "[$(date)] Restoring from: $BACKUP_FILE"
echo "WARNING: This will overwrite the current database. Press Ctrl+C to abort."
sleep 5

gunzip -c "$BACKUP_FILE" | PGPASSWORD="${DB_PASSWORD:-changeme}" pg_restore \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  --clean \
  --if-exists \
  --no-owner

echo "[$(date)] Restore complete."
