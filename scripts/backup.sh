#!/usr/bin/env bash
# Dumps PostgreSQL to a timestamped file. Run from project root or via cron.
# Usage: ./scripts/backup.sh [backup-dir]
# Env vars (read from .env if present): POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load .env if available
if [[ -f "$PROJECT_ROOT/.env" ]]; then
  set -o allexport
  # shellcheck disable=SC1091
  source "$PROJECT_ROOT/.env"
  set +o allexport
fi

BACKUP_DIR="${1:-$PROJECT_ROOT/backups}"
DB="${POSTGRES_DB:-internship_pipeline}"
USER="${POSTGRES_USER:-internship}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_FILE="$BACKUP_DIR/${DB}_${TIMESTAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"

echo "[backup] Dumping $DB → $BACKUP_FILE"

PGPASSWORD="${POSTGRES_PASSWORD:-change-me-local-only}" \
  docker compose exec -T postgres \
  pg_dump -U "$USER" "$DB" | gzip > "$BACKUP_FILE"

echo "[backup] Done: $(du -sh "$BACKUP_FILE" | cut -f1)"

# Keep only last 7 daily backups
find "$BACKUP_DIR" -name "${DB}_*.sql.gz" -mtime +7 -delete
echo "[backup] Old backups pruned (kept last 7 days)"
