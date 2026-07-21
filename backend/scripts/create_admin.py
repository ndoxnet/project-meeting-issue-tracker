# Concept by MrHan (08974747477)
"""Create the initial admin user from environment variables.

Phase 1: placeholder. The real implementation (Phase 2) reads ADMIN_EMAIL,
ADMIN_USERNAME, and ADMIN_INITIAL_PASSWORD from the environment, hashes the
password (passlib), and inserts an ADMIN user if one does not already exist.

The password is NEVER hardcoded and NEVER printed/logged.
"""
from __future__ import annotations


def main() -> None:
    raise NotImplementedError(
        "Implemented in Phase 2: idempotently create the ADMIN user from env "
        "(ADMIN_EMAIL / ADMIN_USERNAME / ADMIN_INITIAL_PASSWORD)."
    )


if __name__ == "__main__":  # pragma: no cover
    main()
