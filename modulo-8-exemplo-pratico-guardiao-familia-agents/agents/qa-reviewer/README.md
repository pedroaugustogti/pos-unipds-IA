# Agente `qa-reviewer`

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — canônico compartilhado


**Papel:** Reviewer — revisa planos, evidências e resultados E2E do `qa` e emite veredito via gateway.

## Quando acionar

- Task em review com handoff do `qa`
- Validação de cobertura de cenários, qualidade de evidências e classificação de bugs
- Disputas sobre pass/fail de testes cross-stack

## Quando NÃO acionar

- Execução de testes → `qa`
- Gate oficial pós-review → `qa-gate`
- Criação de fixtures/harness → `qa-author`

## Revisor/Creator pareado

| Papel | Pasta |
|-------|-------|
| Creator | [`qa/`](../qa/) |
| Reviewer (este) | `qa-reviewer/` |

## Arquivos

| Arquivo | Uso |
|---------|-----|
| `agent.md` | Prompt do reviewer (ReAct, MCP) |
| `SKILL.md` | Checklist de review QA/E2E |

## Decisões

- **Gateway:** `start_review`, `approve_review` ou `request_changes` via `emit_status_event`
- **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json` (evidências anexas)
- **ReAct:** `on_status_event` → `developer_review` → `execute_agent_actuation_tool` (máx. 3 voltas; ver `agent.md`)

## Ver também

- [`../_shared/`](../_shared/) — MCP, board, fluxo LangGraph
- [`../../board_automation/data/maps/TASK_AGENT_MAP.csv`](../../board_automation/data/maps/TASK_AGENT_MAP.csv) — roteamento task → role
- [`../../docs/comportamento/README.md`](../../docs/comportamento/README.md) — índice de comportamento dos agentes