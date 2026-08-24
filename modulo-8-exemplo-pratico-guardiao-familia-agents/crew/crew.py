#!/usr/bin/env python3
"""CrewAI — Supervisor despacha workers (não escreve o sprint inteiro sozinho)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CREW_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(CREW_DIR))

from lib.env_load import ensure_env  # noqa: E402

ensure_env()

from crewai import Agent, Crew, Process, Task  # noqa: E402

from tools.board_tools import BOARD_TOOLS, set_dry_run  # noqa: E402
from tools.event_tools import EVENT_TOOLS, set_dry_run as set_event_dry_run  # noqa: E402
from tools.review_tools import REVIEW_TOOLS, set_dry_run as set_review_dry_run  # noqa: E402
from lib.reviewer_pairs import CREATOR_ROLES, QA_GATE_ROLE, reviewer_for  # noqa: E402

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
    return os.environ.get("CREWAI_MODEL", "gpt-4o-mini")


def build_supervisor_crew(dry_run: bool = False) -> Crew:
    """
    Supervisor + um ciclo de despacho.
    O manager NÃO implementa código: só emite eventos via gateway e lista HITL.
    """
    set_dry_run(dry_run)
    set_review_dry_run(dry_run)
    set_event_dry_run(dry_run)

    supervisor = Agent(
        role="Board Event Supervisor",
        goal=(
            "Roteiar eventos de Status, despachar agentes ociosos e "
            "encaminhar HITL (merge, blocker 3 bugs, review alto risco)."
        ),
        backstory=(
            "Voce e o barramento Supervisor (modulo 8). "
            "Padrao: Sequential no Kanban + Parallel entre tasks. "
            "Porta unica: emit_status_event (gateway). "
            "Nunca mergeie sozinho. Nunca aprove review de SOS/pagamentos/LGPD "
            "sem fila HITL. Workers recebem handoff JSON, nao so task_id."
        ),
        tools=BOARD_TOOLS + EVENT_TOOLS,
        verbose=True,
        allow_delegation=False,
        llm=_llm(),
    )

    scan = Task(
        description=(
            "1) list_idle_crew_agents / snapshot_observability\n"
            "2) Varra filas (Todo claimaveis, Ready for Code Review, Ready for Test, "
            "In Pull Request)\n"
            "3) Para cada card elegivel: resolve_agent_for_board_event\n"
            "4) emit_status_event via tools (claim|start_review|start_test) "
            "somente se agente ocioso e SEM HITL bloqueante\n"
            "5) drain_dispatch_queue\n"
            "6) Liste hitl_queue e blockers — NAO force merge_pr\n"
            "7) Relatorio: dispatches, fila, HITL pendente, gaps"
        ),
        expected_output=(
            "Markdown: Eventos | Dispatches | Idle | HITL queue | Blockers | "
            "Proximos passos humanos"
        ),
        agent=supervisor,
        output_file=str(CREW_DIR / "output" / "supervisor_report.md"),
    )

    return Crew(
        agents=[supervisor],
        tasks=[scan],
        process=Process.sequential,
        verbose=True,
    )


def build_worker_crew(role: str, dry_run: bool = False) -> Crew:
    """Worker unico: executa uma etapa apos handoff (creator ou reviewer)."""
    set_dry_run(dry_run)
    set_review_dry_run(dry_run)
    set_event_dry_run(dry_run)

    is_reviewer = role.endswith("-reviewer")
    is_gate = role == QA_GATE_ROLE

    worker = Agent(
        role=f"Worker {role}",
        goal=(
            f"Consumir handoff em crew/output/handoffs/, executar ate "
            f"{'propor veredito' if is_reviewer else 'open_pr ou bug'}, "
            f"respeitar teto ReAct e emitir evento via gateway."
        ),
        backstory=_load_skill(role.replace("-reviewer", "") if is_reviewer else role),
        tools=(REVIEW_TOOLS if is_reviewer else BOARD_TOOLS[:4]) + EVENT_TOOLS,
        verbose=True,
        allow_delegation=False,
        llm=_llm(),
    )

    task = Task(
        description=(
            f"Papel `{role}`.\n"
            "1) Leia handoff da task atribuida (busy no runtime)\n"
            "2) Siga loop ReAct (max 4): Thought → Act → Observe\n"
            "3) Ao convergir: emit_status_event (open_pr | propose_review | "
            "test_passed | test_failed_bug)\n"
            "4) Se limite de iteracoes: NAO force Done — marque HITL\n"
            f"5) {'QA-gate: nao claim Todo de harness' if is_gate else 'Respeite fronteira de repo/skill'}"
        ),
        expected_output="Relatorio ReAct + evento emitido + path do handoff atualizado",
        agent=worker,
        output_file=str(CREW_DIR / "output" / f"worker_{role.replace('/', '_')}.md"),
    )

    return Crew(agents=[worker], tasks=[task], process=Process.sequential, verbose=True)


def build_events_crew(dry_run: bool = False) -> Crew:
    """Compat: modo events = supervisor."""
    return build_supervisor_crew(dry_run=dry_run)


def build_crew(sprint: int = 1, dry_run: bool = False) -> Crew:
    """Compat legado: supervisor planeja claims do sprint (sem implementar)."""
    set_dry_run(dry_run)
    set_event_dry_run(dry_run)
    crew = build_supervisor_crew(dry_run=dry_run)
    # sobrescreve task para mencionar sprint
    crew.tasks[0].description = (
        f"Sprint {sprint}. " + str(crew.tasks[0].description)
        + "\nUse plan_sprint_assignments só para priorizar; claims via emit_status_event."
    )
    return crew


def build_review_crew(dry_run: bool = False) -> Crew:
    return build_worker_crew("backend-reviewer", dry_run=dry_run)


def build_hierarchical_crew(sprint: int = 1, dry_run: bool = False) -> Crew:
    """Supervisor + workers registrados (delegacao explicita desligada no manager)."""
    set_dry_run(dry_run)
    set_event_dry_run(dry_run)

    supervisor = Agent(
        role="Engineering Manager",
        goal=f"Despachar sprint {sprint} por eventos; nunca mergear.",
        backstory="Supervisor do board Guardião Família (padrão módulo 8).",
        tools=BOARD_TOOLS + EVENT_TOOLS,
        verbose=True,
        allow_delegation=True,
        llm=_llm(),
    )

    workers = []
    for role in list(CREATOR_ROLES) + [QA_GATE_ROLE]:
        workers.append(
            Agent(
                role=role,
                goal=f"Confirmar handoff e disponibilidade para {role}.",
                backstory=_load_skill(role if role != "qa-author" else "qa"),
                tools=EVENT_TOOLS,
                verbose=True,
                allow_delegation=False,
                llm=_llm(),
            )
        )

    task = Task(
        description=(
            f"Sprint {sprint}: liste idle, proponha dispatches, "
            "liste HITL. Nao execute merge_pr. Workers apenas confirmam."
        ),
        expected_output="Plano de despacho + HITL",
        agent=supervisor,
        output_file=str(CREW_DIR / "output" / "hierarchical_dispatch.md"),
    )

    return Crew(
        agents=[supervisor, *workers],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )
