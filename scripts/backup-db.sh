#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STRATUM_META="$SCRIPT_DIR/.."
BACKUP_DIR="$STRATUM_META/backups"
mkdir -p "$BACKUP_DIR"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
TARGET_FILE="$BACKUP_DIR/cashflow_backup_$TIMESTAMP.sql"

echo "=================================================="
echo "📦 Stratum Database Backup Runner"
echo "   Target DB : stratum-cashflow-db (cashflow)"
echo "   Output    : $TARGET_FILE"
echo "=================================================="

if ! docker ps --format '{{.Names}}' | grep -q "^stratum-cashflow-db$"; then
    echo "❌ Error: stratum-cashflow-db container is not running."
    exit 1
fi

docker exec stratum-cashflow-db pg_dump -U postgres -d cashflow > "$TARGET_FILE"

FILE_SIZE=$(ls -lh "$TARGET_FILE" | awk '{print $5}')
echo "✅ Backup successfully created ($FILE_SIZE)."
