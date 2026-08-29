"""Labels agent:* sincronizadas com Status (issues reais apos conversao)."""

from __future__ import annotations

STATUS_LABELS: dict[str, str] = {
    "Todo": "agent:todo",
    "In Progress": "agent:in-progress",
    "Ready for Code Review": "agent:ready-for-code-review",
    "In Code Review": "agent:in-code-review",
    "Ready for Test": "agent:ready-for-test",
    "In Test": "agent:in-test",
    "In Pull Request": "agent:in-pull-request",
    "Done": "agent:done",
}

ALL_AGENT_STATUS_LABELS = frozenset(STATUS_LABELS.values())


def labels_for_status(status: str, role: str | None = None) -> list[str]:
    labels = []
    if status in STATUS_LABELS:
        labels.append(STATUS_LABELS[status])
    if role:
        labels.append(f"agent:{role}")
    return labels


def labels_to_remove_for_transition(new_status: str) -> list[str]:
    keep = STATUS_LABELS.get(new_status)
    return [lb for lb in ALL_AGENT_STATUS_LABELS if lb != keep]
