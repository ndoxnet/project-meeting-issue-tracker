# Frontend — Project Meeting Issue Tracker

> Concept by MrHan (08974747477)
> React + TypeScript + Vite + Tailwind + React Router + TanStack Query.
> **Phase 1 skeleton.**

## ⚠️ Build off the VPS
`npm install` and `npm run build` must run on a developer machine or CI — **never
on the production VPS** (OOM risk; see ADR-004). The VPS only pulls the runtime
image.

## Layout
```
src/
  api/client.ts        # axios instance (/api base)
  layouts/AppShell.tsx # sidebar + top bar shell
  routes/nav.ts        # sidebar nav definition (role-gated)
  pages/               # Login, Dashboard, Issues, IssueDetail, Meetings,
                       # Overdue, Reports, MasterData, Users, AuditLog,
                       # Settings, NotFound
  types/index.ts       # shared domain types (placeholder)
  utils/format.ts      # date/time display helpers (Asia/Jakarta)
  App.tsx / main.tsx   # router + providers
nginx.conf             # runtime: serve static + proxy /api (port 8080)
Dockerfile             # multi-stage; build stage off-VPS only
```

## Local dev (developer machine only)
```bash
npm install
npm run dev        # http://localhost:5173, /api proxied to :8000
npm run build      # production build (OFF-VPS)
npm run typecheck  # tsc --noEmit
```

## Notes
- No lockfile committed in Phase 1 (installs happen off-VPS).
- Menu role-gating is cosmetic; the backend enforces authorization.
