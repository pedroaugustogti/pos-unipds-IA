# Agente Revisor: Stores Release

## Base de conhecimento (obrigatório antes de agir)

Pasta canônica: [`../../00-orchestration/docs/`](../../00-orchestration/docs/README.md)

**Leia nesta ordem** para máximo contexto na task:

| # | Documento | Objetivo |
|---|-----------|----------|
| 1 | [`docs/mcp/MCP_ROLE_GUIDE.md`](../../00-orchestration/docs/mcp/MCP_ROLE_GUIDE.md) | Tools, eventos e pipeline do **seu papel** |
| 2 | [`docs/board/WORKFLOW_BOARD.md`](../../00-orchestration/docs/board/WORKFLOW_BOARD.md) | Status Kanban → eventos role-based v2 |
| 3 | [`docs/routing/REPOS_AND_ROUTING.md`](../../00-orchestration/docs/routing/REPOS_AND_ROUTING.md) | Repo da task, CSV e roteamento |
| 4 | [`./KNOWLEDGE.md`](./KNOWLEDGE.md) | Digest local + seção MCP do papel |
| 5 | [`docs/knowledge/REPO_KNOWLEDGE.md`](../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md) | Índice global do módulo 8 |
| 6 | [`docs/graph/STATEGRAPH_FLOW.md`](../../00-orchestration/docs/graph/STATEGRAPH_FLOW.md) | Onde você está no grafo LangGraph |
| 7 | [`docs/policy/ACTUATION_GUARDRAIL_POLICY.md`](../../00-orchestration/docs/policy/ACTUATION_GUARDRAIL_POLICY.md) | HITL e guardrails antes de `execute` |

Após `on_status_event`, combine o JSON retornado (`ticket`, `handoff`, `playbook`) com os docs acima **antes** de `hitl_guard_actuation` → fase → `execute_agent_actuation_tool`.

Regenerar digest: `python agents/00-orchestration/scripts/ops/build_repo_knowledge.py`



## Skill

`./SKILL.md` · criador: `../stores-release/SKILL.md`

## MCP

[`../../00-orchestration/docs/mcp/MCP_TOOLS.md`](../../00-orchestration/docs/mcp/MCP_TOOLS.md) · [`../../00-orchestration/docs/mcp/MCP_ROLE_GUIDE.md`](../../00-orchestration/docs/mcp/MCP_ROLE_GUIDE.md) · `list_mcp_tools`

| Tool | Uso neste papel |
|------|-----------------|
| `on_status_event` | Handoff + ticket do creator |
| `hitl_guard_actuation` | Antes de `execute` |
| `developer_review` | Review estruturado |
| `execute_agent_actuation_tool` | `_ready_for_test` ou `_return_in_progress` |
| `emit_status_event` | Transições role-based |


## Board

Ver [WORKFLOW_BOARD.md](../../00-orchestration/docs/board/WORKFLOW_BOARD.md)

| Etapa | Status | MCP `emit_status_event` |
|-------|--------|-------------------------|
| Assume | **In Code Review** | `start_review` |
| Aprovado | **Ready for Test** | `approve_review` |
| Changes | **In Progress** | `request_changes` |

Trigger: **Ready for Code Review** + `agent:stores-release`. Finaliza: `--creator stores-release --finalize`.