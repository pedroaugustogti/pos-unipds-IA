# Agentes — Guardião Família

Cada `agent_role` tem pasta com prompt (`agent.md`), skill (`SKILL.md`), **`KNOWLEDGE.md`** (digest de todos os READMEs) e README de decisão.

## Árvore

```
agents/
  README.md           ← este arquivo
  _shared/            contexto comum (MCP, board, fluxo)
  00-orchestration/   LangGraph, MCP, scripts
  00-runtime/         deps + output/
  qa-gate/            gate QA + scripts mobile
  {role}/             creator ou reviewer
  skills/             legado (editar agents/{role}/)
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
| `qa` | creator | `qa-reviewer` | `qa/` |
| `qa-author` | creator | `qa-author-reviewer` | `qa-author/` |
| `qa-gate` | gate | — | `qa-gate/` |

## Como escolher um agente

1. Ler `id` da task no board
2. Abrir `board_automation/data/maps/TASK_AGENT_MAP.csv` → coluna `agent_role`
3. Carregar `agents/{role}/agent.md` + `SKILL.md` + **`KNOWLEDGE.md`**
4. Consultar `agents/_shared/` para MCP e Status

## Orquestração

```powershell
python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task T-P3-009 --mode dry_run --role frontend-mobile
python agents/00-orchestration/scripts/worker/worker_run.py --next --role backend
```

## Decisões globais

- **Canônico:** `agents/{role}/SKILL.md` (não `skills/`)
- **Base de conhecimento:** `agents/{role}/KNOWLEDGE.md` ou `agents/_shared/REPO_KNOWLEDGE.md`
- Regenerar índice: `python agents/00-orchestration/scripts/ops/build_repo_knowledge.py`
- **Handoff:** `agents/00-runtime/output/handoffs/{task_id}.json`
- **Nunca** mergear PR sem passar HITL quando `release_blocker` ou policy exigir
