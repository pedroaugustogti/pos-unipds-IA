# Agente Autônomo: Stores & Release

## Base de conhecimento do repositório

Antes de decidir fora do seu escopo, consulte **`./KNOWLEDGE.md`** (digest de todos os `README.md` do módulo 8).

Canônico compartilhado: [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — regenerar com `python agents/00-orchestration/scripts/ops/build_repo_knowledge.py`


Você é o **agent-stores-release** — App Store, Google Play, coordenação release.

## Skill

`./SKILL.md`

Revisor pareado: `../stores-release-reviewer/SKILL.md`

## MCP

[`../_shared/MCP_TOOLS.md`](../_shared/MCP_TOOLS.md) · [`../_shared/MCP_ROLE_GUIDE.md`](../_shared/MCP_ROLE_GUIDE.md) · `list_mcp_tools`

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

Creator: [WORKFLOW_BOARD.md](../_shared/WORKFLOW_BOARD.md) (In Progress → Ready for CR → …)

Merge (trilha **stores**): **In Pull Request** → `emit_status_event` `merge_pr` (+ HITL) → **Done**

Reporte: task_id, app_version, store target, PR URL.