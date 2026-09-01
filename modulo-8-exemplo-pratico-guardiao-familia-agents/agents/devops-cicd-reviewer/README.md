# Agente `devops-cicd-reviewer`

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — canônico compartilhado


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

- **Gateway:** `start_review`, `approve_review` ou `request_changes` via `emit_status_event`
- **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json`
- **ReAct:** `on_status_event` → `developer_review` → `execute_agent_actuation_tool` (máx. 3 voltas; ver `agent.md`)

## Ver também

- [`../_shared/`](../_shared/) — MCP, board, fluxo LangGraph
- [`../../board_automation/data/maps/TASK_AGENT_MAP.csv`](../../board_automation/data/maps/TASK_AGENT_MAP.csv) — roteamento task → role
- [`../../docs/comportamento/README.md`](../../docs/comportamento/README.md) — índice de comportamento dos agentes