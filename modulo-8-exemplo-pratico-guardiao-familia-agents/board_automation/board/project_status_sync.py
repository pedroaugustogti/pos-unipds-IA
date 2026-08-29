"""Sincroniza campo Status do GitHub Project #2 com o workflow LangGraph."""

from __future__ import annotations

from typing import Any

from board_automation.board.board_client import ORG, PROJECT_NUMBER, _get_status_field, _graphql
from board_automation.board.status_labels import STATUS_LABELS
from board_automation.board.task_status_workflow import AGENT_STAGES, STATUSES

# Cores GitHub Project V2 (SingleSelectFieldOptionInput)
STATUS_COLORS: dict[str, str] = {
    "Todo": "GRAY",
    "In Progress": "BLUE",
    "Ready for Code Review": "YELLOW",
    "In Code Review": "ORANGE",
    "Ready for Test": "PINK",
    "In Test": "PURPLE",
    "In Pull Request": "RED",
    "Done": "GREEN",
}

# Labels agent:* — hex para `gh label create`
LABEL_COLORS: dict[str, str] = {
    "agent:todo": "ededed",
    "agent:in-progress": "fbca04",
    "agent:ready-for-code-review": "d4c5f9",
    "agent:in-code-review": "7057ff",
    "agent:ready-for-test": "0e8a16",
    "agent:in-test": "5319e7",
    "agent:in-pull-request": "1d76db",
    "agent:done": "0e8a16",
}

TARGET_REPOS: tuple[str, ...] = (
    "guardiao-familia-api",
    "guardiao-familia-parent",
    "guardiao-familia-child",
    "guardiao-familia-backoffice",
    "guardiao-familia-site",
)


def _stage_by_status() -> dict[str, dict[str, str]]:
    return {s["status"]: s for s in AGENT_STAGES}


def status_option_description(status: str) -> str:
    """Hint curto — GitHub Projects exibe description no header da coluna Kanban."""
    stage = _stage_by_status().get(status, {})
    owner = stage.get("owner") or "-"
    event_out = (stage.get("event_out") or "-").split("/")[0].strip()
    if event_out in ("", "-"):
        return owner
    return f"{owner} · {event_out}"


def status_label_hint(status: str) -> str:
    """Hint para labels agent:* (max 100 chars no GitHub)."""
    stage = _stage_by_status().get(status, {})
    label = STATUS_LABELS.get(status) or stage.get("label") or ""
    owner = stage.get("owner") or "-"
    event_in = stage.get("event_in") or "-"
    event_out = stage.get("event_out") or "-"
    text = f"{status}: {owner} | {label} | in:{event_in} | out:{event_out}"
    return text[:100]


def build_status_options(existing: dict[str, str]) -> list[dict[str, Any]]:
    """Monta payload GraphQL preservando IDs das opções já existentes."""
    options: list[dict[str, Any]] = []
    for name in STATUSES:
        entry: dict[str, Any] = {
            "name": name,
            "color": STATUS_COLORS.get(name, "GRAY"),
            "description": status_option_description(name),
        }
        if name in existing:
            entry["id"] = existing[name]
        options.append(entry)
    return options


def sync_project_status_field(*, dry_run: bool = False) -> dict[str, Any]:
    """Adiciona/atualiza opções Status no Project #2 conforme STATUSES."""
    field = _get_status_field(dry_run=False)
    if not field:
        return {"ok": False, "error": "Campo Status nao encontrado no Project"}

    existing = {o["name"]: o["id"] for o in field.get("options", [])}
    missing = [s for s in STATUSES if s not in existing]
    report = {
        "ok": True,
        "field_id": field["id"],
        "existing": sorted(existing.keys()),
        "missing": missing,
        "target": list(STATUSES),
        "dry_run": dry_run,
    }

    if dry_run or not field.get("id"):
        return report

    options = build_status_options(existing)
    data = _graphql(
        """
        mutation($fieldId: ID!, $options: [ProjectV2SingleSelectFieldOptionInput!]!) {
          updateProjectV2Field(input: { fieldId: $fieldId, singleSelectOptions: $options }) {
            projectV2Field {
              ... on ProjectV2SingleSelectField {
                id name
                options { id name description color }
              }
            }
          }
        }
        """,
        {"fieldId": field["id"], "options": options},
    )
    updated = (
        (data.get("updateProjectV2Field") or {})
        .get("projectV2Field", {})
        .get("options", [])
    )
    report["synced"] = [o["name"] for o in updated]
    report["missing"] = [s for s in STATUSES if s not in report["synced"]]
    return report


def ensure_status_labels(*, dry_run: bool = False) -> dict[str, Any]:
    """Garante labels agent:* nos repos alvo (marcações de orquestração)."""
    from board_automation.board.board_client import _gh_run

    created: list[str] = []
    updated: list[str] = []
    skipped: list[str] = []
    errors: list[str] = []

    for repo in TARGET_REPOS:
        full = f"{ORG}/{repo}"
        listed = _gh_run(
            "label", "list", "--repo", full, "--json", "name", "--limit", "200",
        )
        existing: set[str] = set()
        if listed.returncode == 0 and (listed.stdout or "").strip():
            import json

            existing = {row["name"] for row in json.loads(listed.stdout)}

        for status, label in STATUS_LABELS.items():
            key = f"{full}:{label}"
            hint = status_label_hint(status)
            if label in existing:
                if dry_run:
                    updated.append(f"{key} (dry_run)")
                    continue
                edit = _gh_run(
                    "label", "edit", label,
                    "--repo", full,
                    "--description", hint,
                )
                if edit.returncode == 0:
                    updated.append(key)
                else:
                    errors.append(f"{key}: {(edit.stderr or edit.stdout or '')[:200]}")
                continue
            if dry_run:
                created.append(f"{key} (dry_run)")
                continue
            color = LABEL_COLORS.get(label, "ededed")
            proc = _gh_run(
                "label", "create", label,
                "--repo", full,
                "--color", color,
                "--description", hint,
            )
            if proc.returncode == 0:
                created.append(key)
            else:
                errors.append(f"{key}: {(proc.stderr or proc.stdout or '')[:200]}")

    return {
        "ok": not errors,
        "created": created,
        "updated": updated,
        "skipped": len(skipped),
        "errors": errors,
        "dry_run": dry_run,
    }
