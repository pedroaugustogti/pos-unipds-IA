# Agente `database`

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md`](../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md) — canônico compartilhado

**Papel:** Creator — modela schema, escreve migrations e abre PRs de banco de dados do Guardião Família.

## Quando acionar

- Task com `agent_role=database`
- Migrations, índices, constraints, seeds e ajustes de performance SQL
- Alinhamento de modelo de dados com requisitos de backend

## Quando NÃO acionar

- Lógica NestJS ou endpoints → `backend`
- Infra RDS/Terraform → `cloud-infra`
- Testes E2E → `qa`
- Revisão de PR → `database-reviewer`

## Revisor/Creator pareado

| Papel | Pasta |
|-------|-------|
| Creator (este) | `database/` |
| Reviewer | [`database-reviewer/`](../database-reviewer/) |

## Arquivos

| Arquivo | Uso |
|---------|-----|
| `agent.md` | Prompt do creator (ReAct, MCP, handoff) |
| `SKILL.md` | Checklist migrations, rollback e procedimentos |

## Decisões

- **Gateway:** Status apenas via `emit_status_event`
- **Handoff:** migrations, ordem de deploy em `agents/00-runtime/output/{task_id}/handoff.json`
- **ReAct:** `on_status_event` → `developer_implement` → `execute_agent_actuation_tool` (eventos `database_*`; ver `agent.md`)
- Nunca dropar dados em produção sem HITL explícito

## Ver também

- [`00-orchestration/docs/`](../../00-orchestration/docs/README.md) — MCP, board, fluxo LangGraph
