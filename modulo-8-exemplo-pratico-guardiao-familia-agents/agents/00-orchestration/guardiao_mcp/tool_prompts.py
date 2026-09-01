"""Prompts MCP para orientar a LLM — descrições objetivas por tool (LangGraph v2)."""

SERVER_INSTRUCTIONS = """\
Servidor MCP do Guardião Família (módulo 8) — **14 tools** usadas pelo LangGraph v2 e pelo Cursor.

## LangGraph v2 (automação)
Grafo: `sync_board` → `orchestrator_decide` → 55 nós `evt_*` (`event_registry.py`).
Cada nó executa um pipeline MCP em sequência via `lib/mcp_invoke`.
CLI: `scripts/langgraph/langgraph_run.py --task T-XXX --mode dry_run`.

## Uso manual (Cursor)
Fora do grafo, use **somente** tools deste servidor (`list_mcp_tools`).

## Pipeline MCP por evento
| Situação | Tools (ordem) |
|----------|----------------|
| Todo → claim | `orchestrator_enter_in_progress` |
| orchestrator_todo | `emit_status_event` |
| Demais eventos | `on_status_event` → `hitl_guard_actuation` → fase? → `execute_agent_actuation_tool` |

**Fase opcional:** `developer_implement` (creator/In Progress) · `developer_review` (reviewer) · `qa_validate` (qa-gate/In Test)

## Regras obrigatórias
1. **Status:** altere SOMENTE com `emit_status_event` (eventos role-based). Catálogo: `list_status_events`.
2. **dry_run:** true (padrão) simula; false só com handoff/AC validados.
3. **HITL:** antes de cada `execute_agent_actuation_tool`, chame `hitl_guard_actuation` e use `guard_pass_id`.
4. **Fase explícita:** prefira chamar `developer_*` / `qa_validate` antes de `execute`; passe o JSON em `phase_work` para evitar reexecução.

## Anti-padrões
- Pular `on_status_event` — perde ticket, skill, handoff e playbook.
- Pular `hitl_guard_actuation` — `execute` rejeita sem `guard_pass_id`.
- Eventos legados (`claim`, `open_pr`, `test_passed`) — use `{agent_role}_{status_slug}`.
- Appium fora de `qa_validate` sem seguir a ordem da seção QA mobile.

## Fluxo manual por papel
| Papel | Sequência |
|-------|-----------|
| creator | `on_status_event` → `hitl_guard` → `developer_implement` → `execute` |
| reviewer | `on_status_event` → `hitl_guard` → `developer_review` → `execute` |
| qa-gate | `on_status_event` → `hitl_guard` → `qa_validate` → `execute` |
| ops/devops | `on_status_event` → `hitl_guard` → `execute` |
| orchestrator | `orchestrator_enter_in_progress` (Todo) ou deixar o grafo v2 decidir |

## QA mobile (ordem obrigatória)
1. **task_id = ticket em execução** — não reutilize entre execuções paralelas sem `qa_db_cleanup`.
2. **Seed (`qa_db_seed`)** — somente quando a massa deve vir da API:
   - Conta/família/filho já no Postgres → `qa_db_seed` + suite com `from_db_seed=true`.
   - AC exige cadastro/família **na UI parent** → **não** chame seed; use `qa_appium_suite_parent` com `feature=create_account` ou `config_family`.
   - Validação **somente no child** → seed parent + `qa_appium_suite_child(from_db_seed=true, child_only=true)`.
3. Suite conforme app alvo e flags (`child_only`, `parent_only`, `feature`, `from_db_seed`).
4. Evidências → `agents/00-runtime/output/{task_id}/qa-gate-({cycle})/evidence/`.
5. `qa_db_cleanup(task_id, dry_run=false)` após evidências.
6. Próximo status via `emit_status_event` role-based (ex: `qa-gate_in_pull_request` ou `qa-gate_return_in_progress`).

Catálogo: `list_mcp_tools` · `agents/_shared/MCP_TOOLS.md` · grafo: `agents/00-orchestration/docs/STATEGRAPH_FLOW.md`.
"""

# --- Gateway / HITL ---

EMIT_STATUS_EVENT = """\
**Quando:** mover task no board Kanban (única porta de status).

**Faz:** valida evento role-based → transição de status → atualiza board GitHub → opcionalmente handoff.

**Formato:**
- Avanço: `{agent_role}_{status_slug}` — ex: `frontend-mobile_in_progress`
- Retrocesso: `{agent_role}_return_{status_slug}` — ex: `frontend-mobile-reviewer_return_in_progress`

**Alternativa:** `agent_role` + `board_status` (+ `return_event=true` para retrocesso).

**Parâmetros:**
- task_id: ID da task (ex: T-P3-009)
- event: string role-based (opcional se usar agent_role + board_status)
- agent_role + board_status: montam o evento automaticamente
- return_event: true para retrocesso
- summary: motivo (obrigatório em produção)
- dry_run: true (padrão) simula; false aplica
- pr_url: URL do PR (`{creator}_ready_for_code_review`)
- from_agent: papel emissor — deve bater com o prefixo do evento

**Catálogo:** `list_status_events` · **Antes de dry_run=false:** confirme handoff, AC e papel.
"""

LIST_STATUS_EVENTS = """\
**Quando:** consultar os 55 eventos role-based antes de `emit_status_event`.

**Faz:** retorna catálogo com event, agent_role, board_status, kind (advance|return), classification.

**Filtros:** agent_role, classification (creator|reviewer|qa-gate|ops|orchestrator).
"""

ON_STATUS_EVENT = """\
**Quando:** após `emit_status_event` ou antes de atuar (status já atualizado).

**Faz:**
1. Resolve evento role-based
2. Identifica `acting_agent` e `assigned_agent`
3. Lê ticket no board (GitHub Project → fallback JSON)
4. Extrai `ticket` por papel: AC, escopo, arquivos, QA, merge, user_flow
5. Anexa `handoff`, `ci`, `model_tier`, `playbook` (skill, passos ReAct)

**Parâmetros:** task_id + event **ou** agent_role + board_status (+ return_event).

**Retorno:** `assigned_agent`, `target_status`, `ticket`, `playbook`, `handoff`.

**Não altera board** — somente leitura/contexto. Handoff canônico: `agents/00-runtime/output/{task_id}/handoff.json`.
"""

HITL_GUARD_ACTUATION = """\
**Quando:** obrigatório **antes de cada** `execute_agent_actuation_tool`.

**Entrada:** `actuation_context` = JSON de `on_status_event`.

**Faz:**
1. Carrega `agents/_shared/ACTUATION_GUARDRAIL_POLICY.md`
2. Analisa ticket, handoff e playbook (injection, alto risco, merge live)
3. Decide `proceed` ou `blocked` + `importance_score`
4. Se blocked: enfileira HITL e comenta na issue (`dry_run=false`)
5. Se proceed: retorna `guard_pass_id` (uso único, TTL 1h)

**Parâmetros:** actuation_context (obrigatório), mode, human_clearance, clearance_note, dry_run.

**Após bloqueio:** triagem humana → `hitl_guard_actuation(human_clearance=true)` → novo `guard_pass_id`.
"""

EXECUTE_AGENT_ACTUATION = """\
**Quando:** após `hitl_guard_actuation` com `proceed=true`.

**Entrada:** `actuation_context` + `guard_pass_id` (obrigatório).

**Faz:**
1. Identifica fase pelo `target_status`
2. Marca `assigned_agent` busy → executa fase (ou usa `phase_work`) → emite próximo evento role-based → idle

**Cursor (manual):** chame `developer_implement` | `developer_review` | `qa_validate` antes; passe o JSON retornado em `phase_work` para `execute` não reexecutar a fase.

**Mapeamento target_status → fase → emit típico:**
| target_status | fase | emit seguinte (exemplo) |
|---------------|------|-------------------------|
| In Progress | implement | `{creator}_ready_for_code_review` |
| Ready for Code Review | start_review | `{reviewer}_in_code_review` |
| In Code Review | review | `{reviewer}_ready_for_test` ou `_return_in_progress` |
| Ready for Test | start_test | `qa-gate_in_test` |
| In Test | qa | `qa-gate_in_pull_request` ou `_return_in_progress` |
| In Pull Request | merge | `devops-cicd_done` (HITL em live) |

**Parâmetros:**
- actuation_context, guard_pass_id (obrigatórios)
- phase_work: JSON opcional de developer_* / qa_validate
- mode: dry_run | live
- use_role_events: true (padrão) emite eventos role-based

**Retorno:** phase, emit_event, board_status_out, work, apply.gateway

**LangGraph v2:** o grafo chama este pipeline automaticamente em cada nó `evt_*`.
"""

DEVELOPER_IMPLEMENT = """\
**Quando:** fase **implement** (`target_status=In Progress`), após `hitl_guard_actuation`.

**Entrada:** `actuation_context` = JSON de `on_status_event`.

**Faz:** skill + agent.md → `execution_plan` (LLM) → implementação → `changed_files`, `unit_tests`.

**Retorno:** `execution_plan`, `changed_files`, `unit_tests`, `decision.next_event` (ex: `{creator}_ready_for_code_review`).
"""

DEVELOPER_REVIEW = """\
**Quando:** fase **review** (`target_status=In Code Review`), após `hitl_guard_actuation`.

**Entrada:** `actuation_context` com handoff/PR.

**Faz:** review estruturado — arquitetura, manutenibilidade, testes.

**Retorno:** `review`, `findings`, `verdict`, `decision` (`{reviewer}_ready_for_test` | `_return_in_progress`).
"""

QA_VALIDATE = """\
**Quando:** fase **qa** (`target_status=In Test`), após `hitl_guard_actuation`.

**Entrada:** `actuation_context` com AC e config QA.

**Faz:**
1. Orquestra MCP: `qa_db_seed` → `qa_appium_suite_*` → `qa_db_cleanup` (quando aplicável)
2. Coleta evidências e valida AC (`ac_validation`)

**Retorno:** `mcp_steps`, `evidence_paths`, `ac_validation`, `decision` (`qa-gate_in_pull_request` | `qa-gate_return_in_progress`).
"""

# --- Orchestrator ---

ORCHESTRATOR_ENTER_IN_PROGRESS = """\
**Quando:** grafo v2 em Todo ou orchestrator manual iniciando ciclo.

**Faz:**
1. Seleciona task **Todo** (menor `priority_rank`; bonus sprint atual)
2. Emite `orchestrator_enter_in_progress` via gateway (`from_agent=orchestrator`)
3. Status alvo: **In Progress** · creator = `agent_role` da task

**Parâmetros:** sprint, sprint_only, task_id (opcional), summary, dry_run.

**LangGraph v2:** nó `evt_orchestrator_enter_in_progress` executa só esta tool.
**Manual:** próximo passo típico — `on_status_event` → pipeline da fase creator.
"""

# --- QA mobile ---

QA_DB_SEED = """\
**Quando:** massa de teste via API (Postgres) **sem** cadastro/família na UI.

**Importante:** profiles criam parent via `POST /auth/register` — nunca insira usuários direto no Postgres.

**Não use quando:** AC exige telas de cadastro/família no app parent — use `qa_appium_suite_parent` com `feature` adequado.

**Faz:** bootstrap API → HTTP (família, filho, pairing-code) → `stage-handoff.json` → cache em `output/{task_id}/seed-cache.json`.

**Profiles:** pairing_warm | basic_parent | parent_home | child_home | permissions_resume

**Child-only:** seed parent + `qa_appium_suite_child(from_db_seed=true, child_only=true)` — não boota parent 5554.

**Parâmetros:** task_id (obrigatório), profile, use_task_config, bootstrap_api, dry_run.

**Próximo:** suite Appium com `from_db_seed=true` e mesmo `task_id`.
"""

QA_DB_CLEANUP = """\
**Quando:** APÓS capturar evidências QA.

**Faz:** purge Postgres + reset stage-handoff + remove cache seed.

**Parâmetros:** task_id (preferido) | handoff_path | parent_email · dry_run.
"""

QA_APPIUM_SCENARIOS = """\
## Como escolher seed + suite

| Objetivo | Seed? | Tool | Flags |
|----------|-------|------|-------|
| Cadastro/família **na UI parent** | Não | `qa_appium_suite_parent` | `feature=create_account` ou `config_family` |
| Login→home com massa no DB | Sim `parent_home` | `qa_appium_suite_parent` | `from_db_seed=true`, `task_id` |
| AC no **app child** | Sim `basic_parent`/`parent_home` | `qa_appium_suite_child` | `from_db_seed=true`, **`child_only=true`** |
| Pairing dual | Sim `child_home` | `qa_appium_suite_child` | `child_only=false`, `feature=pairing` |
| Child pareado (permissões+home) | Sim `permissions_resume` | `qa_appium_suite_child` | `from_db_seed=true` |

**Infra:** parent=5554/8082 · child=5556/9090 · `phase=All` · `reset_handoff_after=true` (padrão com seed).
**Evidências:** `output/{task_id}/qa-gate-({N})/evidence/` · cite paths no `emit_status_event` role-based.
**Cleanup:** `qa_db_cleanup(task_id)` antes de outro ticket.
"""

QA_APPIUM_SUITE_PARENT = """\
**Quando:** validar app **parent** (emulator-5554, Metro 8082).

**Sem seed (UI cadastro/família):**
```
qa_appium_suite_parent(feature="create_account", skip_appium=false, dry_run=false)
```

**Com seed (login→home):**
```
qa_db_seed(task_id="T-XXX", profile="parent_home", dry_run=false)
qa_appium_suite_parent(from_db_seed=true, task_id="T-XXX", feature="login", skip_appium=false, dry_run=false)
```

**Parâmetros:** phase, feature, from_db_seed, task_id, parent_only, reset_handoff_after, skip_build, skip_appium, timeout_sec, dry_run.

---
""" + QA_APPIUM_SCENARIOS

QA_APPIUM_SUITE_CHILD = """\
**Quando:** validar app **child** (emulator-5556, Metro 9090).

**Child-only (massa parent no DB):**
```
qa_db_seed(task_id="T-XXX", profile="child_home", dry_run=false)
qa_appium_suite_child(from_db_seed=true, task_id="T-XXX", child_only=true, skip_appium=false, dry_run=false)
```

**Pairing dual:**
```
qa_appium_suite_child(from_db_seed=true, task_id="T-XXX", child_only=false, feature="pairing", skip_appium=false, dry_run=false)
```

**Parâmetros:** child_only, from_db_seed, task_id, feature, phase, reset_handoff_after, skip_build, skip_appium, timeout_sec, dry_run.

**Próximo:** evidências → `qa_db_cleanup` → `emit_status_event` (`qa-gate_in_pull_request` ou retrocesso).

---
""" + QA_APPIUM_SCENARIOS

LIST_MCP_TOOLS = """\
**Quando:** início de sessão ou dúvida sobre catálogo.

**Faz:** lista as 14 tools (gateway, phase, orchestrator, qa_mobile, meta) e flag writes.

**Grupos v2:** gateway (5) · phase (3) · orchestrator (1) · qa_mobile (4) · meta (1).
"""
