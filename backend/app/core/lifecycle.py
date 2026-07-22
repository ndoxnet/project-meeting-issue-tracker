# Concept by MrHan (08974747477)
"""Issue lifecycle state machine (ADR-012).

Central definition of allowed status transitions. CLOSED -> REOPENED happens only
through the dedicated reopen endpoint; the generic status endpoint uses the
transitions declared here.
"""

from __future__ import annotations

from app.models.enums import IssueStatus

# Allowed transitions for the generic status-change endpoint.
ALLOWED_TRANSITIONS: dict[IssueStatus, set[IssueStatus]] = {
    IssueStatus.OPEN: {IssueStatus.IN_PROGRESS, IssueStatus.PENDING, IssueStatus.CLOSED},
    IssueStatus.IN_PROGRESS: {
        IssueStatus.PENDING,
        IssueStatus.CLOSED,
        IssueStatus.OPEN,
    },
    IssueStatus.PENDING: {
        IssueStatus.IN_PROGRESS,
        IssueStatus.OPEN,
        IssueStatus.CLOSED,
    },
    # CLOSED -> REOPENED only via the reopen endpoint (not the generic status one).
    IssueStatus.CLOSED: set(),
    IssueStatus.REOPENED: {
        IssueStatus.IN_PROGRESS,
        IssueStatus.PENDING,
        IssueStatus.CLOSED,
    },
}


def can_transition(current: IssueStatus, target: IssueStatus) -> bool:
    return target in ALLOWED_TRANSITIONS.get(current, set())
