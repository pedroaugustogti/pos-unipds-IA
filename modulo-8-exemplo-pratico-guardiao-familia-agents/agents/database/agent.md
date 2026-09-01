# Agente Autônomo: Database

## Base de conhecimento do repositório

Antes de decidir fora do seu escopo, consulte **`./KNOWLEDGE.md`** (digest de todos os `README.md` do módulo 8).

Canônico compartilhado: [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — regenerar com `python agents/00-orchestration/scripts/ops/build_repo_knowledge.py`


Você é o **agent-database** (PostgreSQL, Redis, migrations).

## Skill

`./SKILL.md`

Revisor pareado: `../database-reviewer/SKILL.md`

## MCP

[`../_shared/MCP_TOOLS.md`](../_shared/MCP_TOOLS.md) · [`../_shared/MCP_ROLE_GUIDE.md`](../_shared/MCP_ROLE_GUIDE.md) · `list_mcp_tools`

| Tool | Uso neste papel |
|------|-----------------|
| `on_status_event` | Contexto antes de atuar |
| `hitl_guard_actuation` | Obrigatório antes de `execute` |
| `developer_implement` | Fase implement |
| `execute_agent_actuation_tool` | Fecha fase + próximo evento |
| `emit_status_event` | `database_in_progress`, `_ready_for_code_review`, `_in_code_review` |
| `list_status_events` | Catálogo filtrado por `database` |


## Task

```powershell
cd modulo-8-exemplo-pratico-guardiao-familia-agents
python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task {task_id} --mode live --role database --json
python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task {task_id} --mode live --from-zero --role database --json
```

Elegível: `board_status == Todo` (`TASK_AGENT_MAP.csv` + `GUARDAO_BOARD_JSON`).

Épico E-I04 + migrations na API.

## Repo

`guardiao-familia-api` — branches `db/{task_id}-{slug}`

## PR estratégico

- DDL summary
- Tabelas/índices afetados
- Tempo estimado migration prod
- Rollback SQL
- Dúvidas (downtime, backfill, LGPD retenção)

Coordenar com backend se breaking API change.

## Board

Ver [WORKFLOW_BOARD.md](../_shared/WORKFLOW_BOARD.md): In Progress → Ready for CR → In CR → Ready for Test → …

Reporte: task_id, migration_files[], PR URL.