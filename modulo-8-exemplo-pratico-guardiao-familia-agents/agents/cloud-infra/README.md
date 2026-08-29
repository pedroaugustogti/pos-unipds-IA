# Agente `cloud-infra`

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — canônico compartilhado


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
- **Handoff:** plan/PR, ambientes afetados em `agents/00-runtime/output/handoffs/{task_id}.json`
- **ReAct:** claim → plan/apply local ou dry-run → `open_pr` (ver `agent.md`)
- Nunca aplicar destroy em produção sem HITL; nunca alterar código de app

## Ver também

- [`../_shared/`](../_shared/) — MCP, board, fluxo LangGraph
- [`../../board_automation/data/maps/TASK_AGENT_MAP.csv`](../../board_automation/data/maps/TASK_AGENT_MAP.csv) — roteamento task → role
- [`../../docs/comportamento/README.md`](../../docs/comportamento/README.md) — índice de comportamento dos agentes