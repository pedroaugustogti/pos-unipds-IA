"""CrewAI tools para revisao de codigo e finalizacao de PR."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_LIB = Path(__file__).resolve().parents[2]
if str(_LIB) not in sys.path:
    sys.path.insert(0, str(_LIB))

from lib.board_client import finalize_pr_review, find_pr_for_task  # noqa: E402
from lib.reviewer_pairs import CREATOR_ROLES, CREATOR_TO_REVIEWER, reviewer_for  # noqa: E402
from lib.task_router import load_tasks  # noqa: E402

_DRY_RUN = False
REVIEW_TEMPLATE = _LIB / "templates" / "REVIEW_TEMPLATE.md"


def set_dry_run(value: bool) -> None:
    global _DRY_RUN
    _DRY_RUN = value


try:
    from crewai.tools import tool
except ImportError:
    def tool(name: str):  # type: ignore[misc]
        def deco(fn):
            fn.name = name  # type: ignore[attr-defined]
            return fn
        return deco


@tool("Listar PRs aguardando review")
def list_prs_pending_review(creator_role: str = "") -> str:
    """Lista tasks com agent:in-review. Filtro opcional por creator_role."""
    pending = []
    for t in load_tasks():
        if t["status_baseline"] == "done":
            continue
        role = t["agent_role"]
        if creator_role and role != creator_role:
            continue
        pending.append({
            "task_id": t["id"],
            "title": t["title"],
            "creator_role": role,
            "reviewer_role": reviewer_for(role),
            "repo": t["repo"],
            "priority_rank": t["priority_rank"],
        })
    pending.sort(key=lambda x: int(x["priority_rank"]))
    return json.dumps(pending[:20], ensure_ascii=False, indent=2)


@tool("Buscar PR da task")
def get_pr_for_task(task_id: str) -> str:
    """Retorna PR aberto associado a task_id."""
    tasks = load_tasks()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return json.dumps({"ok": False, "error": f"Task {task_id} nao encontrada"})
    result = find_pr_for_task(task["repo"], task_id, dry_run=_DRY_RUN)
    return json.dumps({**result, "task": task}, ensure_ascii=False)


@tool("Finalizar review e atualizar board")
def finalize_review_on_board(
    task_id: str,
    creator_role: str,
    verdict: str,
    review_summary: str,
    pr_url: str = "",
) -> str:
    """
    Finaliza review: comenta PR/issue, labels review:*, Status Done ou In Progress.
    verdict: approved | changes_requested
    """
    tasks = load_tasks()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return json.dumps({"ok": False, "error": f"Task {task_id} nao encontrada"})
    reviewer_role = CREATOR_TO_REVIEWER.get(creator_role, reviewer_for(creator_role))
    result = finalize_pr_review(
        task, creator_role, reviewer_role, verdict, review_summary,
        pr_url=pr_url, dry_run=_DRY_RUN,
    )
    return json.dumps(result, ensure_ascii=False, indent=2)


@tool("Template de review")
def get_review_template(task_id: str, creator_role: str, verdict: str = "approved") -> str:
    """Retorna REVIEW_TEMPLATE.md preenchido parcialmente."""
    if not REVIEW_TEMPLATE.exists():
        return json.dumps({"error": "template nao encontrado"})
    tpl = REVIEW_TEMPLATE.read_text(encoding="utf-8")
    reviewer_role = CREATOR_TO_REVIEWER.get(creator_role, reviewer_for(creator_role))
    board_status = "Ready for Test" if verdict == "approved" else "In Progress"
    for k, v in {
        "{task_id}": task_id,
        "{creator_role}": creator_role,
        "{reviewer_role}": reviewer_role,
        "{verdict}": verdict,
        "{review_date}": "AUTO",
        "{board_status}": board_status,
    }.items():
        tpl = tpl.replace(k, v)
    return tpl


@tool("Review em lote por criador")
def batch_finalize_reviews(creator_role: str, verdict: str, summary: str) -> str:
    """Finaliza review de todas tasks in-review do creator_role (dry-run safe)."""
    tasks = [t for t in load_tasks() if t["agent_role"] == creator_role][:3]
    results = []
    for task in tasks:
        r = finalize_pr_review(
            task, creator_role, reviewer_for(creator_role),
            verdict, summary, dry_run=_DRY_RUN,
        )
        results.append(r)
    return json.dumps(results, ensure_ascii=False, indent=2)


REVIEW_TOOLS = [
    list_prs_pending_review,
    get_pr_for_task,
    finalize_review_on_board,
    get_review_template,
    batch_finalize_reviews,
]
