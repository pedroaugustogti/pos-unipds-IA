#!/usr/bin/env python3
"""CrewAI — orquestrador hierarquico da equipe Guardiao Familia + board GitHub."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CREW_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(CREW_DIR))

from crewai import Agent, Crew, Process, Task  # noqa: E402

from tools.board_tools import BOARD_TOOLS, set_dry_run  # noqa: E402
from tools.review_tools import REVIEW_TOOLS, set_dry_run as set_review_dry_run  # noqa: E402
from tools.event_tools import EVENT_TOOLS, set_dry_run as set_event_dry_run  # noqa: E402
from lib.reviewer_pairs import CREATOR_ROLES, reviewer_for  # noqa: E402

SKILLS = ROOT / "skills"


def _load_skill(role: str) -> str:
    path = SKILLS / role / "SKILL.md"
    if not path.exists():
        path = SKILLS / f"{role}-reviewer" / "SKILL.md"
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            end = text.find("---", 3)
            if end > 0:
                text = text[end + 3 :].strip()
        return text[:3000]
    return f"Especialista {role} do Guardiao Familia."


def _llm():
    model = os.environ.get("CREWAI_MODEL", "gpt-4o-mini")
    return model


def build_crew(sprint: int = 1, dry_run: bool = False) -> Crew:
    set_dry_run(dry_run)
    set_review_dry_run(dry_run)
    set_event_dry_run(dry_run)

    orch_tools = BOARD_TOOLS + EVENT_TOOLS

    orchestrator = Agent(
        role="Engineering Manager / Scrum Orchestrator",
        goal=(
            f"Planejar sprint {sprint}, orquestrar mudancas de Status como EVENTOS, "
            "despachar agentes ociosos e bloquear tasks com 3 bugs recorrentes."
        ),
        backstory=(
            "Voce coordena 8 criadores + 8 revisores + QA + DevOps. "
            "Toda mudanca de board e um evento (claim, open_pr, test_failed_bug, ...). "
            "Ao notificar status: list_idle_crew_agents → resolve_agent_for_board_event → "
            "emit_status_event. No 3o bug da mesma task: blocker + skill impactada."
        ),
        tools=orch_tools,
        verbose=True,
        allow_delegation=True,
        llm=_llm(),
    )

    specialists = {}
    reviewers = {}
    for role in CREATOR_ROLES:
        specialists[role] = Agent(
            role=f"Creator {role}",
            goal=f"Implementar tasks {role} e abrir PR estrategico.",
            backstory=_load_skill(role),
            tools=[BOARD_TOOLS[1], BOARD_TOOLS[2], BOARD_TOOLS[12], BOARD_TOOLS[13]],
            verbose=True,
            allow_delegation=False,
            llm=_llm(),
        )
        rev = reviewer_for(role)
        reviewers[role] = Agent(
            role=f"Reviewer {rev}",
            goal=f"Revisar PRs do {role}, finalizar review e atualizar board.",
            backstory=_load_skill(rev),
            tools=REVIEW_TOOLS,
            verbose=True,
            allow_delegation=False,
            llm=_llm(),
        )

    plan_task = Task(
        description=(
            f"Para o sprint {sprint}: "
            "1) Use plan_sprint_assignments para obter 1 task por agent_role. "
            "2) Analise conflitos de repo e release_blocker. "
            "3) Produza tabela markdown: task_id | agent | repo | priority | branch sugerida."
        ),
        expected_output="Tabela markdown de assignments do sprint com justificativa de roteamento.",
        agent=orchestrator,
    )

    board_task = Task(
        description=(
            f"Para cada assignment do sprint {sprint}: "
            "1) list_idle_crew_agents "
            "2) resolve_agent_for_board_event(task_id, 'claim') "
            "3) Se agente ocioso: emit_status_event(task_id, 'claim') "
            "   (grava Status In Progress no JSON+gh e despacha o creator). "
            "4) Se ocupado: reporte fila. Nao claim duplicado."
        ),
        expected_output=(
            "Tabela: task_id | event | next_agent | idle? | dispatch | board ok."
        ),
        agent=orchestrator,
        context=[plan_task],
    )

    report_task = Task(
        description=(
            "Consolide plano + eventos de claim em relatorio executivo: "
            "tasks claimed, agentes acionados (dispatch), ociosos restantes, "
            "fila, blockers (3 bugs). Proximos eventos esperados (open_pr)."
        ),
        expected_output="Relatorio markdown com secoes Dispatch, Idle, Blockers, Metricas.",
        agent=orchestrator,
        context=[plan_task, board_task],
        output_file=str(CREW_DIR / "output" / "sprint_report.md"),
    )

    review_task = Task(
        description=(
            "Workflow review como eventos: "
            "1) list_prs_pending_review "
            "2) emit_status_event(start_review) se revisor ocioso "
            "3) finalize_review_on_board → approve_review | request_changes "
            "4) notify: quem chamar (qa ou creator). "
            "5) Se test_failed_bug 3x na mesma task: blocker + skill impactada."
        ),
        expected_output=(
            "Tabela: task_id | event | reviewer/qa | verdict | next_agent | blocker?"
        ),
        agent=orchestrator,
        context=[report_task],
        output_file=str(CREW_DIR / "output" / "review_report.md"),
    )

    all_agents = [orchestrator, *specialists.values(), *reviewers.values()]

    return Crew(
        agents=all_agents,
        tasks=[plan_task, board_task, report_task, review_task],
        process=Process.sequential,
        verbose=True,
    )


def build_events_crew(dry_run: bool = False) -> Crew:
    """Crew focada em orquestrar Status como eventos + idle dispatch + blockers."""
    set_dry_run(dry_run)
    set_review_dry_run(dry_run)
    set_event_dry_run(dry_run)

    orchestrator = Agent(
        role="Event Orchestrator",
        goal=(
            "Tratar cada mudanca de Status do board como evento, "
            "despachar agentes ociosos e escalar blocker apos 3 bugs."
        ),
        backstory=(
            "Voce e o barramento de eventos do Project #2. "
            "Ferramentas: emit_status_event, notify_board_status_change, "
            "list_idle_crew_agents, register_task_bug, drain_dispatch_queue."
        ),
        tools=BOARD_TOOLS + EVENT_TOOLS,
        verbose=True,
        allow_delegation=True,
        llm=_llm(),
    )

    scan = Task(
        description=(
            "1) list_idle_crew_agents "
            "2) Varra board (list_backlog_by_agent / list_prs_pending_review) "
            "3) Para cada card elegivel, resolve_agent_for_board_event "
            "4) emit_status_event no evento correto (claim|start_review|start_test|merge_pr) "
            "5) drain_dispatch_queue "
            "6) Reporte blockers (bug_count>=3) com skill impactada."
        ),
        expected_output=(
            "Relatorio: eventos emitidos, dispatches, fila, blockers "
            "(task_id, motivo, skill, path da skill)."
        ),
        agent=orchestrator,
        output_file=str(CREW_DIR / "output" / "events_report.md"),
    )

    return Crew(
        agents=[orchestrator],
        tasks=[scan],
        process=Process.sequential,
        verbose=True,
    )


def build_review_crew(dry_run: bool = False) -> Crew:
    """Crew focada apenas em revisao e finalizacao de PRs."""
    set_dry_run(dry_run)
    set_review_dry_run(dry_run)
    set_event_dry_run(dry_run)

    lead_reviewer = Agent(
        role="Lead Code Reviewer",
        goal="Coordenar revisores pareados e finalizar PRs no board.",
        backstory="Supervisiona 8 revisores especializados do Guardiao Familia.",
        tools=REVIEW_TOOLS + [BOARD_TOOLS[3]],
        verbose=True,
        llm=_llm(),
    )

    reviewer_agents = []
    for role in CREATOR_ROLES:
        rev = reviewer_for(role)
        reviewer_agents.append(Agent(
            role=rev,
            goal=f"Revisar codigo de PRs criados por {role}.",
            backstory=_load_skill(rev),
            tools=REVIEW_TOOLS,
            verbose=True,
            llm=_llm(),
        ))

    scan_task = Task(
        description="Use list_prs_pending_review para listar PRs aguardando review.",
        expected_output="Lista priorizada task_id | creator | reviewer.",
        agent=lead_reviewer,
    )

    finalize_task = Task(
        description=(
            "Para cada item: get_pr_for_task, aplicar checklist da skill revisor, "
            "finalize_review_on_board. Produzir review_report com metricas."
        ),
        expected_output="Relatorio de reviews com verdicts e board atualizado.",
        agent=lead_reviewer,
        context=[scan_task],
        output_file=str(CREW_DIR / "output" / "review_report.md"),
    )

    return Crew(
        agents=[lead_reviewer, *reviewer_agents],
        tasks=[scan_task, finalize_task],
        process=Process.sequential,
        verbose=True,
    )


def build_hierarchical_crew(sprint: int = 1, dry_run: bool = False) -> Crew:
    """Crew hierarquica: manager delega para especialistas."""
    set_dry_run(dry_run)

    manager = Agent(
        role="Engineering Manager",
        goal=f"Orquestrar sprint {sprint} e manter board GitHub sincronizado.",
        backstory="Gerente tecnico que delega tasks e valida claims no Project #2.",
        tools=BOARD_TOOLS,
        verbose=True,
        llm=_llm(),
    )

    workers = []
    for role in ("backend", "frontend-mobile", "cloud-infra", "qa"):
        workers.append(Agent(
            role=role,
            goal=f"Receber e confirmar tasks {role}.",
            backstory=_load_skill(role),
            tools=[BOARD_TOOLS[1], BOARD_TOOLS[2]],
            verbose=True,
            llm=_llm(),
        ))

    delegate_task = Task(
        description=(
            f"Sprint {sprint}: planeje assignments, claim no board, "
            "delegue confirmacao a cada specialist. Atualize Status In Progress."
        ),
        expected_output="Relatorio final com tasks claimed e status board.",
        agent=manager,
    )

    return Crew(
        agents=[manager, *workers],
        tasks=[delegate_task],
        process=Process.hierarchical,
        manager_llm=_llm(),
        verbose=True,
    )
