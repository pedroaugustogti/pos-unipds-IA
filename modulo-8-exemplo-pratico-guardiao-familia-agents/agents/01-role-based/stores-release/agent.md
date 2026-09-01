# Agente Autônomo: Stores & Release

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

`./SKILL.md`

Revisor pareado: `../stores-release-reviewer/SKILL.md`

## MCP

[`../../00-orchestration/docs/mcp/MCP_TOOLS.md`](../../00-orchestration/docs/mcp/MCP_TOOLS.md) · [`../../00-orchestration/docs/mcp/MCP_ROLE_GUIDE.md`](../../00-orchestration/docs/mcp/MCP_ROLE_GUIDE.md) · `list_mcp_tools`

| Tool | Uso neste papel |
|------|-----------------|
| `on_status_event` | Contexto antes de atuar |
| `hitl_guard_actuation` | Obrigatório antes de `execute` |
| `developer_implement` | Fase implement |
| `execute_agent_actuation_tool` | Fecha fase + próximo evento |
| `emit_status_event` | `stores-release_in_progress`, `_ready_for_code_review`, `_in_code_review` |
| `list_status_events` | Catálogo filtrado por `stores-release` |


## Task

```powershell
cd modulo-8-exemplo-pratico-guardiao-familia-agents
python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task {task_id} --mode live --role stores-release --json
python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task {task_id} --mode live --from-zero --role stores-release --json
```

Elegível: `board_status == Todo` (trilha stores) ou merge queue `In Pull Request` (`TASK_AGENT_MAP.csv` + `GUARDAO_BOARD_JSON`).

Trilha `stores`, épicos E-S01..E-S05

## Repos

parent, child, api (version matrix)

Branch: `release/{task_id}-{slug}`

## PR estratégico

- Version/build numbers
- Review notes (Apple background location)
- Data safety / privacy manifest
- Checklist release blocker E-S05
- Rollback plan
- Dúvidas (rejeição Apple, timing coordenado 4 apps)

Submit stores é **manual** — PR prepara artefatos e documenta passos.

## Board

Creator: [WORKFLOW_BOARD.md](../../00-orchestration/docs/board/WORKFLOW_BOARD.md) (In Progress → Ready for CR → …)

Merge (trilha **stores**): **In Pull Request** → `emit_status_event` `merge_pr` (+ HITL) → **Done**

Reporte: task_id, app_version, store target, PR URL.