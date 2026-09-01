# Agente `backend-reviewer`

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md`](../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md) — canônico compartilhado

**Papel:** Reviewer — revisa PRs de backend (NestJS) e emite veredito via gateway; em alto risco, `approved` é proposta sujeita a HITL.

## Quando acionar

- Task em `Ready for Code Review` / `In Code Review` com handoff do `backend`
- Validação de contratos API, segurança (auth, LGPD), SOS e pagamentos
- Disputa creator/reviewer registrada no handoff

## Quando NÃO acionar

- Implementação de código ou abertura de PR → `backend`
- Testes E2E cross-stack após merge → `qa` / `qa-gate`
- Infra ou banco → papéis especializados

## Revisor/Creator pareado

| Papel | Pasta |
|-------|-------|
| Creator | [`backend/`](../backend/) |
| Reviewer (este) | `backend-reviewer/` |

## Arquivos

| Arquivo | Uso |
|---------|-----|
| `agent.md` | Prompt do reviewer (ReAct, HITL, MCP) |
| `SKILL.md` | Checklist de review NestJS |

## Decisões

- **Gateway:** eventos role-based `backend-reviewer_in_code_review`, `backend-reviewer_ready_for_test`, `backend-reviewer_return_in_progress` via `emit_status_event`
- **Handoff:** ler obrigatoriamente `agents/00-runtime/output/{task_id}/handoff.json` antes de revisar
- **ReAct:** `on_status_event` → `developer_review` → `execute_agent_actuation_tool` (máx. 3 voltas; ver `agent.md`)
- Em alto risco, não avançar autonomia plena sem HITL humano

## Ver também

- [`00-orchestration/docs/`](../../00-orchestration/docs/README.md) — MCP, board, fluxo LangGraph
