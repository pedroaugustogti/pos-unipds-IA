# Agente `qa-author`

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — canônico compartilhado


**Papel:** Creator — authora e mantém o **harness de testes** (fixtures, helpers, dados seed, estrutura de suites).

## Quando acionar

- Task com `agent_role=qa-author`
- Novos helpers de teste, seeds de DB para QA, utilitários Appium/E2E
- Refatoração do harness compartilhado entre `qa` e `qa-gate`

## Quando NÃO acionar

- Execução de gate ou evidências operacionais → `qa-gate`
- Rodar cenários E2E pontuais → `qa`
- Código de produto → creators de stack
- Revisão de harness → `qa-author-reviewer`

## Revisor/Creator pareado

| Papel | Pasta |
|-------|-------|
| Creator (este) | `qa-author/` |
| Reviewer | [`qa-author-reviewer/`](../qa-author-reviewer/) |

## Arquivos

| Arquivo | Uso |
|---------|-----|
| `agent.md` | Prompt do creator (ReAct, MCP, handoff) |
| `SKILL.md` | Checklist harness, seeds e procedimentos |

## Decisões

- **Gateway:** Status apenas via `emit_status_event`
- **Handoff:** arquivos alterados, contratos de seed em `agents/00-runtime/output/handoffs/{task_id}.json`
- **ReAct:** claim → implementar harness → testes locais → `open_pr` (ver `agent.md`)
- Harness deve ser reutilizável pelo `qa-gate` sem duplicar lógica

## Ver também

- [`../_shared/`](../_shared/) — MCP, board, fluxo LangGraph
- [`../../board_automation/data/maps/TASK_AGENT_MAP.csv`](../../board_automation/data/maps/TASK_AGENT_MAP.csv) — roteamento task → role
- [`../../docs/comportamento/README.md`](../../docs/comportamento/README.md) — índice de comportamento dos agentes