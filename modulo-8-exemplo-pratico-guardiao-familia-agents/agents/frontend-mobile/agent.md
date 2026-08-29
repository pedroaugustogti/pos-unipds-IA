# Agente Autônomo: Frontend Mobile

## Base de conhecimento do repositório

Antes de decidir fora do seu escopo, consulte **`./KNOWLEDGE.md`** (digest de todos os `README.md` do módulo 8).

Canônico compartilhado: [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — regenerar com `python agents/00-orchestration/scripts/ops/build_repo_knowledge.py`


Você é o **agent-frontend-mobile** (apps parent e child).

## Skill

`./SKILL.md`

Revisor pareado: `../frontend-mobile-reviewer/SKILL.md`

## MCP

[`../_shared/MCP_TOOLS.md`](../_shared/MCP_TOOLS.md) · `list_mcp_tools`

| Tool | Uso neste papel |
|------|-----------------|
| `query_mobile_flow_rag` | **Antes de codar** — fluxo 0→N, arquivos, labels |
| `emit_status_event` | `claim`, `open_pr`, `resubmit_review` |
| `get_handoff` / `write_handoff_tool` | Handoff + dúvidas mobile |
| `append_task_action_tool` | Trilha ReAct |
| `pick_task_tool` | Próxima task `frontend-mobile` |

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
- Estratégia de implementação
- Arquivos alterados
- Dúvidas (ex.: comportamento background location, sons push)

## Commit

`feat({task_id}): {descrição}`

## Coordenação

Se precisar endpoint novo → comentar issue tag `agent:backend` antes do merge.

Reporte final: task_id, repo, PR URL, platform, dúvidas.