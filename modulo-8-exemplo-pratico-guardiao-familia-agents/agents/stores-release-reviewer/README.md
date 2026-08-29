# Agente `stores-release-reviewer`

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — canônico compartilhado


**Papel:** Reviewer — revisa releases e configurações de app stores e emite veredito via gateway.

## Quando acionar

- Task em review com handoff do `stores-release`
- Validação de versão, metadados, compliance de loja e rollback plan
- Disputas de submissão

## Quando NÃO acionar

- Implementação mobile → `frontend-mobile`
- Preparação de release → `stores-release`
- Testes funcionais → `qa-gate`

## Revisor/Creator pareado

| Papel | Pasta |
|-------|-------|
| Creator | [`stores-release/`](../stores-release/) |
| Reviewer (este) | `stores-release-reviewer/` |

## Arquivos

| Arquivo | Uso |
|---------|-----|
| `agent.md` | Prompt do reviewer (ReAct, MCP) |
| `SKILL.md` | Checklist de review de stores |

## Decisões

- **Gateway:** `start_review`, `approve_review` ou `request_changes` via `emit_status_event`
- **Handoff:** ler `agents/00-runtime/output/handoffs/{task_id}.json`
- **ReAct:** handoff → checklist stores → veredito (máx. 3 voltas; ver `agent.md`)
- Releases de alto risco exigem HITL antes de go-live

## Ver também

- [`../_shared/`](../_shared/) — MCP, board, fluxo LangGraph
- [`../../board_automation/data/maps/TASK_AGENT_MAP.csv`](../../board_automation/data/maps/TASK_AGENT_MAP.csv) — roteamento task → role
- [`../../docs/comportamento/README.md`](../../docs/comportamento/README.md) — índice de comportamento dos agentes