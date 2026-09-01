# Agente `frontend-web`

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md`](../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md) — canônico compartilhado

**Papel:** Creator — implementa e abre PRs no site **guardiao-familia-site** (frontend web).

## Quando acionar

- Task com `agent_role=frontend-web`
- Páginas, componentes, rotas, integração com API no browser
- Ajustes de layout, SEO ou fluxos web do produto

## Quando NÃO acionar

- Apps mobile RN → `frontend-mobile`
- Backend ou API → `backend`
- Infra de hosting/CDN → `cloud-infra` / `devops-cicd`
- Revisão de PR → `frontend-web-reviewer`

## Revisor/Creator pareado

| Papel | Pasta |
|-------|-------|
| Creator (este) | `frontend-web/` |
| Reviewer | [`frontend-web-reviewer/`](../frontend-web-reviewer/) |

## Arquivos

| Arquivo | Uso |
|---------|-----|
| `agent.md` | Prompt do creator (ReAct, MCP, handoff) |
| `SKILL.md` | Checklist web, stack e procedimentos |

## Decisões

- **Gateway:** Status apenas via `emit_status_event`
- **Handoff:** PR e contexto em `agents/00-runtime/output/{task_id}/handoff.json`
- **ReAct:** `on_status_event` → `developer_implement` → `execute_agent_actuation_tool` (eventos `frontend-web_*`; ver `agent.md`)
- Nunca mergear sem passar pelo reviewer pareado

## Ver também

- [`00-orchestration/docs/`](../../00-orchestration/docs/README.md) — MCP, board, fluxo LangGraph
