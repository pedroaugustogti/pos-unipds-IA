# Agente `database-reviewer`

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — canônico compartilhado


**Papel:** Reviewer — revisa PRs de banco (migrations, schema) e emite veredito via gateway.

## Quando acionar

- Task em code review com handoff do `database`
- Validação de integridade, rollback, impacto em dados e compatibilidade com API
- Disputas de modelagem

## Quando NÃO acionar

- Escrita de migrations → `database`
- Código de repositório NestJS → `backend`
- Provisionamento RDS → `cloud-infra`

## Revisor/Creator pareado

| Papel | Pasta |
|-------|-------|
| Creator | [`database/`](../database/) |
| Reviewer (este) | `database-reviewer/` |

## Arquivos

| Arquivo | Uso |
|---------|-----|
| `agent.md` | Prompt do reviewer (ReAct, MCP) |
| `SKILL.md` | Checklist de review de migrations |

## Decisões

- **Gateway:** `start_review`, `approve_review` ou `request_changes` via `emit_status_event`
- **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json`
- **ReAct:** handoff → checklist schema → veredito (máx. 3 voltas; ver `agent.md`)

## Ver também

- [`../_shared/`](../_shared/) — MCP, board, fluxo LangGraph
- [`../../board_automation/data/maps/TASK_AGENT_MAP.csv`](../../board_automation/data/maps/TASK_AGENT_MAP.csv) — roteamento task → role
- [`../../docs/comportamento/README.md`](../../docs/comportamento/README.md) — índice de comportamento dos agentes