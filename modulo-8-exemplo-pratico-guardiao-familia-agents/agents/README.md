# Agentes — Guardião Família (v2)

**Papel:** Índice dos agentes — LangGraph v2, MCP role-based e papéis creator/reviewer/qa-gate/ops.

Orquestração **LangGraph v2** + **MCP role-based**: cada `agent_role` vive em `01-role-based/{role}/` com prompt, skill e KNOWLEDGE; o grafo executa 55 nós `evt_*` que disparam pipelines MCP por evento.

## Arquitetura v2

```
Board (GitHub Project)
    ↕ emit_status_event (única porta de status)
LangGraph (57 nós)
    sync_board → orchestrator_decide → evt_* → loop
    ↕ mcp_invoke (in-process)
guardiao_mcp (14 tools, uma por arquivo)
    ↕ lib/orchestrator + lib/gateway
Agentes por papel (01-role-based/)
```

Eventos **role-based** — ex.: `frontend-mobile_in_progress`, `frontend-mobile-reviewer_in_code_review`. Legado v1 **rejeitado** no gateway.

## Árvore

```
agents/
  README.md              ← este arquivo
  _shared/               redirecionamento → 00-orchestration/docs/
  00-orchestration/      LangGraph v2 · guardiao_mcp · scripts · docs/
  00-runtime/            deps · output/{task_id}/ · system/
  01-role-based/         todos os papéis (agent.md, SKILL.md, KNOWLEDGE.md)
```

## Mapa de papéis

| Agente | Tipo | Par | Pasta |
|--------|------|-----|-------|
| `backend` | creator | `backend-reviewer` | `01-role-based/backend/` |
| `frontend-mobile` | creator | `frontend-mobile-reviewer` | `01-role-based/frontend-mobile/` |
| `frontend-web` | creator | `frontend-web-reviewer` | `01-role-based/frontend-web/` |
| `cloud-infra` | creator | `cloud-infra-reviewer` | `01-role-based/cloud-infra/` |
| `database` | creator | `database-reviewer` | `01-role-based/database/` |
| `devops-cicd` | creator | `devops-cicd-reviewer` | `01-role-based/devops-cicd/` |
| `stores-release` | creator | `stores-release-reviewer` | `01-role-based/stores-release/` |
| `qa-author` | creator | `qa-author-reviewer` | `01-role-based/qa-author/` |
| `qa-gate` | gate | — | `01-role-based/qa-gate/` |

## Como escolher um agente

1. Ler `id` da task no board
2. Roteamento: [`00-orchestration/docs/routing/REPOS_AND_ROUTING.md`](00-orchestration/docs/routing/REPOS_AND_ROUTING.md)
3. Carregar `agents/01-role-based/{role}/agent.md` + `SKILL.md` + `KNOWLEDGE.md`
4. Docs: [`00-orchestration/docs/`](00-orchestration/docs/README.md)

## Orquestração

```powershell
python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task T-P3-009 --mode dry_run
python agents/00-orchestration/scripts/langgraph/list_nodes.py
python agents/00-orchestration/scripts/cli/gateway_cli.py emit --task T-P3-009 --event frontend-mobile_in_progress
```

## Documentação

| Tema | Onde |
|------|------|
| Papéis | [`01-role-based/`](01-role-based/) |
| Base de conhecimento | [`00-orchestration/docs/`](00-orchestration/docs/README.md) |
| LangGraph | [`00-orchestration/langgraph_app/`](00-orchestration/langgraph_app/) |
| MCP | [`00-orchestration/guardiao_mcp/`](00-orchestration/guardiao_mcp/) |

## Decisões v2

- **Paths:** `lib/core/agent_paths.py` → `agents/01-role-based/{role}/`
- **Status:** só via `emit_status_event`
- **Handoff:** `agents/00-runtime/output/{task_id}/handoff.json`
- **Skill canônica:** `01-role-based/{role}/SKILL.md`

Bootstrap: `bootstrap.py` ajusta `PYTHONPATH` para imports.
