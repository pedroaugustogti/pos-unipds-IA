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

    orchestrator = Agent(
        role="Engineering Manager / Scrum Orchestrator",
        goal=(
            f"Planejar sprint {sprint}, rotear tasks, sincronizar board Project #2 "
            "no workflow Todo→Done (8 status) e delegar claims."
        ),
        backstory=(
            "Voce coordena 8 criadores + 8 revisores + QA + DevOps. "
            "Respeita transicoes: claim→In Progress, open_pr→Ready for CR, "
            "approve→Ready for Test, test_passed→In PR, merge→Done."
        ),
        tools=BOARD_TOOLS,
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
            f"Execute batch_claim_sprint(sprint={sprint}, limit_per_agent=1) "
            "para atualizar labels, comentarios e Status In Progress no Project #2. "
            "Reporte sucesso/falha por task."
        ),
        expected_output="JSON ou tabela com resultado de cada claim (labels, comment, board_status).",
        agent=orchestrator,
        context=[plan_task],
    )

    report_task = Task(
        description=(
            "Consolide plano + claims em relatorio executivo: "
            "tasks claimed, agentes acionados, proximos passos (implementacao + PR). "
            "Inclua metricas: total SP claimed, agents ativos, blockers."
        ),
        expected_output="Relatorio markdown pronto para docs/ com secao Metricas.",
        agent=orchestrator,
        context=[plan_task, board_task],
        output_file=str(CREW_DIR / "output" / "sprint_report.md"),
    )

    review_task = Task(
        description=(
            "Workflow review (Ready for Code Review → In Code Review → Ready for Test): "
            "1) list_prs_pending_review "
            "2) start_code_review por revisor pareado "
            "3) finalize_review_on_board: approved → Ready for Test; changes_requested → In Progress "
            "4) Se creator corrigir: resubmit_after_review → In Code Review"
        ),
        expected_output="Tabela: task_id | reviewer | verdict | board_status | proximo agente (qa/creator).",
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


def build_review_crew(dry_run: bool = False) -> Crew:
    """Crew focada apenas em revisao e finalizacao de PRs."""
    set_dry_run(dry_run)
    set_review_dry_run(dry_run)

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
