# Agente `cloud-infra-reviewer`

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md`](../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md) — canônico compartilhado

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

- **Gateway:** eventos role-based `cloud-infra-reviewer_in_code_review`, `cloud-infra-reviewer_ready_for_test`, `cloud-infra-reviewer_return_in_progress` via `emit_status_event`
- **Handoff:** ler `agents/00-runtime/output/{task_id}/handoff.json` (plan, ambientes)
- **ReAct:** `on_status_event` → `developer_review` → `execute_agent_actuation_tool` (máx. 3 voltas; ver `agent.md`)
- Mudanças de alto risco exigem HITL antes de apply em produção

## Ver também

- [`00-orchestration/docs/`](../../00-orchestration/docs/README.md) — MCP, board, fluxo LangGraph
