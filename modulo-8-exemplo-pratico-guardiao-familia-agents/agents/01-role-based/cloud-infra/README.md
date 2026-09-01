# Agente `cloud-infra`

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md`](../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md) — canônico compartilhado

**Papel:** Creator — provisiona e altera infraestrutura AWS via **Terraform** (VPC, ECS/Fargate, RDS, etc.).

## Quando acionar

- Task com `agent_role=cloud-infra`
- Módulos Terraform, variáveis de ambiente, recursos AWS novos ou ajustes
- Alinhamento de infra com requisitos de backend/mobile/web

## Quando NÃO acionar

- Código de aplicação (API, UI) → `backend` / `frontend-*`
- Pipelines CI (build/test) → `devops-cicd`
- Migrations SQL → `database`
- Revisão de PR de infra → `cloud-infra-reviewer`

## Revisor/Creator pareado

| Papel | Pasta |
|-------|-------|
| Creator (este) | `cloud-infra/` |
| Reviewer | [`cloud-infra-reviewer/`](../cloud-infra-reviewer/) |

## Arquivos

| Arquivo | Uso |
|---------|-----|
| `agent.md` | Prompt do creator (ReAct, MCP, handoff) |
| `SKILL.md` | Checklist Terraform/AWS e procedimentos |

## Decisões

- **Gateway:** Status apenas via `emit_status_event`
- **Handoff:** plan/PR, ambientes afetados em `agents/00-runtime/output/{task_id}/handoff.json`
- **ReAct:** `on_status_event` → `developer_implement` → `execute_agent_actuation_tool` (eventos `cloud-infra_*`; ver `agent.md`)
- Nunca aplicar destroy em produção sem HITL; nunca alterar código de app

## Ver também

- [`00-orchestration/docs/`](../../00-orchestration/docs/README.md) — MCP, board, fluxo LangGraph
