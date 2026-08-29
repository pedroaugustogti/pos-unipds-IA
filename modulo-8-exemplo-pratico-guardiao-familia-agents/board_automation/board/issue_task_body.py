"""Monta corpo de issue GitHub rico — evita alucinação e perda de contexto entre agentes."""

from __future__ import annotations

import json
from typing import Any

from lib.core.agent_paths import agent_prompt_path, skill_path
from lib.paths import MODULE_ROOT
from board_automation.board.reviewer_pairs import reviewer_for

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
| Escrever specs de teste | `qa` |
| Submit stores | `stores-release` |"""


def _reviewer(agent_role: str) -> str:
    return reviewer_for(agent_role) or f"{agent_role}-reviewer"


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


def format_user_flow_section(ref: dict[str, Any], repo: str, agent_role: str) -> list[str]:
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

    mermaid_block = f"```mermaid\n{mermaid}\n```" if mermaid else "_diagrama opcional — ver MOBILE_USER_FLOW_TEMPLATE.md_"

    qa_steps = uf.get("qa_repro_steps") or []
    qa_block = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(qa_steps)) if qa_steps else "1. Seguir tabela acima no emulador\n2. Screenshot/vídeo no elemento alvo"

    return [
        "",
        "## 2.1 Fluxo do usuário até a funcionalidade *(frontend-mobile — obrigatório)*",
        db_note,
        "",
        "> Regra: [`MOBILE_USER_FLOW_TEMPLATE.md`](board_automation/templates/MOBILE_USER_FLOW_TEMPLATE.md). Creator e qa-gate **seguem estes passos**.",
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
        "### Reproduzir (QA / Appium)",
        qa_block,
        "",
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
        "### DB seed (evidências Appium — opcional)",
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
        f"Profiles: {profiles_doc}",
        "",
        "**Dependências:** Docker (Postgres/Redis/API) · `guardiao-familia-mobile-setup` · emuladores 5554/5556 · `psycopg` (purge script)",
        "",
        "```powershell",
        f"python agents/qa-gate/scripts/mobile_e2e_seed.py --task {task_id} --profile {profile}",
        f"python agents/qa-gate/scripts/qa_mobile_evidence.py --task {task_id} --feature pairing --mode cycle --record-video",
        "```",
        "",
    ]


def build_agent_payload(task: dict[str, Any]) -> dict[str, Any]:
    ref = task.get("refinement") or {}
    qa = task.get("qa") or {}
    tid = task["id"]
    agent_role = task["agent_role"]
    repo = task["repo"]
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
            "creator_exit_event": "open_pr",
            "reviewer_exit_event": "approve_review",
            "qa_exit_event": "test_passed",
            "merge_owner": "stores-release" if task.get("track") == "stores" else "devops-cicd",
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

    ev = qa.get("evidence") or {}
    ev_list = [k.replace("_", " ") for k, v in ev.items() if v] or ["json report"]

    skill = f"`{MODULE8}/{skill_path(agent_role).relative_to(MODULE_ROOT).as_posix()}`"
    agent_md = f"`{MODULE8}/{agent_prompt_path(agent_role).relative_to(MODULE_ROOT).as_posix()}`"
    reviewer_skill = f"`{MODULE8}/{skill_path(reviewer).relative_to(MODULE_ROOT).as_posix()}`"

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
        "| Fase | Board Status | Agente | Skill | Proibido nesta fase |",
        "|------|--------------|--------|-------|---------------------|",
        f"| Claim | Todo → In Progress | **{agent_role}** (creator) | {skill} | Review próprio código |",
        f"| Implementar | In Progress | **{agent_role}** | {agent_md} | Merge, alterar fora do escopo |",
        f"| Review | In Code Review | **{reviewer}** | {reviewer_skill} | Implementar features novas |",
        "| QA | In Test | **qa-gate** | `agents/qa-gate/SKILL.md` | Merge PR |",
        f"| Merge | In Pull Request | **{handoff['merge_owner']}** | agent correspondente | Alterar código da feature |",
        "",
        f"Fluxo: [`STATEGRAPH_FLOW.md`](https://github.com/guardiaofamilia/pos-unipds-IA/blob/main/{MODULE8}/agents/_shared/STATEGRAPH_FLOW.md)",
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
        *format_user_flow_section(ref, repo, agent_role),
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
        "**Antes de `open_pr`:**",
        f"- [ ] Todos os AC verificados localmente (sec. 5)",
        f"- [ ] PR preenchido com `docs/templates/PR_TEMPLATE.md`",
        f"- [ ] Comentário de implementação (sec. 10) na issue",
        f"- [ ] Board → **Ready for Code Review** · evento open_pr",
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
        "## 6. QA (qa-gate)",
        "",
        f"| Campo | Valor |",
        f"|-------|-------|",
        f"| test_suite | `{qa.get('test_suite', 'qa-custom')}` |",
        f"| Cenários | {', '.join(qa.get('scenarios') or [])} |",
        f"| Evidências obrigatórias | {', '.join(ev_list)} |",
        "",
        *format_db_seed_section(qa, tid),
        "**Comando principal:**",
        "```powershell",
        qa.get("how_to_run", ""),
        "```",
        "",
        "**Regra:** se qualquer AC = FAIL → `test_failed_bug` + comentário qa-gate (sec. 10). Não merge.",
        "",
        "## 7. Parar e pedir ajuda (anti-alucinação)",
        "",
        stop_block,
        "",
        "## 8. Handoff / eventos board",
        "",
        "| De | Para | Evento | Quem dispara |",
        "|----|------|--------|--------------|",
        f"| Todo | In Progress | `claim` | orchestrator / creator |",
        f"| In Progress | Ready for Code Review | `open_pr` | **{agent_role}** |",
        f"| In Code Review | Ready for Test | `approve_review` | **{reviewer}** |",
        f"| In Code Review | In Progress | `request_changes` | **{reviewer}** |",
        f"| In Test | In Pull Request | `test_passed` | **qa-gate** |",
        f"| In Test | In Progress | `test_failed_bug` | **qa-gate** |",
        f"| In Pull Request | Done | `merge_pr` | **{handoff['merge_owner']}** |",
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
    ]
    return "\n".join(line for line in lines if line is not None)


_DEFAULT_IMPL = """## [{agent_role}] Implementação

**Board:** In Progress → Ready for Code Review

### O que foi feito
- 

### Arquivos alterados
| Arquivo | Mudança |
|---------|---------|
| | |

### AC verificados (local)
- [ ] AC-01: 
- [ ] AC-02: 

### Comando / output
```
```

### Handoff
PR: 
→ `{reviewer}` · evento `open_pr`"""

_DEFAULT_REVIEW = """## [{reviewer}] Code Review

**Board:** In Code Review → Ready for Test (ou In Progress se changes)

### Checklist
- [ ] Só arquivos de suggested_files alterados
- [ ] AC cobertos pelo diff
- [ ] Sem secrets

| Critério | OK | Notas |
|----------|----|-------|
| Correção | | |
| Escopo | | |

**Decisão:** approve_review / request_changes — motivo:"""

_DEFAULT_QA = """## [qa-gate] QA

**Board:** In Test → In Pull Request (ou In Progress se fail)

| AC | Resultado | Evidência |
|----|-----------|-----------|
| AC-01 | PASS/FAIL | |

### Comandos
```

```

### Evidências
(screenshot / vídeo / JSON)

**Decisão:** test_passed / test_failed_bug"""

_DEFAULT_MERGE = """## [devops-cicd] Merge

PR merged: 
CI: green
Evento: merge_pr → Done"""
