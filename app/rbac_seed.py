from __future__ import annotations

from sqlalchemy import select

from .authorization import MODULES, PERMISSIONS, ROLE_PERMISSIONS
from .database import Database


def seed_rbac(db: Database) -> None:
    """Validate the canonical RBAC catalog against the current database users.

    The current User model stores a role name directly. This seed is intentionally
    non-destructive: it does not remove users or rewrite existing role values.
    It provides the single source of truth that the database-backed Role and
    Permission tables will consume in the next migration phase.
    """
    with db.Session() as session:
        roles = {user.role for user in session.scalars(select(__import__('app.database', fromlist=['User']).User)).all()}
    unknown = roles.difference(ROLE_PERMISSIONS)
    if unknown:
        raise ValueError(f"Unknown roles found in users table: {sorted(unknown)}")


__all__ = ["MODULES", "PERMISSIONS", "ROLE_PERMISSIONS", "seed_rbac"]
