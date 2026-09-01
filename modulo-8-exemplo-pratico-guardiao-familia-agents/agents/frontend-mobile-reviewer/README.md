# Agente `frontend-mobile-reviewer`

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — canônico compartilhado


**Papel:** Reviewer — revisa PRs dos apps React Native (parent/child) e emite veredito via gateway.

## Quando acionar

- Task em code review com handoff do `frontend-mobile`
- Validação de navegação, acessibilidade, contratos com API e padrões RN
- Disputas de implementação mobile

## Quando NÃO acionar

- Implementação de telas ou features → `frontend-mobile`
- Testes E2E automatizados pós-review → `qa` / `qa-gate`
- Release nas lojas → `stores-release`

## Revisor/Creator pareado

| Papel | Pasta |
|-------|-------|
| Creator | [`frontend-mobile/`](../frontend-mobile/) |
| Reviewer (este) | `frontend-mobile-reviewer/` |

## Arquivos

| Arquivo | Uso |
|---------|-----|
| `agent.md` | Prompt do reviewer (ReAct, MCP) |
| `SKILL.md` | Checklist de review mobile |

## Decisões

- **Gateway:** `start_review`, `approve_review` ou `request_changes` via `emit_status_event`
- **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json` antes de revisar
- **ReAct:** `on_status_event` → `developer_review` → `execute_agent_actuation_tool` (máx. 3 voltas; ver `agent.md`)

## Ver também

- [`../_shared/`](../_shared/) — MCP, board, fluxo LangGraph
- [`../../board_automation/data/maps/TASK_AGENT_MAP.csv`](../../board_automation/data/maps/TASK_AGENT_MAP.csv) — roteamento task → role
- [`../../docs/comportamento/README.md`](../../docs/comportamento/README.md) — índice de comportamento dos agentes