# Agente `backend`

## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — canônico compartilhado


**Papel:** Creator — implementa features, corrige bugs e abre PRs no repositório **guardiao-familia-api** (NestJS).

## Quando acionar

- Task no board com `agent_role=backend` (ver `TASK_AGENT_MAP.csv`)
- Endpoints REST/GraphQL, módulos NestJS, DTOs, guards, integrações de serviço
- Correções de API consumidas por mobile ou web

## Quando NÃO acionar

- UI React Native ou site → `frontend-mobile` / `frontend-web`
- Migrations ou schema SQL → `database`
- Terraform ou recursos AWS → `cloud-infra`
- Pipelines GitHub Actions → `devops-cicd`
- Revisão de PR (sem implementação) → `backend-reviewer`

## Revisor/Creator pareado

| Papel | Pasta |
|-------|-------|
| Creator (este) | `backend/` |
| Reviewer | [`backend-reviewer/`](../backend-reviewer/) |

## Arquivos

| Arquivo | Uso |
|---------|-----|
| `agent.md` | Prompt do creator (ReAct, MCP, handoff) |
| `SKILL.md` | Checklist NestJS, repos e procedimentos |

## Decisões

- **Gateway:** alterar Status somente via `emit_status_event` (MCP) — nunca editar coluna do board manualmente
- **Handoff:** gravar PR, branch e dúvidas em `agents/00-runtime/output/handoffs/{task_id}.json`
- **ReAct:** loop claim → implementar → testes do módulo → `open_pr` (máx. 4 voltas; ver `agent.md`)
- Nunca mergear PR; nunca alterar Terraform ou apps mobile

## Ver também

- [`../_shared/`](../_shared/) — MCP, board, fluxo LangGraph
- [`../../board_automation/data/maps/TASK_AGENT_MAP.csv`](../../board_automation/data/maps/TASK_AGENT_MAP.csv) — roteamento task → role
- [`../../docs/comportamento/README.md`](../../docs/comportamento/README.md) — índice de comportamento dos agentes