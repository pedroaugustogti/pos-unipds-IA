"""Monta prompt de atuação completo para execute_agent_actuation_tool."""

from __future__ import annotations

from typing import Any

from board_automation.board.issue_task_body import build_agent_payload
from board_automation.board.task_status_workflow import build_event, merge_owner_for_task
from lib.orchestrator.phase_context import read_agent_docs
from lib.orchestrator.repo_context_scan import scan_repo_context


def _bullet(lines: list[str]) -> str:
    items = [str(x).strip() for x in lines if str(x).strip()]
    return "\n".join(f"- {x}" for x in items) if items else "- _(não definido no ticket)_"


def _section_repo_scan(scan: dict[str, Any]) -> str:
    if not scan.get("repo_available"):
        return _bullet(list(scan.get("notes") or []))
    parts: list[str] = [f"Path: `{scan.get('repo_path')}`"]
    for note in scan.get("notes") or []:
        parts.append(f"- {note}")
    for f in scan.get("files") or []:
        rel = f.get("path")
        if not rel:
            continue
        status = "OK" if f.get("exists") else "AUSENTE"
        syms = ", ".join(f.get("symbols") or []) or "—"
        parts.append(f"- `{rel}` [{status}] símbolos: {syms}")
        snippet = f.get("snippet") or []
        if snippet and f.get("exists"):
            preview = "\n".join(f"  {line}" for line in snippet[:12])
            parts.append(f"  ```\n{preview}\n  ```")
    return "\n".join(parts)


def _next_event_hint(ctx: dict[str, Any], assigned: str) -> str:
    ticket = ctx.get("ticket") or {}
    target = str(ctx.get("target_status") or "")
    creator = str(ticket.get("creator_role") or ctx.get("creator_role") or "backend")
    track = str(ticket.get("track") or "produto")
    expectations = ticket.get("handoff_expectations") or {}

    if target == "In Progress":
        return str(expectations.get("creator_exit_event") or build_event(creator, "Ready for Code Review"))
    if target == "In Code Review":
        return str(expectations.get("reviewer_exit_event") or build_event(f"{creator}-reviewer", "Ready for Test"))
    if target == "In Test":
        return str(expectations.get("qa_exit_event") or build_event("qa-gate", "In Pull Request"))
    if target == "In Pull Request":
        owner = str(expectations.get("merge_owner") or merge_owner_for_task(track))
        return str(expectations.get("merge_exit_event") or build_event(owner, "Done"))
    return build_event(assigned, target) if target else "noop"


def build_actuation_prompt(ctx: dict[str, Any]) -> dict[str, Any]:
    """
    Gera prompt markdown + metadados para a fase do assigned_agent.

    Entrada: resultado de prepare_actuation_for_event (antes de actuation_prompt).
    """
    assigned = str(ctx.get("assigned_agent") or "")
    ticket = ctx.get("ticket") or {}
    playbook = ctx.get("playbook") or {}
    handoff = ctx.get("handoff") or {}
    ci = ctx.get("ci") or {}
    board = ctx.get("board_task") or {}

    docs = read_agent_docs(ctx)
    skill_excerpt = (docs.get("skill") or "")[:3500]
    agent_md_excerpt = (docs.get("agent_prompt") or "")[:2000]

    responsibilities = list(ticket.get("agent_responsibilities") or [])
    if not responsibilities:
        payload = build_agent_payload({
            "id": ctx.get("task_id"),
            "title": ticket.get("title") or board.get("title"),
            "agent_role": ticket.get("creator_role") or board.get("agent_role"),
            "repo": ticket.get("repo") or board.get("repo"),
            "track": ticket.get("track") or board.get("track"),
            "refinement": {
                "context_summary": ticket.get("context_summary"),
                "in_scope": ticket.get("in_scope"),
            },
            "qa": ticket.get("qa") if isinstance(ticket.get("qa"), dict) else {},
        })
        responsibilities = list(
            (payload.get("agent_responsibilities") or {}).get(assigned) or []
        )
    if not responsibilities and assigned in (ticket.get("creator_role"), board.get("agent_role")):
        responsibilities = list(ticket.get("in_scope") or [])
    if not responsibilities and assigned.endswith("-reviewer"):
        responsibilities = [
            "Revisar diff/PR contra AC e escopo",
            "Validar testes e padrões do repo",
            "Aprovar (Ready for Test) ou retroceder com findings",
        ]
    if not responsibilities and assigned == "qa-gate":
        responsibilities = [
            "Executar suite QA/Appium conforme ticket",
            "Validar AC com evidências (PNG/MP4)",
            "Emitir qa-gate_in_pull_request ou retrocesso",
        ]

    repo = str(ticket.get("repo") or board.get("repo") or "")
    suggested = list(ticket.get("suggested_files") or [])
    repo_scan = scan_repo_context(repo, suggested)

    qa_block = ""
    if isinstance(ticket.get("qa"), dict) and ticket["qa"]:
        qa = ticket["qa"]
        qa_block = (
            f"### QA (qa-gate)\n"
            f"- Suite: `{qa.get('test_suite')}`\n"
            f"- Cenários: {qa.get('scenarios')}\n"
            f"- MCP: {qa.get('mcp_sequence') or qa.get('how_to_run')}\n"
        )

    user_flow = ticket.get("user_flow")
    user_flow_block = ""
    if isinstance(user_flow, dict) and user_flow:
        user_flow_block = (
            "### User flow (mobile)\n"
            f"- App: `{user_flow.get('app')}` · Emulator: `{user_flow.get('emulator')}` · Metro: `{user_flow.get('metro_port')}`\n"
            f"- Alvo: `{user_flow.get('target_screen')}` → `{user_flow.get('target_element')}`\n"
        )

    prompt = f"""# Prompt de atuação — {assigned}

## Situação do board
- **Task:** `{ctx.get('task_id')}` — {ticket.get('title') or board.get('title')}
- **Evento emitido:** `{ctx.get('event')}`
- **Status alvo:** `{ctx.get('target_status')}`
- **Agente atuante:** `{assigned}` (emissor do evento: `{ctx.get('acting_agent')}`)
- **Issue:** #{ticket.get('issue_number') or board.get('issue_number')} · Repo: `{repo}`
- **Board status atual:** `{board.get('board_status')}`

## Sua missão nesta fase
{playbook.get('start_hint')}

### Responsabilidades ({assigned})
{_bullet(responsibilities)}

### Playbook ReAct
- Passos: {", ".join(playbook.get("react_steps") or [])}
- Máx. iterações: {playbook.get("max_iterations")}

## Ticket — contexto e escopo
### Resumo
{ticket.get("context_summary") or "_(sem context_summary)_"}

### User story
{ticket.get("user_story") or "_(n/a)_"}

### Dentro do escopo
{_bullet(list(ticket.get("in_scope") or []))}

### Fora do escopo
{_bullet(list(ticket.get("out_of_scope") or []))}

### Não editar (do_not_touch)
{_bullet(list(ticket.get("do_not_touch") or []))}

### Critérios de aceite
{_bullet(list(ticket.get("acceptance_criteria") or []))}

### Verificação dos AC
{_bullet([f"{v.get('id')}: {v.get('command')} → {v.get('expected')}" for v in (ticket.get("ac_verification") or []) if isinstance(v, dict)])}

### Arquivos sugeridos
{_bullet(suggested)}

### Passos de implementação (creator)
{_bullet(list(ticket.get("implementation_steps") or []))}

{user_flow_block}
{qa_block}

## Repositório — leitura local
{_section_repo_scan(repo_scan)}

- **Branch:** `{ticket.get("branch")}` (base: `{ticket.get("base_branch")}`)
- **Path:** `{ticket.get("repo_path")}`

## Skill do agente (trecho)
{skill_excerpt}

## Agent.md (trecho)
{agent_md_excerpt}

## Handoff / CI
- Handoff summary: {handoff.get("summary") or "_(vazio)_"}
- PR: {handoff.get("pr_url") or ci.get("pr_url") or "_(sem PR)_"}
- CI: `{ci.get("ci_status") or "pending"}`

## Saída esperada desta fase
- **Próximo evento típico:** `{_next_event_hint(ctx, assigned)}`
- Respeite escopo, AC e skill. Não avance fase sem `emit_status_event` role-based.
- Após concluir o trabalho da fase, o pipeline chamará `execute_agent_actuation_tool` com este contexto.
"""

    return {
        "markdown": prompt.strip(),
        "assigned_agent": assigned,
        "target_status": ctx.get("target_status"),
        "repo_scan": repo_scan,
        "skill_path": docs.get("skill_path"),
        "agent_prompt_path": docs.get("agent_prompt_path"),
        "next_event_hint": _next_event_hint(ctx, assigned),
        "char_count": len(prompt),
    }
