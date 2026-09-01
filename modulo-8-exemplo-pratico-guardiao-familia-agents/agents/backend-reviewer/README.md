# Agente `backend-reviewer`

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — canônico compartilhado


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

- **Gateway:** `start_review`, `approve_review` ou `request_changes` via `emit_status_event`
- **Handoff:** ler obrigatoriamente `agents/00-runtime/output/{task_id}/handoff.json` antes de revisar
- **ReAct:** get_handoff → checklist → veredito (máx. 3 voltas; ver `agent.md`)
- Em alto risco, não avançar autonomia plena sem HITL humano

## Ver também

- [`../_shared/`](../_shared/) — MCP, board, fluxo LangGraph
- [`../../board_automation/data/maps/TASK_AGENT_MAP.csv`](../../board_automation/data/maps/TASK_AGENT_MAP.csv) — roteamento task → role
- [`../../docs/comportamento/README.md`](../../docs/comportamento/README.md) — índice de comportamento dos agentes