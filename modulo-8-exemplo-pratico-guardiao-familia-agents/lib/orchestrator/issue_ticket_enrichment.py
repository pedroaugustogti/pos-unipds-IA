"""Enriquece task do board com refinement/QA do JSON local e corpo da issue GitHub."""

from __future__ import annotations

import json
import re
from typing import Any

from board_automation.board.board_client import ORG, _gh_json
from board_automation.board.board_task_loader import get_board_task_from_json
from board_automation.board.issue_task_body import build_agent_payload

AGENT_TASK_RE = re.compile(r"```agent-task\s*\n(.*?)\n```", re.DOTALL | re.IGNORECASE)


def parse_agent_task_block(body: str) -> dict[str, Any]:
    match = AGENT_TASK_RE.search(body or "")
    if not match:
        return {}
    try:
        data = json.loads(match.group(1))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def fetch_issue_body(repo: str, issue_number: str) -> str:
    num = str(issue_number or "").strip()
    if not num or not repo:
        return ""
    try:
        payload = _gh_json(
            "issue", "view", num,
            "--repo", f"{ORG}/{repo}",
            "--json", "body",
        )
        if isinstance(payload, dict):
            return str(payload.get("body") or "")
    except Exception:  # noqa: BLE001
        pass
    return ""


def _deep_merge_dict(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, val in extra.items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge_dict(out[key], val)
        elif val not in (None, "", [], {}):
            out[key] = val
    return out


def enrich_task_ticket(task: dict[str, Any]) -> dict[str, Any]:
    """Mescla board JSON local + payload agent-task da issue GitHub."""
    tid = str(task.get("id") or "")
    enriched = dict(task)

    local = get_board_task_from_json(tid) if tid else None
    if local:
        for key in ("refinement", "qa", "agent_responsibilities", "handoff_expectations", "epic_id", "depends_on"):
            if local.get(key):
                if key in ("refinement", "qa") and isinstance(local.get(key), dict):
                    enriched[key] = _deep_merge_dict(enriched.get(key) or {}, local[key])
                else:
                    enriched.setdefault(key, local.get(key))
                    if key == "epic_id" and not enriched.get("epic_id"):
                        enriched["epic_id"] = local.get("epic_id")

    repo = str(enriched.get("repo") or "")
    issue_number = str(enriched.get("issue_number") or "")
    if repo and issue_number:
        body = fetch_issue_body(repo, issue_number)
        payload = parse_agent_task_block(body)
        if payload:
            if payload.get("refinement"):
                enriched["refinement"] = _deep_merge_dict(
                    enriched.get("refinement") or {},
                    payload["refinement"],
                )
            if payload.get("qa"):
                enriched["qa"] = _deep_merge_dict(enriched.get("qa") or {}, payload["qa"])
            if payload.get("agent_responsibilities"):
                enriched["agent_responsibilities"] = _deep_merge_dict(
                    enriched.get("agent_responsibilities") or {},
                    payload["agent_responsibilities"],
                )
            for key in ("epic_id", "depends_on", "branch", "base_branch", "repo_path", "title"):
                if payload.get(key) and not enriched.get(key):
                    enriched[key] = payload[key]
            enriched["issue_body_parsed"] = True

    if not enriched.get("repo_path"):
        payload = build_agent_payload(enriched)
        enriched["repo_path"] = payload.get("repo_path")
    return enriched
