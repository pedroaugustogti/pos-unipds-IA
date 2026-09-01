# Agente `frontend-web-reviewer`

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — canônico compartilhado


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

- **Gateway:** `start_review`, `approve_review` ou `request_changes` via `emit_status_event`
- **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json` antes de revisar
- **ReAct:** handoff → checklist → veredito (máx. 3 voltas; ver `agent.md`)

## Ver também

- [`../_shared/`](../_shared/) — MCP, board, fluxo LangGraph
- [`../../board_automation/data/maps/TASK_AGENT_MAP.csv`](../../board_automation/data/maps/TASK_AGENT_MAP.csv) — roteamento task → role
- [`../../docs/comportamento/README.md`](../../docs/comportamento/README.md) — índice de comportamento dos agentes