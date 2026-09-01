# Agente `devops-cicd-reviewer`

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md`](../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md) — canônico compartilhado

**Papel:** Reviewer — revisa PRs de CI/CD e emite veredito via gateway.

## Quando acionar

- Task em code review com handoff do `devops-cicd`
- Validação de segurança de workflows, permissões, caches e impacto em builds
- Disputas de pipeline

## Quando NÃO acionar

- Authoring de workflows → `devops-cicd`
- Infra AWS → `cloud-infra`
- Execução de gate QA → `qa-gate`

## Revisor/Creator pareado

| Papel | Pasta |
|-------|-------|
| Creator | [`devops-cicd/`](../devops-cicd/) |
| Reviewer (este) | `devops-cicd-reviewer/` |

## Arquivos

| Arquivo | Uso |
|---------|-----|
| `agent.md` | Prompt do reviewer (ReAct, MCP) |
| `SKILL.md` | Checklist de review CI/CD |

## Decisões

- **Gateway:** eventos role-based `devops-cicd-reviewer_in_code_review`, `devops-cicd-reviewer_ready_for_test`, `devops-cicd-reviewer_return_in_progress` via `emit_status_event`
- **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json`
- **ReAct:** `on_status_event` → `developer_review` → `execute_agent_actuation_tool` (máx. 3 voltas; ver `agent.md`)

## Ver também

- [`00-orchestration/docs/`](../../00-orchestration/docs/README.md) — MCP, board, fluxo LangGraph
