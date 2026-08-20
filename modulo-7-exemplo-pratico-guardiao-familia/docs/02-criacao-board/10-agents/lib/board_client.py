"""Cliente GitHub: issues, labels, comentários e Project V2 status.

Atualiza Status em paralelo:
1. `08-board/github-project-2-import.json` (fonte local dos agentes)
2. GitHub Project #2 via `gh` (`gh project item-edit` / `gh api graphql`)
"""

from __future__ import annotations

import json
import os
import subprocess
import urllib.request
from datetime import datetime, timezone

ORG = "guardiaofamilia"
PROJECT_NUMBER = 2
PROJECT_ID = "PVT_kwDOEDZbAM4Bg2rE"
GH = os.environ.get("GH_PATH", "gh")

from lib.local_board import update_local_status  # noqa: E402
from lib.task_status_workflow import (  # noqa: E402
    EVENT_TARGET,
    STATUSES,
    merge_owner_for_task,
    resolve_status,
)

# Retrocompat: aliases legados → novos status
LEGACY_STATUS_MAP = {
    "in_review": "In Code Review",
    "in-review": "In Code Review",
}


def _resolve_board_status(status: str) -> str:
    key = status.lower().replace(" ", "_")
    if key in LEGACY_STATUS_MAP:
        return LEGACY_STATUS_MAP[key]
    if status in EVENT_TARGET:
        return EVENT_TARGET[status]
    return resolve_status(status)


def _token() -> str | None:
    return (os.environ.get("CURSOR_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN") or "").strip() or None


def _gh_env() -> dict[str, str]:
    env = os.environ.copy()
    token = _token()
    if token:
        env.setdefault("GH_TOKEN", token)
        env.setdefault("GITHUB_TOKEN", token)
    return env


def _gh_run(*args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [GH, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=_gh_env(),
        check=check,
    )


def _gh_json(*args: str) -> dict | list:
    """Prefer `--format json` (projects); fallback `--json` quando aplicável."""
    r = _gh_run(*args, "--format", "json")
    if r.returncode != 0:
        raise RuntimeError(r.stderr or r.stdout or "gh failed")
    return json.loads(r.stdout) if (r.stdout or "").strip() else {}


def _graphql(query: str, variables: dict | None = None) -> dict:
    """GraphQL via `gh api graphql` (preferido) ou urllib com token."""
    payload = {"query": query, "variables": variables or {}}
    r = subprocess.run(
        [GH, "api", "graphql", "--input", "-"],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=_gh_env(),
    )
    if r.returncode == 0 and (r.stdout or "").strip():
        data = json.loads(r.stdout)
        if data.get("errors"):
            raise RuntimeError("; ".join(e["message"] for e in data["errors"]))
        return data.get("data") or {}

    token = _token()
    if not token:
        raise RuntimeError(
            "gh api graphql falhou e nao ha GITHUB_TOKEN/CURSOR_GITHUB_TOKEN. "
            f"stderr: {(r.stderr or r.stdout or '')[:400]}"
        )
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "gf-crew-board",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode())
    if data.get("errors"):
        raise RuntimeError("; ".join(e["message"] for e in data["errors"]))
    return data["data"]


def find_issue_number(repo: str, task_id: str, dry_run: bool = False) -> str | None:
    if dry_run:
        return "0"
    proc = _gh_run(
        "issue",
        "list",
        "--repo",
        f"{ORG}/{repo}",
        "--search",
        f"[{task_id}] in:title",
        "--json",
        "number",
        "--limit",
        "1",
    )
    if proc.returncode != 0:
        return None
    data = json.loads(proc.stdout or "[]")
    return str(data[0]["number"]) if data else None


def add_labels(repo: str, task_id: str, labels: list[str], dry_run: bool = False) -> dict:
    num = find_issue_number(repo, task_id, dry_run)
    if not num:
        return {"ok": False, "error": f"Issue nao encontrada: [{task_id}] em {repo}"}
    if dry_run:
        return {"ok": True, "dry_run": True, "issue": num, "labels": labels}
    for label in labels:
        _gh_run(
            "issue",
            "edit",
            num,
            "--repo",
            f"{ORG}/{repo}",
            "--add-label",
            label,
        )
    return {"ok": True, "issue": num, "labels": labels}


def comment_issue(repo: str, task_id: str, body: str, dry_run: bool = False) -> dict:
    num = find_issue_number(repo, task_id, dry_run)
    if not num:
        return {"ok": False, "error": f"Issue nao encontrada: [{task_id}]"}
    if dry_run:
        return {"ok": True, "dry_run": True, "issue": num, "body_preview": body[:200]}
    _gh_run(
        "issue",
        "comment",
        num,
        "--repo",
        f"{ORG}/{repo}",
        "--body",
        body,
        check=True,
    )
    return {"ok": True, "issue": num}


def _get_status_field(dry_run: bool = False) -> dict | None:
    if dry_run:
        return {"id": "dry", "options": [{"name": s, "id": s} for s in STATUSES]}
    fields = _gh_json("project", "field-list", str(PROJECT_NUMBER), "--owner", ORG)
    if isinstance(fields, dict):
        field_list = fields.get("fields", [])
    else:
        field_list = fields
    for f in field_list:
        if f.get("name") == "Status":
            return f
    return None


def _find_project_item_id(task_id: str, title: str) -> str | None:
    items: list[dict] = []
    cursor = None
    prefix = f"[{task_id}]"
    while True:
        args = ["project", "item-list", str(PROJECT_NUMBER), "--owner", ORG, "--limit", "100"]
        if cursor:
            args.extend(["--after", cursor])
        batch = _gh_json(*args)
        if isinstance(batch, dict):
            batch = batch.get("items", [])
        for item in batch:
            t = item.get("title") or ""
            if t.startswith(prefix) or t == title:
                return item["id"]
        items.extend(batch)
        if len(batch) < 100:
            break
        cursor = batch[-1].get("id")
    return None


def _update_github_status(task_id: str, title: str, gh_status: str) -> dict:
    """Atualiza Status no Project #2 via gh (item-edit) com fallback GraphQL."""
    item_id = _find_project_item_id(task_id, f"[{task_id}] {title}")
    if not item_id:
        return {"ok": False, "error": f"Item Project nao encontrado para {task_id}"}

    field = _get_status_field(False)
    if not field:
        return {"ok": False, "error": "Campo Status nao encontrado no Project"}

    option_id = None
    for opt in field.get("options", []):
        if opt["name"] == gh_status:
            option_id = opt["id"]
            break
    if not option_id:
        return {"ok": False, "error": f"Opcao Status '{gh_status}' nao encontrada"}

    # Preferencia: gh project item-edit
    edit = _gh_run(
        "project",
        "item-edit",
        "--id",
        item_id,
        "--project-id",
        PROJECT_ID,
        "--field-id",
        field["id"],
        "--single-select-option-id",
        option_id,
    )
    if edit.returncode == 0:
        return {
            "ok": True,
            "task_id": task_id,
            "status": gh_status,
            "item_id": item_id,
            "via": "gh project item-edit",
        }

    # Fallback: gh api graphql / token
    _graphql(
        """
        mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: ProjectV2FieldValue!) {
          updateProjectV2ItemFieldValue(input: {
            projectId: $projectId, itemId: $itemId, fieldId: $fieldId, value: $value
          }) { projectV2Item { id } }
        }
        """,
        {
            "projectId": PROJECT_ID,
            "itemId": item_id,
            "fieldId": field["id"],
            "value": {"singleSelectOptionId": option_id},
        },
    )
    return {
        "ok": True,
        "task_id": task_id,
        "status": gh_status,
        "item_id": item_id,
        "via": "gh api graphql",
        "item_edit_stderr": (edit.stderr or edit.stdout or "")[:300],
    }


def update_project_status(task_id: str, title: str, status: str, dry_run: bool = False) -> dict:
    """Atualiza Status no JSON local + GitHub Project #2 (gh)."""
    gh_status = _resolve_board_status(status)
    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "task_id": task_id,
            "status": gh_status,
            "local": {"ok": True, "dry_run": True},
            "github": {"ok": True, "dry_run": True},
        }

    local = update_local_status(task_id, gh_status)
    try:
        github = _update_github_status(task_id, title, gh_status)
    except Exception as exc:  # noqa: BLE001 — reportar falha remota sem desfazer local
        github = {"ok": False, "error": str(exc)}

    ok = bool(local.get("ok")) and bool(github.get("ok"))
    return {
        "ok": ok,
        "task_id": task_id,
        "status": gh_status,
        "local": local,
        "github": github,
    }


def claim_task(task: dict, agent: str, branch: str, dry_run: bool = False) -> dict:
    """Claim completo: labels, comentario, status In Progress."""
    ts = datetime.now(timezone.utc).isoformat()
    repo = task["repo"]
    task_id = task["id"]

    label_result = add_labels(
        repo, task_id,
        [f"agent:{agent}", "agent:in-progress"],
        dry_run=dry_run,
    )
    comment_result = comment_issue(
        repo, task_id,
        f"**CrewAI Orchestrator** — agent `{agent}` claimed `{task_id}` at {ts}\n\n"
        f"Branch: `{branch}`\n"
        f"Sprint: {task.get('sprint')} | Priority: #{task.get('priority_rank')}",
        dry_run=dry_run,
    )
    status_result = update_project_status(
        task_id, task["title"], "in_progress", dry_run=dry_run,
    )

    return {
        "task_id": task_id,
        "agent": agent,
        "branch": branch,
        "labels": label_result,
        "comment": comment_result,
        "board_status": status_result,
    }


def complete_task(task: dict, agent: str, pr_url: str = "", dry_run: bool = False) -> dict:
    """PR aberto → Ready for Code Review."""
    repo = task["repo"]
    task_id = task["id"]
    labels = add_labels(
        repo, task_id,
        ["agent:ready-for-review", "agent:in-review"],
        dry_run=dry_run,
    )
    body = f"**CrewAI** — PR aberto por `{agent}` → **Ready for Code Review**"
    if pr_url:
        body += f"\n\n{pr_url}"
    comment = comment_issue(repo, task_id, body, dry_run=dry_run)
    status = update_project_status(
        task_id, task["title"], "Ready for Code Review", dry_run=dry_run,
    )
    return {"task_id": task_id, "labels": labels, "comment": comment, "board_status": status}


def find_pr_for_task(repo: str, task_id: str, dry_run: bool = False) -> dict:
    """Busca PR aberto que referencia task_id no titulo ou branch."""
    if dry_run:
        return {"ok": True, "dry_run": True, "number": 0, "url": f"https://github.com/{ORG}/{repo}/pull/0"}
    proc = _gh_run(
        "pr",
        "list",
        "--repo",
        f"{ORG}/{repo}",
        "--search",
        f"{task_id} in:title",
        "--state",
        "open",
        "--json",
        "number,url,title,headRefName",
        "--limit",
        "1",
    )
    if proc.returncode != 0:
        return {"ok": False, "error": proc.stderr or "gh pr list failed"}
    data = json.loads(proc.stdout or "[]")
    if not data:
        proc2 = _gh_run(
            "pr",
            "list",
            "--repo",
            f"{ORG}/{repo}",
            "--search",
            f"head:{task_id.lower()}",
            "--state",
            "open",
            "--json",
            "number,url,title",
            "--limit",
            "1",
        )
        data = json.loads(proc2.stdout or "[]") if proc2.returncode == 0 else []
    if not data:
        return {"ok": False, "error": f"PR aberto nao encontrado para {task_id}"}
    pr = data[0]
    return {"ok": True, "number": pr["number"], "url": pr["url"], "title": pr.get("title")}


def comment_pr(repo: str, pr_number: int | str, body: str, dry_run: bool = False) -> dict:
    if dry_run:
        return {"ok": True, "dry_run": True, "pr": pr_number}
    _gh_run(
        "pr",
        "comment",
        str(pr_number),
        "--repo",
        f"{ORG}/{repo}",
        "--body",
        body,
        check=True,
    )
    return {"ok": True, "pr": pr_number}


def finalize_pr_review(
    task: dict,
    creator_role: str,
    reviewer_role: str,
    verdict: str,
    review_summary: str,
    pr_url: str = "",
    dry_run: bool = False,
) -> dict:
    """
    Finaliza ciclo de review: comenta PR/issue, atualiza labels e board.
    verdict: approved | changes_requested
    """
    repo = task["repo"]
    task_id = task["id"]
    ts = datetime.now(timezone.utc).isoformat()
    verdict = verdict.lower().replace(" ", "_")

    pr_info = find_pr_for_task(repo, task_id, dry_run=dry_run) if not pr_url else {
        "ok": True, "url": pr_url, "number": pr_url.rstrip("/").split("/")[-1],
    }

    if verdict == "approved":
        board_status = "Ready for Test"
        extra_labels = ["review:approved", "agent:ready-for-test"]
    else:
        board_status = "In Progress"
        extra_labels = ["review:changes-requested", "agent:in-progress"]

    label_result = add_labels(repo, task_id, extra_labels, dry_run=dry_run)

    issue_body = (
        f"**Review `{reviewer_role}`** — veredito `{verdict}` at {ts}\n\n"
        f"Criador: `{creator_role}`\n\n"
        f"{review_summary[:4000]}"
    )
    if pr_info.get("ok") and pr_info.get("url"):
        issue_body += f"\n\nPR: {pr_info['url']}"
    issue_comment = comment_issue(repo, task_id, issue_body, dry_run=dry_run)

    pr_comment = None
    if pr_info.get("ok") and pr_info.get("number") is not None:
        pr_body = (
            f"## Review by `{reviewer_role}`\n\n"
            f"**Veredito:** `{verdict}`\n\n{review_summary}"
        )
        pr_comment = comment_pr(repo, pr_info["number"], pr_body, dry_run=dry_run)

    status_result = update_project_status(
        task_id, task["title"], board_status, dry_run=dry_run,
    )

    return {
        "task_id": task_id,
        "creator_role": creator_role,
        "reviewer_role": reviewer_role,
        "verdict": verdict,
        "board_status": board_status,
        "pr": pr_info,
        "labels": label_result,
        "issue_comment": issue_comment,
        "pr_comment": pr_comment,
        "board": status_result,
    }


def _apply_status_with_labels(
    task: dict,
    status: str,
    labels: list[str],
    comment: str,
    dry_run: bool = False,
) -> dict:
    repo = task["repo"]
    task_id = task["id"]
    label_result = add_labels(repo, task_id, labels, dry_run=dry_run) if labels else {"ok": True}
    comment_result = comment_issue(repo, task_id, comment, dry_run=dry_run) if comment else {"ok": True}
    status_result = update_project_status(task_id, task["title"], status, dry_run=dry_run)
    return {
        "task_id": task_id,
        "status": _resolve_board_status(status),
        "labels": label_result,
        "comment": comment_result,
        "board": status_result,
    }


def start_code_review(task: dict, reviewer_role: str, dry_run: bool = False) -> dict:
    """Revisor assume → In Code Review."""
    return _apply_status_with_labels(
        task, "In Code Review",
        [f"agent:{reviewer_role}", "agent:in-review"],
        f"**{reviewer_role}** iniciou code review → **In Code Review**",
        dry_run,
    )


def resubmit_after_changes(task: dict, creator_role: str, pr_url: str = "", dry_run: bool = False) -> dict:
    """Correcao CR → In Code Review (re-review)."""
    body = f"**{creator_role}** — correcoes CR aplicadas → **In Code Review**"
    if pr_url:
        body += f"\n\n{pr_url}"
    return _apply_status_with_labels(
        task, "In Code Review",
        ["agent:in-review", f"agent:{creator_role}"],
        body,
        dry_run,
    )


def start_qa(task: dict, dry_run: bool = False) -> dict:
    """QA inicia testes → In Test."""
    return _apply_status_with_labels(
        task, "In Test",
        ["agent:qa", "agent:in-test"],
        "**agent-qa** iniciou testes → **In Test**",
        dry_run,
    )


def complete_qa_pass(task: dict, summary: str = "", dry_run: bool = False) -> dict:
    """Testes OK → In Pull Request."""
    track = task.get("track", "produto")
    merge_agent = merge_owner_for_task(track)
    body = f"**agent-qa** testes aprovados → **In Pull Request** (@{merge_agent})"
    if summary:
        body += f"\n\n{summary[:2000]}"
    return _apply_status_with_labels(
        task, "In Pull Request",
        ["agent:in-pr", f"agent:{merge_agent}"],
        body,
        dry_run,
    )


def report_qa_bug(task: dict, summary: str, dry_run: bool = False) -> dict:
    """Bug em QA → In Progress (creator corrige)."""
    creator = task.get("agent_role", "backend")
    body = f"**agent-qa** bug/regressao → **In Progress** (@{creator})\n\n{summary[:2000]}"
    return _apply_status_with_labels(
        task, "In Progress",
        ["type:bug", "agent:in-progress", f"agent:{creator}"],
        body,
        dry_run,
    )


def complete_merge(task: dict, agent: str = "devops-cicd", dry_run: bool = False) -> dict:
    """Merge concluido → Done."""
    return _apply_status_with_labels(
        task, "Done",
        ["agent:done", "review:approved"],
        f"**{agent}** merge concluido → **Done**",
        dry_run,
    )
