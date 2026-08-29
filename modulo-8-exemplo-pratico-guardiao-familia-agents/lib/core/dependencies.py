"""E1 — depends_on entre tasks do mapa."""

from __future__ import annotations

from typing import Any


def parse_depends_on(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [p.strip() for p in str(raw).replace(";", ",").split(",") if p.strip()]


def dependencies_satisfied(
    task: dict[str, Any],
    by_id: dict[str, dict[str, Any]],
    *,
    allow_after_pr: bool = False,
) -> tuple[bool, list[str]]:
    """Retorna (ok, missing_ids). Done sempre libera; In Pull Request se allow_after_pr."""
    deps = parse_depends_on(task.get("depends_on"))
    missing: list[str] = []
    ok_statuses = {"Done"}
    if allow_after_pr:
        ok_statuses.add("In Pull Request")
    for dep in deps:
        other = by_id.get(dep)
        if not other:
            missing.append(dep)
            continue
        st = other.get("board_status") or other.get("status_baseline") or "Todo"
        if st not in ok_statuses:
            missing.append(dep)
    return (len(missing) == 0, missing)
