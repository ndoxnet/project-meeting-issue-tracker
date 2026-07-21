# ADR-008 — Argon2 Password Hashing via pwdlib

**Status:** Accepted

## Context
Phase 1 left the hashing library open. The MVP needs a modern, well-supported
password hash with sane defaults and a clean async-friendly API.

## Decision
Use **`pwdlib[argon2]`** with `PasswordHash.recommended()` (Argon2id). Wrapper in
`app/core/passwords.py` provides `hash_password`, `verify_password`, and
`verify_and_update_password` (transparent rehash on parameter changes). Password
policy for the MVP: length 12–128, and the password may not equal the username or
email. A precomputed dummy hash is verified for unknown users to equalize timing
(reduces username enumeration). Passwords and hashes are never logged.

## Consequences
- Strong, memory-hard hashing with modern defaults.
- `passlib`/`bcrypt` are explicitly not used (avoids the passlib+bcrypt 4.x
  compatibility pitfalls flagged in Phase 1).
- Argon2's recommended parameters are intentionally slow (~0.3–0.8s/op), which
  lengthens the test suite; acceptable for correctness.

## Alternatives Considered
- **passlib[bcrypt]**: rejected — maintenance/compat friction; 72-byte truncation.
- **Direct argon2-cffi**: rejected — pwdlib gives a cleaner verify-and-update API.
