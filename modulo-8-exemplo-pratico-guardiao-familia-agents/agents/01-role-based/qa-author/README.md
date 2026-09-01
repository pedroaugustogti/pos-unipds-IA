# Agente `qa-author`

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md`](../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md) — canônico compartilhado

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
- **Handoff:** arquivos alterados, contratos de seed em `agents/00-runtime/output/{task_id}/handoff.json`
- **ReAct:** `on_status_event` → `developer_implement` → `execute_agent_actuation_tool` (eventos `qa-author_*`; ver `agent.md`)
- Harness deve ser reutilizável pelo `qa-gate` sem duplicar lógica

## Ver também

- [`00-orchestration/docs/`](../../00-orchestration/docs/README.md) — MCP, board, fluxo LangGraph
