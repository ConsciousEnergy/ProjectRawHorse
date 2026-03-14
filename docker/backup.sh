#!/usr/bin/env bash
# PostgreSQL backup script for Project RawHorse.
# Run from the host or inside a container with access to the DB.
#
# Usage: ./backup.sh [retention_days]
# Default retention: 7 days

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
RETENTION_DAYS="${1:-7}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/prh_backup_${TIMESTAMP}.sql.gz"

DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${POSTGRES_USER:-prh}"
DB_NAME="${POSTGRES_DB:-rawhorse}"

mkdir -p "$BACKUP_DIR"

echo "[$(date)] Starting PostgreSQL backup..."
PGPASSWORD="${DB_PASSWORD:-changeme}" pg_dump \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  --format=custom \
  | gzip > "$BACKUP_FILE"

FILESIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "[$(date)] Backup complete: $BACKUP_FILE ($FILESIZE)"

echo "[$(date)] Pruning backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "prh_backup_*.sql.gz" -mtime +"$RETENTION_DAYS" -delete

REMAINING=$(find "$BACKUP_DIR" -name "prh_backup_*.sql.gz" | wc -l)
echo "[$(date)] Retained $REMAINING backups."
