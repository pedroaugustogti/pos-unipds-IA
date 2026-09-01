# Agente `cloud-infra-reviewer`

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — canônico compartilhado


**Papel:** Reviewer — revisa PRs de infraestrutura Terraform/AWS e emite veredito via gateway.

## Quando acionar

- Task em code review com handoff do `cloud-infra`
- Validação de segurança (IAM, SG), custo, drift e impacto em ambientes
- Disputas de mudanças de infra

## Quando NÃO acionar

- Authoring de módulos Terraform → `cloud-infra`
- Pipelines de deploy → `devops-cicd`
- Schema de banco → `database`

## Revisor/Creator pareado

| Papel | Pasta |
|-------|-------|
| Creator | [`cloud-infra/`](../cloud-infra/) |
| Reviewer (este) | `cloud-infra-reviewer/` |

## Arquivos

| Arquivo | Uso |
|---------|-----|
| `agent.md` | Prompt do reviewer (ReAct, MCP) |
| `SKILL.md` | Checklist de review Terraform/AWS |

## Decisões

- **Gateway:** `start_review`, `approve_review` ou `request_changes` via `emit_status_event`
- **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json` (plan, ambientes)
- **ReAct:** `on_status_event` → `developer_review` → `execute_agent_actuation_tool` (máx. 3 voltas; ver `agent.md`)
- Mudanças de alto risco exigem HITL antes de apply em produção

## Ver também

- [`../_shared/`](../_shared/) — MCP, board, fluxo LangGraph
- [`../../board_automation/data/maps/TASK_AGENT_MAP.csv`](../../board_automation/data/maps/TASK_AGENT_MAP.csv) — roteamento task → role
- [`../../docs/comportamento/README.md`](../../docs/comportamento/README.md) — índice de comportamento dos agentes