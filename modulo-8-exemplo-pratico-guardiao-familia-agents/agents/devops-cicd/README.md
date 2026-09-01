# Agente `devops-cicd`

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — canônico compartilhado


**Papel:** Creator — configura e mantém pipelines **CI/CD** (GitHub Actions, build, test, deploy hooks).

## Quando acionar

- Task com `agent_role=devops-cicd`
- Workflows YAML, secrets de CI, gates de qualidade no pipeline
- Integração de testes automatizados no fluxo de PR/merge

## Quando NÃO acionar

- Código de produto (API, UI) → creators de stack
- Recursos AWS/Terraform → `cloud-infra`
- Authoring de harness de teste → `qa-author`
- Revisão de PR → `devops-cicd-reviewer`

## Revisor/Creator pareado

| Papel | Pasta |
|-------|-------|
| Creator (este) | `devops-cicd/` |
| Reviewer | [`devops-cicd-reviewer/`](../devops-cicd-reviewer/) |

## Arquivos

| Arquivo | Uso |
|---------|-----|
| `agent.md` | Prompt do creator (ReAct, MCP, handoff) |
| `SKILL.md` | Checklist CI/CD e procedimentos |

## Decisões

- **Gateway:** Status apenas via `emit_status_event`
- **Handoff:** workflows alterados, impacto em repos em `agents/00-runtime/output/{task_id}/handoff.json`
- **ReAct:** claim → editar workflow → validar local/dry-run → `open_pr` (ver `agent.md`)
- Nunca expor secrets no repositório; nunca mergear sem reviewer

## Ver também

- [`../_shared/`](../_shared/) — MCP, board, fluxo LangGraph
- [`../../board_automation/data/maps/TASK_AGENT_MAP.csv`](../../board_automation/data/maps/TASK_AGENT_MAP.csv) — roteamento task → role
- [`../../docs/comportamento/README.md`](../../docs/comportamento/README.md) — índice de comportamento dos agentes