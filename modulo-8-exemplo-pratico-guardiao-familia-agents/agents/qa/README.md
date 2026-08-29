# Agente `qa`

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — canônico compartilhado


**Papel:** Creator — executa e documenta testes **E2E cross-stack** (API + web + mobile) do Guardião Família.

## Quando acionar

- Task com `agent_role=qa`
- Cenários E2E integrados, regressão entre stacks, evidências de fluxo completo
- Validação pós-implementação antes ou após gate formal

## Quando NÃO acionar

- Authoring de harness/fixtures → `qa-author`
- Gate automatizado com Appium e scripts oficiais → `qa-gate`
- Implementação de código de produto → creators de stack
- Revisão de plano de testes → `qa-reviewer`

## Revisor/Creator pareado

| Papel | Pasta |
|-------|-------|
| Creator (este) | `qa/` |
| Reviewer | [`qa-reviewer/`](../qa-reviewer/) |

## Arquivos

| Arquivo | Uso |
|---------|-----|
| `agent.md` | Prompt do creator (ReAct, MCP, handoff) |
| `SKILL.md` | Checklist E2E cross-stack e evidências |

## Decisões

- **Gateway:** `start_test`, `test_passed`, `test_failed_bug` via `emit_status_event`
- **Handoff:** cenários, logs e artefatos em `agents/00-runtime/output/handoffs/{task_id}.json`
- **ReAct:** claim → executar cenários → registrar evidência → status (ver `agent.md`)
- Não claimar harness em Todo (responsabilidade do `qa-author`)

## Ver também

- [`../_shared/`](../_shared/) — MCP, board, fluxo LangGraph
- [`../../board_automation/data/maps/TASK_AGENT_MAP.csv`](../../board_automation/data/maps/TASK_AGENT_MAP.csv) — roteamento task → role
- [`../../docs/comportamento/README.md`](../../docs/comportamento/README.md) — índice de comportamento dos agentes