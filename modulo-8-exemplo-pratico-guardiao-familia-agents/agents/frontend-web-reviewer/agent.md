# Agente Revisor: Frontend Web

## Base de conhecimento do repositório

Antes de decidir fora do seu escopo, consulte **`./KNOWLEDGE.md`** (digest de todos os `README.md` do módulo 8).

Canônico compartilhado: [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — regenerar com `python agents/00-orchestration/scripts/ops/build_repo_knowledge.py`


**frontend-web-reviewer** — par de `frontend-web`.

## Skill

`./SKILL.md` · criador: `../frontend-web/SKILL.md`

## MCP

[`../_shared/MCP_TOOLS.md`](../_shared/MCP_TOOLS.md) · [`../_shared/MCP_ROLE_GUIDE.md`](../_shared/MCP_ROLE_GUIDE.md) · `list_mcp_tools`

| Tool | Uso neste papel |
|------|-----------------|
| `on_status_event` | Handoff + ticket do creator |
| `hitl_guard_actuation` | Antes de `execute` |
| `developer_review` | Review estruturado |
| `execute_agent_actuation_tool` | `_ready_for_test` ou `_return_in_progress` |
| `emit_status_event` | Transições role-based |


## Board

Ver [WORKFLOW_BOARD.md](../_shared/WORKFLOW_BOARD.md)

| Etapa | Status | MCP `emit_status_event` |
|-------|--------|-------------------------|
| Assume | **In Code Review** | `start_review` |
| Aprovado | **Ready for Test** | `approve_review` |
| Changes | **In Progress** | `request_changes` |

Creator corrige → `resubmit_review` → **In Code Review**

Trigger: **Ready for Code Review** + `agent:frontend-web`. Finaliza: `--creator frontend-web --finalize`.