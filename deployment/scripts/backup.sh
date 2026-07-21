#!/usr/bin/env bash
# Concept by MrHan (08974747477)
# Backup script for the Project Meeting Issue Tracker.
#   - PostgreSQL: pg_dump (custom format) from the internal-only postgres service.
#   - Attachments: tar of the attachments volume (via the backend container).
#
# Phase 1: reference script. It is NOT run in Phase 1. Run it from the project
# root on the VPS during operation (e.g. via cron). It never exposes the DB port.
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_DIR"

ENV_FILE="${ENV_FILE:-.env}"
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_DIR/deployment/backup}"
STAMP="$(date +%Y%m%d-%H%M%S)"
RETAIN_DAYS="${RETAIN_DAYS:-14}"

# shellcheck disable=SC1090
set -a; [ -f "$ENV_FILE" ] && . "$ENV_FILE"; set +a

mkdir -p "$BACKUP_DIR"

echo "[backup] pg_dump -> $BACKUP_DIR/db-$STAMP.dump"
docker compose --env-file "$ENV_FILE" exec -T postgres \
    pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc \
    > "$BACKUP_DIR/db-$STAMP.dump"

echo "[backup] attachments -> $BACKUP_DIR/attachments-$STAMP.tar.gz"
docker compose --env-file "$ENV_FILE" exec -T backend \
    tar -czf - -C "${STORAGE_PATH:-/app/storage}" . \
    > "$BACKUP_DIR/attachments-$STAMP.tar.gz"

echo "[backup] pruning backups older than ${RETAIN_DAYS} days"
find "$BACKUP_DIR" -type f \( -name 'db-*.dump' -o -name 'attachments-*.tar.gz' \) \
    -mtime "+${RETAIN_DAYS}" -print -delete || true

echo "[backup] done. Store copies OFF-host; backups contain sensitive data."
