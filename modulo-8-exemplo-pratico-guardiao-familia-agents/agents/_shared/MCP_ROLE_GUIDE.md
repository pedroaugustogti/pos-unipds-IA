# MCP por papel — Guardião Família v2

Servidor: `guardiao_mcp` · 14 tools · [`MCP_TOOLS.md`](MCP_TOOLS.md) · `list_mcp_tools`

## Pipeline comum (manual ou via LangGraph v2)

```
on_status_event → hitl_guard_actuation → [fase] → execute_agent_actuation_tool
```

| Tool | Grupo | Função |
|------|-------|--------|
| `list_status_events` | gateway | Catálogo dos 55 eventos role-based |
| `emit_status_event` | gateway | **Única porta** de mudança de status |
| `on_status_event` | gateway | Contexto: ticket, handoff, playbook, assigned_agent |
| `hitl_guard_actuation` | gateway | Guardrail HITL → `guard_pass_id` |
| `execute_agent_actuation_tool` | gateway | Fecha fase + emite próximo evento |
| `developer_implement` | phase | Plano + implementação (creator) |
| `developer_review` | phase | Review estruturado (reviewer) |
| `qa_validate` | phase | QA + evidências (qa-gate) |
| `orchestrator_enter_in_progress` | orchestrator | Claim Todo → In Progress |
| `qa_db_seed` / `qa_db_cleanup` | qa_mobile | Massa Postgres + cleanup |
| `qa_appium_suite_parent` / `_child` | qa_mobile | Suites Appium |

**Regras:** `dry_run=true` por padrão · sem eventos legados (`claim`, `open_pr`, `test_passed`) · handoff em `agents/00-runtime/output/{task_id}/handoff.json`

---

## Creator (`classification: creator`)

Papéis: `backend`, `frontend-mobile`, `frontend-web`, `cloud-infra`, `database`, `devops-cicd`, `qa-author`, `stores-release`

**Tools:** `on_status_event` → `hitl_guard_actuation` → `developer_implement` → `execute_agent_actuation_tool` (+ `emit_status_event` se orquestrar manualmente)

**Eventos** (substitua `{role}` pelo seu papel):

| Status alvo | Evento |
|-------------|--------|
| In Progress | `{role}_in_progress` |
| Ready for Code Review | `{role}_ready_for_code_review` (`pr_url` obrigatório) |
| In Code Review | `{role}_in_code_review` |

**Dica:** passe o JSON de `developer_implement` em `phase_work` do `execute` para não reexecutar a fase.

---

## Reviewer (`classification: reviewer`)

Papéis: `{creator}-reviewer` (ex: `backend-reviewer`, `frontend-mobile-reviewer`)

**Tools:** `on_status_event` → `hitl_guard_actuation` → `developer_review` → `execute_agent_actuation_tool`

**Eventos** (substitua `{reviewer}`):

| Status alvo | Evento | Intenção |
|-------------|--------|----------|
| In Code Review | `{reviewer}_in_code_review` | Iniciar review |
| Ready for Test | `{reviewer}_ready_for_test` | Aprovar |
| In Progress | `{reviewer}_return_in_progress` | Pedir mudanças |

Leia handoff + PR antes de `developer_review`.

---

## QA-Gate (`classification: qa-gate`)

Papel: `qa-gate`

**Tools:** `on_status_event` → `hitl_guard_actuation` → `qa_validate` → `execute_agent_actuation_tool`  
**QA mobile (dentro de `qa_validate` ou manual):** `qa_db_seed` → `qa_appium_suite_*` → `qa_db_cleanup`

**Eventos:**

| Status alvo | Evento |
|-------------|--------|
| In Test | `qa-gate_in_test` |
| In Pull Request | `qa-gate_in_pull_request` |
| In Progress | `qa-gate_return_in_progress` |

**Child-only:** `qa_db_seed(profile=basic_parent)` + `qa_appium_suite_child(child_only=true, from_db_seed=true)`.

---

## Ops / merge (`classification: ops`)

Papéis: `devops-cicd`, `stores-release` (fase **In Pull Request** → **Done**)

**Tools:** `on_status_event` → `hitl_guard_actuation` → `execute_agent_actuation_tool` (sem fase LLM)

**Evento:** `{ops}_done` (ex: `devops-cicd_done`, `stores-release_done`)

HITL obrigatório em `mode=live` para merge.

---

## Orchestrator

Tool: `orchestrator_enter_in_progress` — seleciona task Todo e move para In Progress.

No LangGraph v2 o nó `evt_orchestrator_enter_in_progress` executa automaticamente.
