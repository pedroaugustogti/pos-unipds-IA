"""Monta corpo de issue GitHub rico — evita alucinação e perda de contexto entre agentes."""

from __future__ import annotations

import json
from typing import Any

from board_automation.board.reviewer_pairs import reviewer_for
from board_automation.board.task_status_workflow import build_event
from board_automation.board.reviewer_pairs import normalize_creator_role

GUARDAO_ROOT = r"C:\Users\pedro\Documents\guardiao-familia"
MODULE8 = "modulo-8-exemplo-pratico-guardiao-familia-agents"

REDIRECT_TABLE = """| Se precisar de… | Pare e redirecione para |
|-----------------|-------------------------|
| Terraform / AWS apply | `cloud-infra` |
| GitHub Actions / deploy | `devops-cicd` |
| Migration PostgreSQL | `database` |
| Endpoint NestJS / service | `backend` |
| App parent/child RN | `frontend-mobile` |
| Site / backoffice | `frontend-web` |
| Escrever specs de teste | `qa-author` |
| Submit stores | `stores-release` |"""


def _reviewer(agent_role: str) -> str:
    return reviewer_for(agent_role) or f"{agent_role}-reviewer"


def _task_events(agent_role: str, reviewer: str, merge_owner: str) -> dict[str, str]:
    """Eventos role-based v2 para esta task (gateway / MCP)."""
    role = normalize_creator_role(agent_role)
    return {
        "orchestrator_enter": "orchestrator_enter_in_progress",
        "creator_in_progress": build_event(role, "In Progress"),
        "ready_for_cr": build_event(role, "Ready for Code Review"),
        "in_code_review": build_event(reviewer, "In Code Review"),
        "ready_for_test": build_event(reviewer, "Ready for Test"),
        "return_in_progress": build_event(reviewer, "In Progress", return_=True),
        "resubmit_cr": build_event(role, "In Code Review"),
        "qa_in_test": build_event("qa-gate", "In Test"),
        "qa_in_pr": build_event("qa-gate", "In Pull Request"),
        "qa_return": build_event("qa-gate", "In Progress", return_=True),
        "merge_done": build_event(merge_owner, "Done"),
    }


def _slug(task_id: str) -> str:
    return task_id.lower().replace("-", "")


def default_branch(repo: str) -> str:
    if repo in ("guardiao-familia-parent", "guardiao-familia-child", "guardiao-familia-site"):
        return "master"
    return "main"


MOBILE_APPS = frozenset({"guardiao-familia-parent", "guardiao-familia-child"})
MOBILE_DEFAULTS = {
    "guardiao-familia-parent": {"emulator": "emulator-5554", "metro_port": 8082, "bundle": "com.guardiaofamilia.parent"},
    "guardiao-familia-child": {"emulator": "emulator-5556", "metro_port": 9090, "bundle": "com.guardiofilho"},
}

_QA_REPRO_CLI_MARKERS = (
    "qa_mobile_evidence.py",
    "mobile_e2e_seed.py",
    "qa-gate/scripts/",
    "python agents/",
    "subir stack:",
)


def _normalize_qa_repro_steps(steps: list[str], *, mobile: bool) -> list[str]:
    """Remove passos de execução CLI — qa_repro_steps = o que validar após suite MCP."""
    if not mobile or not steps:
        return steps
    out = [s for s in steps if not any(m in s.lower() for m in _QA_REPRO_CLI_MARKERS)]
    if out:
        return out
    return [
        "Após `qa_appium_suite_*`: confirmar `target_element` visível",
        "Screenshot + MP4 conforme AC (gerados pela suite MCP)",
    ]


def _qa_db_seed_profile(repo: str, qa: dict[str, Any]) -> str:
    raw = qa.get("db_seed")
    if isinstance(raw, dict) and raw.get("profile"):
        return str(raw["profile"])
    if repo == "guardiao-familia-child":
        return "basic_parent"
    return "child_home"


def _qa_appium_child_only(repo: str, qa: dict[str, Any]) -> bool:
    """Child com seed na API: Appium só no emulator-5556; parent/família já no Postgres."""
    scope = qa.get("appium_scope")
    if scope == "child_only":
        return True
    if scope in ("dual", "parent_child"):
        return False
    if repo != "guardiao-familia-child":
        return False
    raw = qa.get("db_seed")
    return isinstance(raw, dict) and bool(raw.get("enabled"))


def format_qa_repro_appium_section(
    tid: str,
    qa_steps: list[str],
    qa: dict[str, Any],
    *,
    repo: str = "",
) -> list[str]:
    """Secção 2.1 — reprodução QA/Appium sempre via MCP."""
    raw_seed = qa.get("db_seed")
    profile = _qa_db_seed_profile(repo, qa) if repo else "child_home"
    if isinstance(raw_seed, dict) and raw_seed.get("profile") and not repo:
        profile = str(raw_seed["profile"])
    child_only = _qa_appium_child_only(repo, qa) if repo else False
    appium_tool = "qa_appium_suite_child" if profile != "pairing_warm" else "qa_appium_suite_parent"
    appium_args = f'from_db_seed=true, task_id="{tid}", dry_run=false'
    if child_only and appium_tool == "qa_appium_suite_child":
        appium_args += ", child_only=true"
    cleanup_note = (
        f"7. qa_db_cleanup(task_id=\"{tid}\", dry_run=false)  # qa.db_seed.cleanup=true"
        if isinstance(raw_seed, dict) and raw_seed.get("cleanup")
        else f"7. qa_db_cleanup(task_id=\"{tid}\", dry_run=false)  # se qa.db_seed.cleanup=true"
    )

    lines = [
        "### Reproduzir (QA / Appium)",
        "",
        "> **Regra:** reprodução E2E/Appium é **sempre via MCP** (`guardiao-familia-agents`). "
        "Não usar `qa_mobile_evidence.py`, Appium CLI ou `adb` como caminho principal — "
        "executar a sequência abaixo (detalhe na **sec. 6** e **Anexo D**). "
        "Fallback CLI somente se `list_mcp_tools()` falhar.",
        "",
        "```",
        "1. list_mcp_tools()",
        f"2. get_handoff(task_id=\"{tid}\")",
        f"3. emit_status_event(task_id=\"{tid}\", event=\"qa-gate_in_test\", dry_run=false)",
        f"4. query_mobile_flow_rag(query=<feature/tela>, task_id=\"{tid}\")",
        f"5. qa_db_seed(task_id=\"{tid}\", profile=\"{profile}\", use_task_config=true, dry_run=false)",
        f"6. {appium_tool}({appium_args})",
        "   # validar cenários abaixo + evidências PNG/MP4",
        cleanup_note,
        f"8. emit_status_event(task_id=\"{tid}\", event=\"qa-gate_in_pull_request\"|\"qa-gate_return_in_progress\", dry_run=false)",
        "```",
        "",
        "#### Cenários a validar (pós-suite MCP)",
    ]
    if qa_steps:
        lines.extend(f"{i + 1}. {s}" for i, s in enumerate(qa_steps))
    else:
        lines.extend([
            "1. Seguir passos da tabela acima até `target_element`",
            "2. Screenshot/vídeo no elemento alvo",
        ])
    lines.append("")
    return lines


def format_user_flow_section(
    ref: dict[str, Any],
    repo: str,
    agent_role: str,
    *,
    tid: str = "",
    qa: dict[str, Any] | None = None,
) -> list[str]:
    """Secção 2.1 — obrigatória para frontend-mobile."""
    if agent_role != "frontend-mobile":
        return []

    uf = ref.get("user_flow") or {}
    flow_id = ref.get("user_flow_id") or uf.get("flow_id")
    db_note = ""
    if flow_id:
        db_note = f"\n> Fonte: `mobile_user_flows.db` · flow_id `{flow_id}`\n"
    defaults = MOBILE_DEFAULTS.get(repo, {})
    app = uf.get("app") or repo
    entry = uf.get("entry_point") or "_(preencher entry_point)_"
    pre = uf.get("preconditions") or []
    steps = uf.get("steps") or []
    target_screen = uf.get("target_screen") or "_(target_screen)_"
    target_el = uf.get("target_element") or "_(target_element)_"
    nav_files = uf.get("navigation_files") or []
    emulator = uf.get("emulator") or defaults.get("emulator", "emulator-5554")
    metro = uf.get("metro_port") or defaults.get("metro_port", 8082)
    mermaid = uf.get("mermaid") or ""

    pre_lines = "\n".join(f"- [ ] {p}" for p in pre) if pre else "- [ ] _(preconditions)_"
    nav_lines = "\n".join(f"- `{f}`" for f in nav_files) if nav_files else "- _(navigation_files — ex.: App.tsx)_"

    if steps:
        table = ["| # | Tela | Ação usuário | Comportamento | Arquivo / condição |", "|---|------|--------------|---------------|-------------------|"]
        for s in steps:
            table.append(
                f"| {s.get('order', '?')} | {s.get('screen', '')} | {s.get('user_action', '')} | "
                f"{s.get('system_behavior', '')} | `{s.get('file', '')}` {s.get('route_condition', '')} |".strip()
            )
        steps_block = "\n".join(table)
    else:
        steps_block = "| # | Tela | Ação | Comportamento | Arquivo |\n|---|------|------|---------------|--------|\n| 1 | | | | |"

    mermaid_block = f"```mermaid\n{mermaid}\n```" if mermaid else "_diagrama opcional_"

    qa_steps = uf.get("qa_repro_steps") or []
    qa_dict = qa or {}
    qa_steps = _normalize_qa_repro_steps(qa_steps, mobile=_is_mobile_qa(repo, qa_dict))
    repro_block = (
        format_qa_repro_appium_section(tid, qa_steps, qa_dict, repo=repo)
        if tid and _is_mobile_qa(repo, qa_dict)
        else [
            "### Reproduzir (QA / Appium)",
            "\n".join(f"{i + 1}. {s}" for i, s in enumerate(qa_steps))
            if qa_steps
            else "1. Seguir tabela acima no emulador\n2. Screenshot/vídeo no elemento alvo",
            "",
        ]
    )

    return [
        "",
        "## 2.1 Fluxo do usuário até a funcionalidade *(frontend-mobile — obrigatório)*",
        db_note,
        "",
        "> Creator e qa-gate **seguem os passos abaixo** (user flow obrigatório: `app`, `entry_point`, `preconditions`, `steps`, `target_screen`, `target_element`, `emulator`, `metro_port`).",
        "",
        f"| Campo | Valor |",
        f"|-------|-------|",
        f"| App | `{app}` |",
        f"| Entry point | {entry} |",
        f"| Emulador | `{emulator}` |",
        f"| Metro | port `{metro}` |",
        f"| **Alvo** | `{target_screen}` → `{target_el}` |",
        "",
        "### Pré-condições",
        pre_lines,
        "",
        "### Navegação (arquivos de rota)",
        nav_lines,
        "",
        "### Passos",
        steps_block,
        "",
        "### Diagrama",
        mermaid_block,
        "",
        *repro_block,
    ]


def format_agent_responsibilities_section(task: dict[str, Any], reviewer: str) -> list[str]:
    raw = task.get("agent_responsibilities")
    if not raw or not isinstance(raw, dict):
        return []
    agent_role = str(task.get("agent_role") or "creator")
    ordered: list[tuple[str, Any]] = [
        (agent_role, raw.get(agent_role)),
        (reviewer, raw.get(reviewer) or raw.get(f"{agent_role}-reviewer")),
        ("qa-gate", raw.get("qa-gate") or raw.get("qa-agent") or raw.get("qa")),
    ]
    lines = [
        "",
        "## 0.1 Responsabilidades por agente (esta task)",
        "",
        "> Cada agente executa **apenas** o seu bloco. Não avançar fase sem evento do board.",
        "",
    ]
    found = False
    for role, items in ordered:
        if not items:
            continue
        found = True
        if isinstance(items, str):
            items = [items]
        lines.append(f"### `{role}`")
        lines.append("")
        for item in items:
            lines.append(f"- {item}")
        lines.append("")
    return lines if found else []


def _is_mobile_qa(repo: str, qa: dict[str, Any]) -> bool:
    return repo in MOBILE_APPS or bool(qa.get("db_seed"))


def format_phase_table(
    agent_role: str,
    reviewer: str,
    handoff: dict[str, Any],
    repo: str,
    qa: dict[str, Any],
) -> list[str]:
    mobile = _is_mobile_qa(repo, qa)
    child_only = _qa_appium_child_only(repo, qa)
    qa_cell = (
        "MCP `qa_db_seed(basic_parent)` → `qa_appium_suite_child(child_only=true)` → evidências → `qa_db_cleanup`"
        if child_only
        else (
            "MCP `qa_db_seed` → `qa_appium_suite_*` → evidências → `qa_db_cleanup`"
            if mobile
            else "Executar suite sec. 6 + evidências"
        )
    )
    impl_forbid = "Merge, QA Appium, fora do escopo" if mobile else "Merge, QA E2E, fora do escopo"
    rag = ", RAG antes de codar" if agent_role == "frontend-mobile" else ""
    impl_resp = (
        "Codificar escopo sec. 3 · estratégia no PR/comentário · arquivos alterados · testes unitários"
        if agent_role == "frontend-mobile"
        else f"Entregar diff no escopo sec. 3 + AC locais"
    )
    review_resp = (
        "Avaliar implementação do creator · qualidade de código · cobertura de testes unitários"
        if "mobile" in reviewer or agent_role == "frontend-mobile"
        else "Review PR, eventos role-based v2 (ver Anexo A)"
    )
    qa_resp = (
        "Cenários + AC · MCP guardiao-familia-agents · evidências PNG/MP4/JSON"
        if mobile
        else qa_cell
    )
    return [
        "| Fase | Board Status | Agente | Responsabilidade | Proibido nesta fase |",
        "|------|--------------|--------|------------------|---------------------|",
        f"| Dispatch | Todo → In Progress | **{agent_role}** (creator) | Branch, implementar escopo sec. 3, testes{rag} | Review próprio código |",
        f"| Implementar | In Progress | **{agent_role}** | {impl_resp} | {impl_forbid} |",
        f"| Review | In Code Review | **{reviewer}** | {review_resp} | Implementar feature, rodar QA gate |",
        f"| QA | In Test | **qa-gate** | {qa_resp} | Merge PR, alterar código |",
        f"| Merge | In Pull Request | **{handoff['merge_owner']}** | `{build_event(handoff['merge_owner'], 'Done')}` após HITL | Alterar código da feature |",
    ]


def format_qa_mcp_steps(tid: str, profile: str = "child_home", *, child_only: bool = False) -> list[str]:
    appium_tool = "qa_appium_suite_child" if profile != "pairing_warm" else "qa_appium_suite_parent"
    appium_params = f"`from_db_seed=true`, `task_id={tid}`, `dry_run=false`"
    if child_only and appium_tool == "qa_appium_suite_child":
        appium_params += ", `child_only=true`"
    return [
        "",
        "### DB seed + suite (MCP — obrigatório)",
        "",
        "| Passo | Tool MCP | Parâmetros |",
        "|-------|----------|------------|",
        f"| 1 | `get_handoff` | `task_id={tid}` |",
        f"| 2 | `emit_status_event` | `event=qa-gate_in_test`, `dry_run=false` |",
        f"| 3 | `query_mobile_flow_rag` | `query=<tela/feature>`, `task_id={tid}` |",
        f"| 4 | `qa_db_seed` | `task_id={tid}`, `profile={profile}`, `use_task_config=true`, `dry_run=false` |",
        f"| 5 | `{appium_tool}` | {appium_params} |",
        f"| 6 | (evidência) | screenshots / MP4 conforme AC |",
        f"| 7 | `qa_db_cleanup` | `task_id={tid}`, `dry_run=false` |",
        f"| 8 | `emit_status_event` | `qa-gate_in_pull_request` ou `qa-gate_return_in_progress`, `dry_run=false` |",
        "",
    ]


def format_qa_section(qa: dict[str, Any], tid: str, repo: str) -> list[str]:
    ev = qa.get("evidence") or {}
    ev_list = [k.replace("_", " ") for k, v in ev.items() if v] or ["json report"]
    mobile = _is_mobile_qa(repo, qa)
    raw_seed = qa.get("db_seed")
    profile = _qa_db_seed_profile(repo, qa)
    child_only = _qa_appium_child_only(repo, qa)

    lines = [
        "## 6. QA (qa-gate)",
        "",
        "| Campo | Valor |",
        "|-------|-------|",
        f"| test_suite | `{qa.get('test_suite', 'qa-custom')}` |",
        f"| Cenários | {', '.join(qa.get('scenarios') or [])} |",
        f"| Evidências obrigatórias | {', '.join(ev_list)} |",
    ]
    if child_only:
        lines.append(
            "| Execução Appium | **Somente app child** (`emulator-5556`, `child_only=true`) — "
            f"massa parent/família via `qa_db_seed(profile={profile})`; não abrir emulador parent |"
        )
    if mobile:
        lines.append("| MCP server | `guardiao-familia-agents` (`list_mcp_tools`) |")
    lines.append("| Referência QA | **Anexo D** (qa-gate + evidências) |")
    if mobile:
        lines.extend(format_qa_mcp_steps(tid, profile, child_only=child_only))
    lines.extend(format_db_seed_section(qa, tid))
    how = (qa.get("how_to_run") or "").strip()
    if how:
        label = "**Fallback CLI (somente se MCP indisponível):**" if mobile else "**Comando principal:**"
        lines.append(label)
        lines.append("")
        lines.append("```powershell")
        lines.append(how)
        lines.append("```")
        lines.append("")
    lines.append("**Regra:** se qualquer AC = FAIL → `qa-gate_return_in_progress` + comentário qa-gate (sec. 10). Não merge.")
    lines.append("")
    return lines


def _format_annex_d_mobile(tid: str, repo: str, qa: dict[str, Any]) -> str:
    child_only = _qa_appium_child_only(repo, qa)
    profile = _qa_db_seed_profile(repo, qa)
    appium_call = (
        "`qa_appium_suite_child(from_db_seed=true, child_only=true)`"
        if child_only
        else "`qa_appium_suite_child(from_db_seed=true)`"
    )
    if child_only:
        stack = (
            f"**Stack Appium:** somente child (`emulator-5556`, Metro `:9090`) + Docker API/Postgres — "
            f"parent/família via `qa_db_seed(profile={profile})`; **não** subir emulador parent (5554)"
        )
        markers = "`fast-stack-last.json` → `ok: true` · log com `SMOKE_CHILD_OK` · ChildHomeV2 visível"
    else:
        stack = (
            "**Stack:** Docker API/Postgres · emuladores 5554+5556 · `fast-stack.ps1` no mobile-setup · Appium dual"
        )
        markers = "`fast-stack-last.json` → `ok: true` · log com `PAIRING_COMPLETE` / `SMOKE_CHILD_OK`"
    evidence = f"agents/00-runtime/output/{tid}/qa-gate-({{N}})/evidence/"
    return f"""## Anexo D — Papel `qa-gate` + evidências mobile (resumo)

**MCP (obrigatório):** `get_handoff` → `qa-gate_in_test` → `qa_db_seed(profile={profile})` → {appium_call} → screenshots/MP4 → `qa_db_cleanup` → `qa-gate_in_pull_request` | `qa-gate_return_in_progress`

{stack}

**Evidências:** PNG + MP4 + JSON em `{evidence}`

**Marcadores de sucesso:** {markers}

**Anti-patterns:** `qa-gate_in_pull_request` sem evidência visual · Appium sem `APPS_READY_OK` · commitar `stage-handoff.json`"""


def format_appendices(
    task: dict[str, Any],
    agent_role: str,
    reviewer: str,
    handoff: dict[str, Any],
    ref: dict[str, Any],
    qa: dict[str, Any],
    ev: dict[str, str],
) -> list[str]:
    tid = task["id"]
    title = task["title"]
    repo = task["repo"]
    mobile = _is_mobile_qa(repo, qa)
    defaults = MOBILE_DEFAULTS.get(repo, {})
    files = ref.get("suggested_files") or []
    file_rows = "\n".join(f"| `{f}` | alteração conforme escopo |" for f in files[:6]) or "| _(suggested_files)_ | |"

    annex_d_mobile = _format_annex_d_mobile(tid, repo, qa)

    annex_d_generic = """## Anexo D — Papel `qa-gate` (resumo)

- Ler handoff + `qa-gate_in_test` via MCP `emit_status_event`
- Executar suite sec. 6 e validar todos os AC
- Anexar evidências (screenshot, log, JSON) na issue
- `qa-gate_in_pull_request` somente se todos AC PASS · senão `qa-gate_return_in_progress`
- Não alterar código da feature nem fazer merge"""

    annex_b_extra = ""
    if agent_role == "frontend-mobile":
        emu = defaults.get("emulator", "emulator-5554")
        metro = defaults.get("metro_port", 8082)
        annex_b_extra = f"""
- Repo desta task: `{repo}` · Metro **{metro}** · emulador **{emu}**
- Antes de codar: `query_mobile_flow_rag` (MCP) para fluxo 0→N e arquivos de tela"""

    return [
        "---",
        "",
        "## Anexo A — Fluxo board (eventos v2 role-based)",
        "",
        "| Evento | Status alvo | Quem dispara |",
        "|--------|-------------|--------------|",
        f"| `{ev['orchestrator_enter']}` | In Progress | orchestrator |",
        f"| `{ev['creator_in_progress']}` | In Progress | {agent_role} |",
        f"| `{ev['ready_for_cr']}` | Ready for Code Review | {agent_role} |",
        f"| `{ev['in_code_review']}` | In Code Review | {reviewer} |",
        f"| `{ev['ready_for_test']}` | Ready for Test | {reviewer} |",
        f"| `{ev['return_in_progress']}` | In Progress | {reviewer} |",
        f"| `{ev['resubmit_cr']}` | In Code Review | {agent_role} (pós-correção) |",
        f"| `{ev['qa_in_test']}` | In Test | qa-gate |",
        f"| `{ev['qa_in_pr']}` | In Pull Request | qa-gate |",
        f"| `{ev['qa_return']}` | In Progress | qa-gate |",
        f"| `{ev['merge_done']}` | Done | {handoff['merge_owner']} |",
        "",
        f"## Anexo B — Papel `{agent_role}` (resumo)",
        "",
        f"- Implementar apenas escopo sec. 3 · eventos MCP: `{ev['creator_in_progress']}` → `{ev['ready_for_cr']}`{annex_b_extra}",
        "- Não executar QA gate nem merge — handoff para reviewer e qa-gate",
        "- Redirecionar trabalho fora do escopo → agente correto (sec. 3)",
        "",
        f"## Anexo C — Papel `{reviewer}` (resumo)",
        "",
        f"- Assumir PR em **Ready for Code Review** (`{ev['in_code_review']}`)",
        "- Validar escopo sec. 3, qualidade do código e testes do creator",
        f"- `{ev['ready_for_test']}` → Ready for Test · `{ev['return_in_progress']}` → In Progress com comentários acionáveis",
        "- Não implementar feature nem rodar suite QA gate",
        "",
        annex_d_mobile if mobile else annex_d_generic,
        "",
        f"## Anexo E — Template PR (preencher antes de `{ev['ready_for_cr']}`)",
        "",
        "```markdown",
        "## Resumo",
        f"**Task:** {tid} — {title}",
        f"**Agente:** {agent_role} · **Repo:** {repo}",
        "",
        "## Estratégia",
        "1. _(decisões técnicas principais)_",
        "2. _(ordem de implementação)_",
        "",
        "## Arquivos alterados",
        "| Arquivo | Mudança |",
        "|---------|---------|",
        file_rows,
        "",
        "## Test plan",
        "- [ ] Todos os AC sec. 5 verificados localmente",
        "- [ ] Sem regressão nos fluxos críticos",
        "",
        "## Board",
        f"- [ ] Issue {tid} → Ready for Code Review",
        "- [ ] Comentário sec. 10.1 na issue",
        "```",
        "",
    ]


def format_db_seed_section(qa: dict[str, Any], task_id: str) -> list[str]:
    raw = qa.get("db_seed")
    if not raw:
        return []
    if isinstance(raw, bool) and not raw:
        return []
    from lib.mobile.mobile_e2e_seed import SEED_PROFILES, default_db_seed_config

    cfg = raw if isinstance(raw, dict) else default_db_seed_config(task_id)
    profile = str(cfg.get("profile") or "child_home")
    meta = SEED_PROFILES.get(profile, {})
    profiles_doc = " · ".join(f"`{k}`" for k in SEED_PROFILES)
    return [
        "",
        "### DB seed (config ticket)",
        "",
        "| Campo | Valor |",
        "|-------|-------|",
        f"| enabled | `{bool(cfg.get('enabled', True))}` |",
        f"| profile | `{profile}` — {meta.get('summary', '')} |",
        f"| family_name | `{cfg.get('family_name', f'QA Evidence {task_id}')}` |",
        f"| child_name | `{cfg.get('child_name', '')}` |",
        f"| resume_after_step | `{cfg.get('resume_after_step', meta.get('resume_after_step'))}` |",
        f"| cleanup | `{bool(cfg.get('cleanup', True))}` pós-evidência |",
        "",
        f"Profiles disponíveis: {profiles_doc}",
        "",
        "**Dependências:** Docker (Postgres/Redis/API) · `guardiao-familia-mobile-setup` · emuladores 5554/5556 · MCP `guardiao-familia-agents` habilitado no Cursor",
        "",
    ]


def build_agent_payload(task: dict[str, Any]) -> dict[str, Any]:
    ref = task.get("refinement") or {}
    qa = task.get("qa") or {}
    tid = task["id"]
    agent_role = task["agent_role"]
    repo = task["repo"]
    reviewer = _reviewer(agent_role)
    merge_owner = "stores-release" if task.get("track") == "stores" else "devops-cicd"
    ev = _task_events(agent_role, reviewer, merge_owner)
    return {
        "task_id": tid,
        "title": task["title"],
        "agent_role": agent_role,
        "agent_role_secondary": task.get("agent_role_secondary") or "",
        "track": task["track"],
        "repo": repo,
        "repo_path": task.get("repo_path") or f"{GUARDAO_ROOT}\\{repo}",
        "epic_id": task.get("epic_id", ""),
        "release_blocker": bool(task.get("release_blocker")),
        "depends_on": [task["depends_on"]] if task.get("depends_on") else [],
        "branch": task.get("branch") or f"feat/{tid.lower()}-sandbox",
        "base_branch": task.get("base_branch") or default_branch(repo),
        "user_flow": ref.get("user_flow") if agent_role == "frontend-mobile" else None,
        "refinement": ref,
        "qa": qa,
        "agent_responsibilities": task.get("agent_responsibilities") or {},
        "handoff_expectations": task.get("handoff_expectations")
        or {
            "creator_exit_event": ev["ready_for_cr"],
            "reviewer_exit_event": ev["ready_for_test"],
            "qa_exit_event": ev["qa_in_pr"],
            "merge_owner": merge_owner,
            "merge_exit_event": ev["merge_done"],
        },
    }


def _enrich_refinement_from_db(task: dict[str, Any]) -> dict[str, Any]:
    """Merge user_flow do SQLite local quando ticket mobile incompleto."""
    ref = dict(task.get("refinement") or {})
    if task.get("agent_role") != "frontend-mobile":
        return ref
    try:
        from lib.mobile.mobile_flow_discovery import resolve_user_flow_for_task

        db_flow = resolve_user_flow_for_task({**task, "refinement": ref})
    except Exception:  # noqa: BLE001
        return ref
    if not db_flow:
        return ref
    existing = ref.get("user_flow") or {}
    if existing.get("steps") and not db_flow.get("steps"):
        return ref
    merged = {**db_flow, **{k: v for k, v in existing.items() if v}}
    ref["user_flow"] = merged
    if db_flow.get("flow_id"):
        ref["user_flow_id"] = db_flow["flow_id"]
    return ref


def build_issue_body(task: dict[str, Any], conventions: dict[str, str] | None = None) -> str:
    """Corpo markdown completo para issue — fonte única template + P3 seed."""
    task = {**task, "refinement": _enrich_refinement_from_db(task)}
    conv = conventions or {}
    ref = task.get("refinement") or {}
    qa = task.get("qa") or {}
    tid = task["id"]
    agent_role = task["agent_role"]
    repo = task["repo"]
    reviewer = _reviewer(agent_role)
    payload = build_agent_payload(task)
    handoff = payload["handoff_expectations"]
    ev = _task_events(agent_role, reviewer, handoff["merge_owner"])
    branch = payload["branch"]
    base = payload["base_branch"]
    repo_path = payload["repo_path"]

    # --- seções estruturadas ---
    ac_rows = ref.get("acceptance_hints") or []
    ac_checklist = "\n".join(
        f"- [ ] **{a.split(':')[0]}:** {':'.join(a.split(':')[1:]).strip()}"
        if ":" in a
        else f"- [ ] {a}"
        for a in ac_rows
    )

    ac_verify = ref.get("ac_verification") or []
    if ac_verify:
        verify_lines = ["| AC | Como verificar | Output esperado |", "|----|----------------|-----------------|"]
        for v in ac_verify:
            verify_lines.append(
                f"| {v.get('id', '?')} | `{v.get('command', '')}` | {v.get('expected', '')} |"
            )
        ac_verify_block = "\n".join(verify_lines)
    else:
        ac_verify_block = "_(preencher ac_verification no backlog)_"

    steps = ref.get("implementation_steps") or []
    steps_block = "\n".join(f"{i + 1}. {s}" if not s[0].isdigit() else s for i, s in enumerate(steps)) if steps else "_(ver in_scope + suggested_files)_"

    in_scope = "\n".join(f"- {x}" for x in (ref.get("in_scope") or []))
    out_scope = "\n".join(f"- {x}" for x in (ref.get("out_of_scope") or []))
    files = "\n".join(f"- `{f}`" for f in (ref.get("suggested_files") or []))
    do_not = "\n".join(f"- `{f}`" for f in (ref.get("do_not_touch") or [])) or "- _(nenhum além de out_of_scope)_"

    stop_rules = ref.get("stop_and_redirect") or [
        "Tocar arquivo fora de suggested_files sem AC explícito → comentar issue e redirecionar",
        "Precisar de terraform apply / deploy prod → parar; não executar",
        "Dependência bloqueante não Done → não implementar; comentar blocker",
    ]
    stop_block = "\n".join(f"- {r}" for r in stop_rules)

    state_before = ref.get("state_before") or "_(descrever comportamento/código atual)_"
    state_after = ref.get("state_after") or "_(descrever comportamento/código após merge)_"

    depends = task.get("depends_on")
    dep_block = f"`{depends}` deve estar **Done** antes de iniciar." if depends else "Nenhuma."

    impl_tpl = (conv.get("implementation") or _DEFAULT_IMPL).replace("{agent_role}", agent_role).replace("{reviewer}", reviewer)
    review_tpl = (conv.get("review") or _DEFAULT_REVIEW).replace("{reviewer}", reviewer)

    lines = [
        f"# [{tid}] {task['title']}",
        "",
        "> **Leia secções 0–9 antes de codar.** Não invente paths, endpoints ou AC.",
        "",
        "---",
        "",
        "## 0. Quem faz o quê (não confundir papéis)",
        "",
        *format_phase_table(agent_role, reviewer, handoff, repo, qa),
        "",
        "Fluxo board: ver **Anexo A** (eventos) e sec. 8.",
        *format_agent_responsibilities_section(task, reviewer),
        "",
        "## 1. Identificação",
        "",
        "| Campo | Valor |",
        "|-------|-------|",
        f"| Task ID | `{tid}` |",
        f"| Creator | `{agent_role}` |",
        f"| Reviewer | `{reviewer}` |",
        f"| QA | `qa-gate` |",
        f"| Merge owner | `{handoff['merge_owner']}` |",
        f"| Trilha | `{task.get('track', 'produto')}` |",
        f"| Repo | `{repo}` |",
        f"| Path local | `{repo_path}` |",
        f"| Branch | `{branch}` (base: `{base}`) |",
        f"| Depends on | {dep_block} |",
        "",
        "## 2. Estado atual → estado desejado",
        "",
        "### Antes (não assumir — verificar no repo)",
        "",
        state_before,
        "",
        "### Depois (Definition of Done creator)",
        "",
        state_after,
        "",
        "### Contexto",
        "",
        ref.get("context_summary", ""),
        "",
        ref.get("user_story") and f"**User story:** {ref.get('user_story')}" or "",
        "",
        "### Notas técnicas (factos)",
        "",
        ref.get("technical_notes") or "Ver arquivos sugeridos e AC.",
        *format_user_flow_section(ref, repo, agent_role, tid=tid, qa=qa),
        "",
        "## 3. Escopo rígido",
        "",
        "### Dentro do escopo (só isto)",
        in_scope,
        "",
        "### Fora do escopo",
        out_scope,
        "",
        "### Arquivos permitidos (suggested_files)",
        files,
        "",
        "### Não editar",
        do_not,
        "",
        "### Redirecionamento",
        REDIRECT_TABLE,
        "",
        "## 4. Passo a passo — creator (`{agent_role}`)",
        "",
        "```powershell",
        f"cd {repo_path}",
        f"git fetch origin",
        f"git checkout {base}",
        f"git pull origin {base}",
        f"git checkout -b {branch}",
        "```",
        "",
        steps_block,
        "",
        f"**Antes de `{ev['ready_for_cr']}`:**",
        f"- [ ] Todos os AC verificados localmente (sec. 5)",
        f"- [ ] PR preenchido conforme **Anexo E** (template inline)",
        f"- [ ] Comentário de implementação (sec. 10) na issue",
        f"- [ ] Board → **Ready for Code Review** · `emit_status_event` com `{ev['ready_for_cr']}`",
    ]
    if agent_role == "frontend-mobile":
        lines.append("- [ ] Fluxo sec. 2.1 reproduzido no emulador antes do PR")
    lines += [
        "",
        "## 5. Critérios de aceite + verificação",
        "",
        ac_checklist,
        "",
        ac_verify_block,
        "",
        *format_qa_section(qa, tid, repo),
        "## 7. Parar e pedir ajuda (anti-alucinação)",
        "",
        stop_block,
        "",
        "## 8. Handoff / eventos board",
        "",
        "| De | Para | Evento | Quem dispara |",
        "|----|------|--------|--------------|",
        f"| Todo | In Progress | `{ev['orchestrator_enter']}` | orchestrator |",
        f"| In Progress | Ready for Code Review | `{ev['ready_for_cr']}` | **{agent_role}** |",
        f"| In Code Review | Ready for Test | `{ev['ready_for_test']}` | **{reviewer}** |",
        f"| In Code Review | In Progress | `{ev['return_in_progress']}` | **{reviewer}** |",
        f"| In Test | In Pull Request | `{ev['qa_in_pr']}` | **qa-gate** |",
        f"| In Test | In Progress | `{ev['qa_return']}` | **qa-gate** |",
        f"| In Pull Request | Done | `{ev['merge_done']}` | **{handoff['merge_owner']}** |",
        "",
        "## 9. Payload máquina (`agent-task`)",
        "",
        "```agent-task",
        json.dumps(payload, ensure_ascii=False, indent=2),
        "```",
        "",
        "## 10. Templates de comentário (obrigatório por fase)",
        "",
        "### 10.1 Implementação — `{agent_role}`",
        "```markdown",
        impl_tpl,
        "```",
        "",
        "### 10.2 Code Review — `{reviewer}`",
        "```markdown",
        review_tpl,
        "```",
        "",
        "### 10.3 QA — `qa-gate`",
        "```markdown",
        conv.get("qa") or _DEFAULT_QA,
        "```",
        "",
        "### 10.4 Merge — `{handoff['merge_owner']}`",
        "```markdown",
        conv.get("merge") or _DEFAULT_MERGE,
        "```",
        *format_appendices(task, agent_role, reviewer, handoff, ref, qa, ev),
    ]
    return "\n".join(line for line in lines if line is not None)


_DEFAULT_IMPL = """## [{agent_role}] Implementação

**Status board:** In Progress → Ready for Code Review

### Estratégia de codificação
1. _(decisões técnicas: onde centralizar lógica, helpers, padrões RN)_
2. _(ordem de implementação e trade-offs)_

### O que foi feito
- 

### Arquivos alterados
| Arquivo | Mudança |
|---------|---------|
| | |

### Testes unitários
- [ ] Criados/ajustados em: `path/do/teste.test.ts`
- [ ] Comando: `npm test -- <suite>`
- [ ] Output: exit 0

### Como validar localmente
```

```

### Handoff
PR: 
→ `{reviewer}` via evento role-based v2 (`handoff_expectations.creator_exit_event`)"""

_DEFAULT_REVIEW = """## [{reviewer}] Code Review

**Status board:** In Code Review → Ready for Test (ou In Progress se changes)

### Escopo verificado (implementação do frontend-mobile)
- [ ] Diff alinhado ao comentário sec. 10.1 e escopo sec. 3
- [ ] Estratégia de codificação coerente com o problema
- [ ] Sem secrets / credenciais

### Qualidade de código
| Critério | OK | Notas |
|----------|----|-------|
| Correção / lógica | | |
| Legibilidade / padrões RN | | |
| Escopo (só suggested_files) | | |

### Cobertura de testes unitários
- [ ] Testes cobrem AC e bordas relevantes
- [ ] Assertivas adequadas (não só smoke)
- [ ] `npm test` verde no PR

### Decisão
- [ ] Emitir evento reviewer `{role}_ready_for_test` — segue para qa-gate
- [ ] Emitir evento reviewer `{role}_return_in_progress` — motivo:"""

_DEFAULT_QA = """## [qa-gate] QA

**Status board:** In Test → In Pull Request (ou In Progress se fail)

### Cenários de teste (sec. 6)
| Cenário | Passos | Resultado esperado |
|---------|--------|------------------|
| | | |

### Critérios de aceite
| ID | Critério | Resultado | Evidência |
|----|----------|-----------|-----------|
| AC-01 | | PASS / FAIL | PNG/MP4 abaixo |
| AC-02 | | PASS / FAIL | |

### Comandos executados (MCP guardiao-familia-agents — obrigatório)
```
get_handoff → qa-gate_in_test → query_mobile_flow_rag → qa_db_seed → qa_appium_suite_* → qa_db_cleanup → qa-gate_in_pull_request|qa-gate_return_in_progress
```

### Evidências (anexar mídias)
- Screenshot PNG: 
- Vídeo MP4: 
- JSON report: `agents/00-runtime/output/{task_id}/qa-gate-({N})/evidence/`

### Decisão
- [ ] **`qa-gate_in_pull_request`** — todos AC PASS
- [ ] **`qa-gate_return_in_progress`** — AC falhou:"""

_DEFAULT_MERGE = """## [devops-cicd] Merge

PR merged: 
CI: green
Evento role-based v2: `{ops_role}_done` → Done"""
