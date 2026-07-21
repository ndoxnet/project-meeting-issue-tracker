# ADR-009 — PyJWT with HS256 Access Tokens

**Status:** Accepted

## Context
The MVP needs stateless authentication without a session store (ADR-003). A JWT
library and algorithm must be fixed, and token handling must be safe against
common pitfalls (algorithm confusion, leaking failure detail).

## Decision
Use **PyJWT** with **HS256**. Implemented in `app/core/tokens.py`:
- Tokens carry `sub`, `iat`, `exp`, `jti`, plus `role` and `type=access`.
- The signing secret comes from `SECRET_KEY` (env, validated ≥ 32 chars).
- Decoding passes an **explicit** algorithm allow-list from settings; the token's
  own `alg` header is never trusted (prevents algorithm-confusion attacks).
- `require=[sub, iat, exp, jti]` is enforced; wrong `type` is rejected.
- All failures raise one generic `TokenError` → HTTP 401 with a generic message;
  expired vs malformed vs bad-signature is not distinguished to the client.
- **Authorization uses the current DB role**, not the JWT `role` claim alone.

### Token model (MVP)
Access token only. **No** refresh token, **no** server-side revocation/blacklist,
**no** rotation. Logout is advisory: the endpoint audits the event and the client
must discard the token; the token remains valid until it expires. This limitation
is documented in SECURITY.md and the logout response message.

## Consequences
- Simple, stateless auth; no Redis.
- A stolen token is valid until expiry (mitigated by a bounded expiry). Revocation
  can be added later via a `jti` denylist if needed.

## Alternatives Considered
- **python-jose**: rejected (maintenance concerns; explicitly excluded by spec).
- **RS256/asymmetric**: deferred — unnecessary for a single-service MVP.
- **Server-side sessions**: rejected — would require a store (ADR-003).
