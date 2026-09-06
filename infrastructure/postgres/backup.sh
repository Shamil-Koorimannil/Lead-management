#!/bin/sh
set -e

# Repository PostgreSQL Automated Backup Script
# Usage: ./backup.sh [/path/to/backup_dir]

BACKUP_DIR="${1:-./backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="${POSTGRES_DB:-lead_management_db}"
DB_USER="${POSTGRES_USER:-lead_user}"
DB_HOST="${POSTGRES_HOST:-postgres}"
DB_PORT="${POSTGRES_PORT:-5432}"

mkdir -p "$BACKUP_DIR"

BACKUP_FILE="${BACKUP_DIR}/lead_mgmt_backup_${TIMESTAMP}.sql.gz"

echo "[$(date)] Starting PostgreSQL backup for database '${DB_NAME}'..."

export PGPASSWORD="${POSTGRES_PASSWORD}"

pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" --clean --if-exists | gzip > "$BACKUP_FILE"

if [ -s "$BACKUP_FILE" ]; then
    echo "[$(date)] Backup completed successfully: ${BACKUP_FILE}"
else
    echo "[$(date)] ERROR: Backup file is empty or missing!" >&2
    rm -f "$BACKUP_FILE"
    exit 1
fi

# Retention cleanup: Keep backups from the last 14 days
echo "[$(date)] Cleaning up backups older than 14 days..."
find "$BACKUP_DIR" -name "lead_mgmt_backup_*.sql.gz" -mtime +14 -exec rm -f {} \;

echo "[$(date)] Backup routine finished cleanly."
