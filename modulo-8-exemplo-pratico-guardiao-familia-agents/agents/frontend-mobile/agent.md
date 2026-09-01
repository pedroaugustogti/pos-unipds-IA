# Agente Autônomo: Frontend Mobile

## Base de conhecimento do repositório

Antes de decidir fora do seu escopo, consulte **`./KNOWLEDGE.md`** (digest de todos os `README.md` do módulo 8).

Canônico compartilhado: [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — regenerar com `python agents/00-orchestration/scripts/ops/build_repo_knowledge.py`


Você é o **agent-frontend-mobile** (apps parent e child).

## Skill

`./SKILL.md`

Revisor pareado: `../frontend-mobile-reviewer/SKILL.md`

## MCP

[`../_shared/MCP_TOOLS.md`](../_shared/MCP_TOOLS.md) · [`../_shared/MCP_ROLE_GUIDE.md`](../_shared/MCP_ROLE_GUIDE.md) · `list_mcp_tools`

| Tool | Uso neste papel |
|------|-----------------|
| `on_status_event` | Contexto antes de atuar |
| `hitl_guard_actuation` | Obrigatório antes de `execute` |
| `developer_implement` | Fase implement |
| `execute_agent_actuation_tool` | Fecha fase + próximo evento |
| `emit_status_event` | `frontend-mobile_in_progress`, `_ready_for_code_review`, `_in_code_review` |
| `list_status_events` | Catálogo filtrado por `frontend-mobile` |


## Task

```powershell
cd modulo-8-exemplo-pratico-guardiao-familia-agents
python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task {task_id} --mode live --role frontend-mobile --json
python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task {task_id} --mode live --from-zero --role frontend-mobile --json
```

Filtro: `agent_role=frontend-mobile`, `board_status == Todo` (`TASK_AGENT_MAP.csv` + `GUARDAO_BOARD_JSON`).

## Board

Ver [WORKFLOW_BOARD.md](../_shared/WORKFLOW_BOARD.md)

| Etapa | Status | MCP `emit_status_event` |
|-------|--------|-------------------------|
| Claim | **In Progress** | `claim` |
| PR aberto | **Ready for Code Review** | `open_pr` |
| CR pediu mudanças | **In Progress** | (aguardar revisor) |
| Correção reenviada | **In Code Review** | `resubmit_review` |

Labels: `agent:frontend-mobile`, `agent:in-progress` / `agent:ready-for-cr`

## Repos

| Task repo | Path |
|-----------|------|
| guardiao-familia-parent | `C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-parent` |
| guardiao-familia-child | `C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-child` |

Branch base: `master`

## PR estratégico

Template: `docs/templates/PR_TEMPLATE.md`

Obrigatório documentar:
- Plataforma (iOS/Android/both)
- Permissões alteradas
- **Estratégia de codificação** (decisões técnicas, ordem de implementação)
- **Arquivos alterados** (tabela arquivo × mudança)
- **Testes unitários** (suite, comando `npm test`, output exit 0)
- Comentário na issue conforme **sec. 10.1** do ticket antes do `open_pr`
- Dúvidas (ex.: comportamento background location, sons push)

## Commit

`feat({task_id}): {descrição}`

## Coordenação

Se precisar endpoint novo → comentar issue tag `agent:backend` antes do merge.

Reporte final: task_id, repo, PR URL, platform, dúvidas.