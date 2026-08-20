"""CrewAI tools para board e roteamento de tasks."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# lib/ no path
_LIB = Path(__file__).resolve().parents[2]
if str(_LIB) not in sys.path:
    sys.path.insert(0, str(_LIB))

from lib.board_client import (  # noqa: E402
    claim_task,
    complete_task,
    complete_merge,
    complete_qa_pass,
    report_qa_bug,
    resubmit_after_changes,
    start_code_review as board_start_review,
    start_qa,
    update_project_status,
    comment_issue,
    add_labels,
)
from lib.task_router import (  # noqa: E402
    AGENT_ROLES,
    load_tasks,
    pick_task,
    pick_tasks_for_sprint,
    slugify,
)

_DRY_RUN = False


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


@tool("Listar backlog por agente")
def list_backlog_by_agent(sprint: int = 1) -> str:
    """Lista tasks elegiveis (board_status claimavel) agrupadas por agent_role."""
    tasks = load_tasks()
    by_role: dict[str, list] = {r: [] for r in AGENT_ROLES}
    for t in tasks:
        if t.get("board_status") == "Done":
            continue
        if int(t["sprint"]) != sprint:
            continue
        role = t["agent_role"]
        if role in by_role:
            by_role[role].append({
                "id": t["id"],
                "title": t["title"],
                "rank": t["priority_rank"],
                "repo": t["repo"],
                "sp": t["effort_sp"],
                "board_status": t.get("board_status"),
            })
    for role in by_role:
        by_role[role].sort(key=lambda x: int(x["rank"]))
        by_role[role] = by_role[role][:5]
    return json.dumps(by_role, ensure_ascii=False, indent=2)


@tool("Selecionar proxima task")
def select_next_task(agent_role: str, sprint: int = 1) -> str:
    """Seleciona a melhor task para um agent_role no sprint. Retorna JSON da task."""
    task = pick_task(agent_role, sprint)
    if not task:
        return json.dumps({"error": f"Nenhuma task para {agent_role} no sprint {sprint}"})
    branch = f"feat/{task['id']}-{slugify(task['title'])}"
    return json.dumps({**task, "suggested_branch": branch}, ensure_ascii=False)


@tool("Claim task no board")
def claim_task_on_board(task_id: str, agent_role: str, sprint: int = 1) -> str:
    """Claim: labels agent:*, comentario na issue, Status In Progress no Project #2."""
    tasks = load_tasks()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return json.dumps({"ok": False, "error": f"Task {task_id} nao encontrada"})
    branch = f"feat/{task_id}-{slugify(task['title'])}"
    result = claim_task(task, agent_role, branch, dry_run=_DRY_RUN)
    return json.dumps(result, ensure_ascii=False, indent=2)


@tool("Atualizar status do board")
def update_board_status(task_id: str, title: str, status: str) -> str:
    """Atualiza Status no JSON local (github-project-2-import.json) e no Project #2 via gh."""
    result = update_project_status(task_id, title, status, dry_run=_DRY_RUN)
    return json.dumps(result, ensure_ascii=False)


@tool("Aplicar evento de workflow")
def apply_workflow_event(task_id: str, title: str, event: str, kind: str = "feature") -> str:
    """Eventos: claim, open_pr, start_review, request_changes, resubmit_review, approve_review, start_test, test_failed_bug, test_passed, merge_pr.

    Orquestra: board (JSON+gh) + notificacao idle/dispatch/blocker (3 bugs).
    """
    from lib.event_orchestrator import emit_board_event
    from lib.task_status_workflow import EVENT_TARGET

    if event not in EVENT_TARGET:
        return json.dumps({"ok": False, "error": f"Evento invalido: {event}"})
    result = emit_board_event(
        task_id, event, title=title, dry_run=_DRY_RUN, apply_board=True,
    )
    result["kind"] = kind
    return json.dumps(result, ensure_ascii=False, indent=2)


@tool("Iniciar code review")
def start_code_review(task_id: str, reviewer_role: str) -> str:
    """Revisor assume task → In Code Review (evento start_review)."""
    tasks = load_tasks()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return json.dumps({"ok": False, "error": f"Task {task_id} nao encontrada"})
    result = board_start_review(task, reviewer_role, dry_run=_DRY_RUN)
    return json.dumps(result, ensure_ascii=False)


@tool("Reenviar apos correcao CR")
def resubmit_after_review(task_id: str, agent_role: str, pr_url: str = "") -> str:
    """Creator corrigiu CR → In Code Review (evento resubmit_review)."""
    tasks = load_tasks()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return json.dumps({"ok": False, "error": f"Task {task_id} nao encontrada"})
    result = resubmit_after_changes(task, agent_role, pr_url, dry_run=_DRY_RUN)
    return json.dumps(result, ensure_ascii=False)


@tool("QA inicia testes")
def start_qa_on_board(task_id: str) -> str:
    """Ready for Test → In Test (evento start_test)."""
    tasks = load_tasks()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return json.dumps({"ok": False, "error": f"Task {task_id} nao encontrada"})
    result = start_qa(task, dry_run=_DRY_RUN)
    return json.dumps(result, ensure_ascii=False)


@tool("QA aprova testes")
def complete_qa_pass_on_board(task_id: str, summary: str = "") -> str:
    """In Test → In Pull Request (evento test_passed)."""
    tasks = load_tasks()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return json.dumps({"ok": False, "error": f"Task {task_id} nao encontrada"})
    result = complete_qa_pass(task, summary, dry_run=_DRY_RUN)
    return json.dumps(result, ensure_ascii=False)


@tool("QA reporta bug")
def report_qa_bug_on_board(task_id: str, summary: str) -> str:
    """In Test → In Progress + type:bug. Conta bugs; no 3o marca blocker + skill impactada."""
    from lib.event_orchestrator import notify_status_change

    tasks = load_tasks()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return json.dumps({"ok": False, "error": f"Task {task_id} nao encontrada"})
    board_side = report_qa_bug(task, summary, dry_run=_DRY_RUN)
    orch = notify_status_change(
        task_id,
        "test_failed_bug",
        from_status="In Test",
        to_status="In Progress",
        summary=summary,
        dry_run=_DRY_RUN,
    )
    return json.dumps({"board": board_side, "orchestration": orch}, ensure_ascii=False, indent=2)


@tool("Concluir merge")
def complete_merge_on_board(task_id: str, agent_role: str = "devops-cicd") -> str:
    """In Pull Request → Done (evento merge_pr)."""
    tasks = load_tasks()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return json.dumps({"ok": False, "error": f"Task {task_id} nao encontrada"})
    result = complete_merge(task, agent_role, dry_run=_DRY_RUN)
    return json.dumps(result, ensure_ascii=False)


@tool("Etapas do workflow por agente")
def workflow_stages_for_agent(agent_role: str) -> str:
    """Retorna JSON com status onde o agente entra/sai."""
    from lib.task_status_workflow import stages_for_role, mermaid_agent_swimlane

    return json.dumps({
        "agent_role": agent_role,
        "stages": stages_for_role(agent_role),
        "diagram": mermaid_agent_swimlane(),
    }, ensure_ascii=False, indent=2)


@tool("Planejar sprint completo")
def plan_sprint_assignments(sprint: int = 1, limit_per_agent: int = 1) -> str:
    """Planeja assignments: 1 task por agent_role, ordenado por priority_rank."""
    assignments = pick_tasks_for_sprint(sprint, limit_per_agent)
    for a in assignments:
        a["suggested_branch"] = f"feat/{a['id']}-{slugify(a['title'])}"
    return json.dumps(assignments, ensure_ascii=False, indent=2)


@tool("Executar claim em lote")
def batch_claim_sprint(sprint: int = 1, limit_per_agent: int = 1) -> str:
    """Claim automatico de todas as tasks planejadas para o sprint no board."""
    assignments = pick_tasks_for_sprint(sprint, limit_per_agent)
    results = []
    for task in assignments:
        agent = task["assigned_agent"]
        branch = f"feat/{task['id']}-{slugify(task['title'])}"
        r = claim_task(task, agent, branch, dry_run=_DRY_RUN)
        results.append(r)
    return json.dumps(results, ensure_ascii=False, indent=2)


@tool("Marcar task em review")
def mark_task_in_review(task_id: str, agent_role: str, pr_url: str = "") -> str:
    """PR aberto → Ready for Code Review (evento open_pr)."""
    tasks = load_tasks()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return json.dumps({"ok": False, "error": f"Task {task_id} nao encontrada"})
    result = complete_task(task, agent_role, pr_url, dry_run=_DRY_RUN)
    return json.dumps(result, ensure_ascii=False, indent=2)


BOARD_TOOLS = [
    list_backlog_by_agent,
    select_next_task,
    claim_task_on_board,
    update_board_status,
    apply_workflow_event,
    workflow_stages_for_agent,
    start_code_review,
    resubmit_after_review,
    start_qa_on_board,
    complete_qa_pass_on_board,
    report_qa_bug_on_board,
    complete_merge_on_board,
    plan_sprint_assignments,
    batch_claim_sprint,
    mark_task_in_review,
]
