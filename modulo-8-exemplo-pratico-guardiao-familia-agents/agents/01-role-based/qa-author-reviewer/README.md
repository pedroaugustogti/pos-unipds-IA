# Agente `qa-author-reviewer`

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md`](../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md) — canônico compartilhado

**Papel:** Reviewer — revisa PRs de harness de testes e emite veredito via gateway.

## Quando acionar

- Task em code review com handoff do `qa-author`
- Validação de seeds, idempotência, isolamento de ambientes e reuso pelo gate
- Disputas sobre estrutura do harness

## Quando NÃO acionar

- Authoring de fixtures → `qa-author`
- Execução de testes E2E → `qa` / `qa-gate`
- Código de aplicação → creators de stack

## Revisor/Creator pareado

| Papel | Pasta |
|-------|-------|
| Creator | [`qa-author/`](../qa-author/) |
| Reviewer (este) | `qa-author-reviewer/` |

## Arquivos

| Arquivo | Uso |
|---------|-----|
| `agent.md` | Prompt do reviewer (ReAct, MCP) |
| `SKILL.md` | Checklist de review de harness |

## Decisões

- **Gateway:** eventos role-based `qa-author-reviewer_in_code_review`, `qa-author-reviewer_ready_for_test`, `qa-author-reviewer_return_in_progress` via `emit_status_event`
- **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json`
- **ReAct:** `on_status_event` → `developer_review` → `execute_agent_actuation_tool` (máx. 3 voltas; ver `agent.md`)

## Ver também

- [`00-orchestration/docs/`](../../00-orchestration/docs/README.md) — MCP, board, fluxo LangGraph
