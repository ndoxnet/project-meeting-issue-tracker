# Frontend Off-VPS Validation (GitHub Actions Bootstrap)

> Concept by MrHan (08974747477)
> The frontend must be installed/built/tested OFF the production VPS (ADR-004).
> This describes the GitHub-hosted-runner route. No npm ever runs on the VPS.

## Why a two-stage flow
`npm ci` requires a committed `package-lock.json`, which does not exist yet (the
Phase 2C.1 scaffold was authored on the production VPS where npm is forbidden). So:
1. **Bootstrap** (`frontend-bootstrap-validation.yml`) runs `npm install` on a
   GitHub runner, validates everything, and uploads the produced `package-lock.json`
   and the real generated `schema.ts` as **artifacts** (the workflow is read-only
   and cannot commit back).
2. A human commits those two files.
3. The **permanent** workflow (`frontend-validation.yml`, currently a `.template`)
   is activated and uses `npm ci` + `check:api` on every PR/push.

## Prerequisite
Connect this repository to a **private** GitHub repository (no remote is configured
locally today):
```bash
git remote add origin git@github.com:<org>/<repo>.git   # example — use your repo
git push -u origin master
```
Until a remote exists, the workflows are committed but cannot run.

## Stage 1 — Run the bootstrap workflow
1. Push the branch that contains `.github/workflows/frontend-bootstrap-validation.yml`.
2. GitHub → **Actions** → **Frontend Bootstrap Validation** → **Run workflow**.
3. Wait for a green run. It performs: `npm install` → `generate:api` → `lint` →
   `typecheck` → `test` (×2) → `build` → source-map check → secret scan →
   `npm audit --omit=dev --audit-level=high`.
4. Download the artifact **`frontend-bootstrap-artifacts`**.

## Stage 2 — Commit the produced files (on a trusted machine)
Extract from the artifact and copy into the repo at the SAME paths:
```
frontend/package-lock.json
frontend/src/api/generated/schema.ts
```
Then:
```bash
git add frontend/package-lock.json frontend/src/api/generated/schema.ts
git commit -m "chore: add frontend lockfile and generated api types (from CI bootstrap)"
```
Review the generated `schema.ts` diff (placeholder → real). **Do NOT** copy
`node_modules/`, `dist/`, `coverage/`, `.env*`, npm credentials, or any logs.

## Stage 3 — Activate the permanent workflow
```bash
git mv .github/workflows/frontend-validation.yml.template \
       .github/workflows/frontend-validation.yml
git commit -m "ci: activate permanent frontend validation (npm ci)"
```
Push and confirm the **Frontend Validation** workflow is green (it runs `npm ci`
and `npm run check:api`).

## Preferred alternative — developer workstation
If a trusted laptop/dev VM is available, skip the artifact dance:
```bash
cd frontend
npm install                 # creates package-lock.json
npm run generate:api        # real schema.ts
npm run check:api && npm run lint && npm run typecheck && npm run test && npm run build
git add package-lock.json src/api/generated/schema.ts
git commit -m "chore: add frontend lockfile and generated api types"
```
Then push and let the permanent CI validate with `npm ci`. The artifact method is a
fallback when no dev workstation exists.

## Security notes
- Both workflows use `permissions: contents: read` — they cannot push or deploy.
- No GitHub Secrets are required or used. No VPS/SSH connection. No production
  backend calls (tests are MSW-mocked in jsdom). Artifacts are limited to the
  lockfile + generated schema and expire in 7 days.
