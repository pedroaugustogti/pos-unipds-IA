# Agente `stores-release`

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md`](../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md) — canônico compartilhado

**Papel:** Creator — prepara e executa releases nas **app stores** (Google Play, App Store) do Guardião Família.

## Quando acionar

- Task com `agent_role=stores-release`
- Versionamento, changelogs, metadados de loja, tracks de release
- Coordenação de build assinado e submissão

## Quando NÃO acionar

- Desenvolvimento de features mobile → `frontend-mobile`
- Testes E2E ou evidências → `qa` / `qa-gate`
- Infra de backend → `cloud-infra`
- Revisão de PR → `stores-release-reviewer`

## Revisor/Creator pareado

| Papel | Pasta |
|-------|-------|
| Creator (este) | `stores-release/` |
| Reviewer | [`stores-release-reviewer/`](../stores-release-reviewer/) |

## Arquivos

| Arquivo | Uso |
|---------|-----|
| `agent.md` | Prompt do creator (ReAct, MCP, handoff) |
| `SKILL.md` | Checklist stores, versionamento e procedimentos |

## Decisões

- **Gateway:** Status apenas via `emit_status_event`
- **Handoff:** versão, track, links de release em `agents/00-runtime/output/{task_id}/handoff.json`
- **ReAct:** `on_status_event` → `developer_implement` → `execute_agent_actuation_tool` (eventos `stores-release_*`; ver `agent.md`)
- Nunca publicar em produção sem reviewer e HITL quando `release_blocker`

## Ver também

- [`00-orchestration/docs/`](../../00-orchestration/docs/README.md) — MCP, board, fluxo LangGraph
