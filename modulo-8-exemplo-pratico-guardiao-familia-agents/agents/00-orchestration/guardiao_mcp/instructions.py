"""Instruções globais do servidor MCP."""

SERVER_INSTRUCTIONS = """\
Servidor MCP do Guardião Família (módulo 8) — **14 tools** usadas pelo LangGraph v2 e pelo Cursor.

## LangGraph v2 (automação)
Grafo: `sync_board` → `orchestrator_decide` → 55 nós `evt_*` (`langgraph_app/registry/`).
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
