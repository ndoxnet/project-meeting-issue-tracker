# ADR-004 — Build the Frontend Outside the Production VPS

**Status:** Accepted

## Context
Phase 0 discovery found the VPS at ~2–3 GB available RAM with swap 100% full and
only 2 cores, co-located with business-critical MetaTrader/Wine trading services.
A Vite production build can spike well over 1 GB RAM and risks an OOM kill that
could take down the trading services.

## Decision
The frontend is **built outside the production VPS** — on a developer machine or
CI. The resulting **Docker image** (or static artifact) is pushed to a registry;
the VPS only **pulls** and runs it. `npm install`, `vite build`, and
`docker build` for the frontend are **never** run on the VPS.

## Consequences
- No OOM risk to co-located services from frontend builds.
- Requires a registry (or artifact transfer) in the deployment pipeline.
- The frontend `Dockerfile` still contains a build stage, but that stage is only
  executed off-VPS.

## Alternatives Considered
- **Build on the VPS at low-traffic hours with memory caps**: rejected as the
  default — still risky given full swap; kept only as a documented fallback.
- **Upgrade the VPS first**: deferred — not required to proceed; may be revisited.
