#!/bin/sh
set -e

# Repository PostgreSQL Automated Restore Script
# WARNING: This script will OVERWRITE existing database data!
# Usage: ./restore.sh /path/to/lead_mgmt_backup_YYYYMMDD_HHMMSS.sql.gz

if [ -z "$1" ]; then
    echo "ERROR: Backup file path required."
    echo "Usage: ./restore.sh /path/to/lead_mgmt_backup_YYYYMMDD_HHMMSS.sql.gz"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "ERROR: File '$BACKUP_FILE' does not exist."
    exit 1
fi

DB_NAME="${POSTGRES_DB:-lead_management_db}"
DB_USER="${POSTGRES_USER:-lead_user}"
DB_HOST="${POSTGRES_HOST:-postgres}"
DB_PORT="${POSTGRES_PORT:-5432}"

echo "=========================================================="
echo "WARNING: RESTORE PROCEDURE STARTED"
echo "Target Database: ${DB_NAME} at ${DB_HOST}:${DB_PORT}"
echo "Backup File: ${BACKUP_FILE}"
echo "=========================================================="

export PGPASSWORD="${POSTGRES_PASSWORD}"

echo "[$(date)] Decompressing and restoring database..."
gunzip -c "$BACKUP_FILE" | psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"

echo "[$(date)] Database restoration completed successfully!"
