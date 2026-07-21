# ADR-003 — No Redis for the MVP

**Status:** Accepted

## Context
The spec asks to avoid unnecessary infrastructure. The VPS swap is full and RAM
is tight. Common reasons to add Redis (session store, cache, queue, rate-limit
backend) are evaluated against actual MVP needs.

## Decision
**Do not add Redis** in the MVP.
- Authentication uses **stateless JWT** (no server session store).
- Dashboard aggregates are simple SQL over a modest dataset (no cache needed yet).
- Login rate-limiting for the MVP can use an in-process limiter or a DB-backed
  counter; a distributed store is unnecessary for a single backend replica.

## Consequences
- One fewer container, less RAM, less operational surface.
- If we later need cross-replica rate-limiting, background jobs, or caching, Redis
  can be added as a discrete, reversible change.

## Alternatives Considered
- **Add Redis now for rate-limiting/cache**: rejected — premature; no measured
  need; costs scarce RAM.
