# Agente `frontend-web-reviewer`

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md`](../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md) — canônico compartilhado

**Papel:** Reviewer — revisa PRs do site web (guardiao-familia-site) e emite veredito via gateway.

## Quando acionar

- Task em code review com handoff do `frontend-web`
- Validação de UX, acessibilidade, performance e contratos com API
- Disputas de implementação web

## Quando NÃO acionar

- Implementação de páginas ou componentes → `frontend-web`
- Testes E2E → `qa` / `qa-gate`
- Deploy ou infra → `devops-cicd` / `cloud-infra`

## Revisor/Creator pareado

| Papel | Pasta |
|-------|-------|
| Creator | [`frontend-web/`](../frontend-web/) |
| Reviewer (este) | `frontend-web-reviewer/` |

## Arquivos

| Arquivo | Uso |
|---------|-----|
| `agent.md` | Prompt do reviewer (ReAct, MCP) |
| `SKILL.md` | Checklist de review web |

## Decisões

- **Gateway:** eventos role-based `frontend-web-reviewer_in_code_review`, `frontend-web-reviewer_ready_for_test`, `frontend-web-reviewer_return_in_progress` via `emit_status_event`
- **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json` antes de revisar
- **ReAct:** `on_status_event` → `developer_review` → `execute_agent_actuation_tool` (máx. 3 voltas; ver `agent.md`)

## Ver também

- [`00-orchestration/docs/`](../../00-orchestration/docs/README.md) — MCP, board, fluxo LangGraph
