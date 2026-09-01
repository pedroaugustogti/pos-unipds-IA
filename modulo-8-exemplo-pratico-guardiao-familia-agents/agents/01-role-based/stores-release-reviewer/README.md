# Agente `stores-release-reviewer`

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md`](../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md) — canônico compartilhado

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

- **Gateway:** eventos role-based `stores-release-reviewer_in_code_review`, `stores-release-reviewer_ready_for_test`, `stores-release-reviewer_return_in_progress` via `emit_status_event`
- **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json`
- **ReAct:** `on_status_event` → `developer_review` → `execute_agent_actuation_tool` (máx. 3 voltas; ver `agent.md`)
- Releases de alto risco exigem HITL antes de go-live

## Ver também

- [`00-orchestration/docs/`](../../00-orchestration/docs/README.md) — MCP, board, fluxo LangGraph
