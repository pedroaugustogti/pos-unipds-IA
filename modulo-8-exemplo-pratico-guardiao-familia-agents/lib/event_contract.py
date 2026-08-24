"""Contrato único de evento de Status (gateway do board)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

EventName = Literal[
    "claim",
    "start_work",
    "open_pr",
    "start_review",
    "request_changes",
    "resubmit_review",
    "approve_review",
    "propose_review",  # LLM propõe; humano confirma em risco alto
    "start_test",
    "test_failed_bug",
    "test_passed",
    "merge_pr",
    "reopen",
    "hitl_required",
    "hitl_approved",
    "hitl_rejected",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class EventPayload:
    """Payload fechado que atravessa orchestrator → worker → board."""

    task_id: str
    event: str
    from_status: str | None = None
    to_status: str | None = None
    agent_role: str | None = None
    next_agent: str | None = None
    repo: str | None = None
    branch: str | None = None
    pr_url: str | None = None
    summary: str = ""
    doubts: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    bug_kind: str | None = None  # regression | flaky | unknown
    correlation_id: str = field(default_factory=lambda: str(uuid4()))
    idempotency_key: str | None = None
    at: str = field(default_factory=_now)
    dry_run: bool = False

    def key(self) -> str:
        if self.idempotency_key:
            return self.idempotency_key
        return f"{self.task_id}:{self.event}:{self.from_status}:{self.to_status}"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EventPayload":
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        return cls(**{k: v for k, v in data.items() if k in known})
