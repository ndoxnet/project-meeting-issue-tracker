# Restore Procedure — Project Meeting Issue Tracker

> Concept by MrHan (08974747477)
> Reference procedure. Phase 1 does not execute any of this.

Backups are produced by `deployment/scripts/backup.sh`:
- `db-<stamp>.dump` — PostgreSQL custom-format dump (`pg_dump -Fc`).
- `attachments-<stamp>.tar.gz` — archive of the attachments volume.

## Prerequisites
- Run from the project root on the VPS, with a valid `.env`.
- The `postgres` service is up and healthy.
- **Take a fresh backup before restoring** (restore overwrites data).

## 1. Restore the database
```bash
# Copy the chosen dump into the postgres container, then pg_restore.
STAMP=YYYYMMDD-HHMMSS
docker compose --env-file .env cp \
  deployment/backup/db-$STAMP.dump postgres:/tmp/db.dump

# Clean restore into the existing database (drops & recreates objects).
docker compose --env-file .env exec -T postgres \
  pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists /tmp/db.dump
```

## 2. Restore attachments
```bash
STAMP=YYYYMMDD-HHMMSS
docker compose --env-file .env exec -T backend \
  sh -c 'rm -rf "$STORAGE_PATH"/* && tar -xzf - -C "$STORAGE_PATH"' \
  < deployment/backup/attachments-$STAMP.tar.gz
```

## 3. Verify
```bash
docker compose --env-file .env exec -T postgres \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT count(*) FROM issues;"
curl -fsS http://127.0.0.1:5200/healthz
```

## Notes
- The database is internal-only; all restore commands go through the container,
  never a host port.
- Keep backup files access-restricted — they contain sensitive data.
- If a restore follows a bad migration, restore the DB dump taken **before** that
  migration, then re-apply migrations forward as needed.
