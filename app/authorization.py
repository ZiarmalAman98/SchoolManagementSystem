from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import User


# Phase 1 RBAC foundation. Permissions are deliberately explicit so they can
# later be persisted in Role/Permission tables without changing the callers.
PERMISSIONS: tuple[str, ...] = (
    "view", "create", "edit", "delete", "print", "export", "import",
    "approve", "reject", "pay", "collect", "manage", "restore", "backup",
)

MODULES: tuple[str, ...] = (
    "students", "teachers", "academics", "attendance", "exams", "results",
    "fees", "hr", "library", "transport", "inventory", "health", "parents",
    "communication", "events", "discipline", "documents", "certificates",
    "reports", "users", "settings", "backup", "audit",
)

ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "Super Admin": frozenset(f"{module}.{permission}" for module in MODULES for permission in PERMISSIONS),
    "School Admin": frozenset(f"{module}.{permission}" for module in MODULES for permission in PERMISSIONS if permission not in {"delete", "restore"}),
    "Principal": frozenset(
        f"{module}.{permission}"
        for module in ("students", "teachers", "academics", "attendance", "exams", "results", "fees", "hr", "reports", "documents", "certificates")
        for permission in ("view", "create", "edit", "print", "export", "approve")
    ),
    "Vice Principal": frozenset(
        f"{module}.{permission}"
        for module in ("students", "teachers", "academics", "attendance", "exams", "results", "reports")
        for permission in ("view", "create", "edit", "print", "export")
    ),
    "Academic Manager": frozenset(
        f"{module}.{permission}"
        for module in ("students", "teachers", "academics", "attendance", "exams", "results", "reports")
        for permission in ("view", "create", "edit", "print", "export", "approve")
    ),
    "Teacher": frozenset(
        f"{module}.{permission}"
        for module in ("students", "attendance", "exams", "results", "academics")
        for permission in ("view", "create", "edit", "print", "export")
    ),
    "Accountant": frozenset(
        f"{module}.{permission}"
        for module in ("fees", "reports")
        for permission in ("view", "create", "edit", "print", "export", "collect", "pay")
    ),
    "Receptionist": frozenset(
        f"{module}.{permission}"
        for module in ("students", "parents", "fees", "documents", "communication")
        for permission in ("view", "create", "edit", "print")
    ),
    "Librarian": frozenset(
        f"{module}.{permission}"
        for module in ("students", "library", "reports")
        for permission in ("view", "create", "edit", "print", "export")
    ),
    "HR Officer": frozenset(
        f"{module}.{permission}"
        for module in ("teachers", "hr", "attendance", "reports", "documents")
        for permission in ("view", "create", "edit", "print", "export", "approve")
    ),
    "Exam Officer": frozenset(
        f"{module}.{permission}"
        for module in ("students", "academics", "exams", "results", "reports")
        for permission in ("view", "create", "edit", "print", "export", "approve")
    ),
    "Attendance Officer": frozenset(
        f"{module}.{permission}"
        for module in ("students", "teachers", "attendance", "reports")
        for permission in ("view", "create", "edit", "print", "export")
    ),
    "Parent": frozenset(f"{module}.view" for module in ("students", "attendance", "fees", "results", "academics", "communication", "events")),
    "Student": frozenset(f"{module}.view" for module in ("students", "attendance", "fees", "results", "academics", "communication", "events")),
    "Security/Guard": frozenset(f"{module}.{permission}" for module in ("students", "events") for permission in ("view", "create", "print")),
    "Transport Manager": frozenset(
        f"{module}.{permission}"
        for module in ("students", "transport", "fees", "reports")
        for permission in ("view", "create", "edit", "print", "export")
    ),
    "Store Manager": frozenset(
        f"{module}.{permission}"
        for module in ("inventory", "suppliers", "reports")
        for permission in ("view", "create", "edit", "delete", "print", "export", "approve")
    ),
    "Viewer": frozenset(f"{module}.view" for module in MODULES),
}


@dataclass(frozen=True)
class AuthorizationContext:
    user_id: int
    username: str
    role: str

    def can(self, module: str, action: str) -> bool:
        if self.role == "Super Admin":
            return True
        return f"{module}.{action}" in ROLE_PERMISSIONS.get(self.role, frozenset())

    def require(self, module: str, action: str) -> None:
        if not self.can(module, action):
            raise PermissionError(f"Permission denied: {self.role} cannot {action} {module}")


def context_for(user: User) -> AuthorizationContext:
    return AuthorizationContext(user_id=user.id, username=user.username, role=user.role)


def get_user_context(session: Session, user_id: int) -> AuthorizationContext | None:
    user = session.get(User, user_id)
    return context_for(user) if user else None


def permissions_for_role(role: str) -> frozenset[str]:
    return ROLE_PERMISSIONS.get(role, frozenset())


def has_permission(role: str, module: str, action: str) -> bool:
    return role == "Super Admin" or f"{module}.{action}" in ROLE_PERMISSIONS.get(role, frozenset())


def allowed_actions(role: str, module: str, actions: Iterable[str] = PERMISSIONS) -> tuple[str, ...]:
    return tuple(action for action in actions if has_permission(role, module, action))
