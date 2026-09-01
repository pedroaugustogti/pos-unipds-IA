# Agente `database-reviewer`

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md`](../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md) — canônico compartilhado

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

- **Gateway:** eventos role-based `database-reviewer_in_code_review`, `database-reviewer_ready_for_test`, `database-reviewer_return_in_progress` via `emit_status_event`
- **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json`
- **ReAct:** `on_status_event` → `developer_review` → `execute_agent_actuation_tool` (máx. 3 voltas; ver `agent.md`)

## Ver também

- [`00-orchestration/docs/`](../../00-orchestration/docs/README.md) — MCP, board, fluxo LangGraph
