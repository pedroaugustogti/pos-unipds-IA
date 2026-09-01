# Agentes — Guardião Família

Cada `agent_role` tem pasta com prompt (`agent.md`), skill (`SKILL.md`), **`KNOWLEDGE.md`** (digest + seção MCP v2) e README de decisão.

## Árvore

```
agents/
  README.md           ← este arquivo
  _shared/            MCP_TOOLS, MCP_ROLE_GUIDE, WORKFLOW_BOARD
  00-orchestration/   LangGraph v2, guardiao_mcp, scripts/langgraph + cli
  00-runtime/         deps + output/ + system/
  qa-gate/            gate QA + scripts mobile
  {role}/             creator ou reviewer
  skills/             legado (canônico: agents/{role}/)
```

## Mapa de papéis

| Agente | Tipo | Par | Pasta |
|--------|------|-----|-------|
| `backend` | creator | `backend-reviewer` | `backend/` |
| `frontend-mobile` | creator | `frontend-mobile-reviewer` | `frontend-mobile/` |
| `frontend-web` | creator | `frontend-web-reviewer` | `frontend-web/` |
| `cloud-infra` | creator | `cloud-infra-reviewer` | `cloud-infra/` |
| `database` | creator | `database-reviewer` | `database/` |
| `devops-cicd` | creator | `devops-cicd-reviewer` | `devops-cicd/` |
| `stores-release` | creator | `stores-release-reviewer` | `stores-release/` |
| `qa` | creator (alias) | `qa-reviewer` | `qa/` |
| `qa-author` | creator | `qa-author-reviewer` | `qa-author/` |
| `qa-gate` | gate | — | `qa-gate/` |

## Como escolher um agente

1. Ler `id` da task no board
2. Abrir `board_automation/data/maps/TASK_AGENT_MAP.csv` → coluna `agent_role`
3. Carregar `agents/{role}/agent.md` + `SKILL.md` + **`KNOWLEDGE.md`** (seção MCP no topo)
4. Consultar `agents/_shared/MCP_ROLE_GUIDE.md` para tools do papel

## Orquestração

```powershell
python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task T-P3-009 --mode dry_run
python agents/00-orchestration/scripts/langgraph/smoke_pipeline.py --task T-P3-009 --mode dry_run
```

## Decisões globais

- **Canônico:** `agents/{role}/SKILL.md` (não `skills/`)
- **MCP v2:** 14 tools · guia por papel em `_shared/MCP_ROLE_GUIDE.md`
- **Handoff:** `agents/00-runtime/output/{task_id}/handoff.json`
- **Nunca** mergear PR sem HITL quando policy exigir (`hitl_guard_actuation`)
