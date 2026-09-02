# Workflow do board

Contrato de **status**, **eventos** e **papéis** compartilhado por todos os agentes. Independe da fonte de dados — GitHub Project, CSV local ou sandbox.

## Duas fontes, um fluxo

| Papel | Fonte típica | O que fornece |
|-------|--------------|---------------|
| **Status em tempo real** | GitHub Project (import JSON) | Coluna atual da task (`board_status`) |
| **Roteamento e metadados** | CSV de mapa (`TASK_AGENT_MAP*.csv`) | `agent_role`, repo, track, prioridade, dependências |

O orquestrador **mescla** as duas: status vem do board; creator/reviewer vêm do CSV. Referências:

- Board automation (reconcile, imports) → [`board_automation/README.md`](../../board_automation/README.md)
- CSV / roteamento → [`board_automation/data/maps/README.md`](../../board_automation/data/maps/README.md)
- Nós LangGraph e eventos → [`STATEGRAPH_FLOW.md`](./STATEGRAPH_FLOW.md)

Env overrides (opcionais): `GUARDAO_BOARD_JSON`, `GUARDAO_TASK_MAP_CSV`.

## Pipeline de status

```
Todo → In Progress → Ready for Code Review → In Code Review
  → Ready for Test → In Test → In Pull Request → Done
```

Transições **só** via `emit_status_event` (gateway ou MCP). Nunca alterar status manualmente fora desse caminho.

## Quem age em cada status

| Status | Agente responsável |
|--------|-------------------|
| Todo | `orchestrator` (dispatch / dispatch prioritário) |
| In Progress | **creator** da task (coluna `agent_role` no CSV) |
| Ready for Code Review | fila → **{creator}-reviewer** |
| In Code Review | **{creator}-reviewer** |
| Ready for Test | `qa-gate` (aguarda CI) |
| In Test | `qa-gate` |
| In Pull Request | `devops-cicd` (prod/infra) ou `stores-release` (track stores) |
| Done | encerramento após HITL em `{ops}_done` |

Exceções de roteamento (repo/track fora de escopo): `scope_redirect` — ver [`REPOS_AND_ROUTING.md`](./REPOS_AND_ROUTING.md).

## Eventos principais (v2 role-based)

Padrão: `{agent_role}_{status_slug}` · retrocesso: `{role}_return_{status_slug}`

| Evento (exemplo backend) | Status alvo | Quem emite |
|--------|-------------|------------|
| `orchestrator_enter_in_progress` | In Progress | orchestrator |
| `backend_in_progress` | In Progress | backend (creator) |
| `backend_ready_for_code_review` | Ready for Code Review | backend |
| `backend-reviewer_in_code_review` | In Code Review | backend-reviewer |
| `backend-reviewer_ready_for_test` | Ready for Test | backend-reviewer |
| `backend-reviewer_return_in_progress` | In Progress | backend-reviewer |
| `qa-gate_in_test` | In Test | qa-gate |
| `qa-gate_in_pull_request` | In Pull Request | qa-gate |
| `qa-gate_return_in_progress` | In Progress | qa-gate |
| `devops-cicd_done` / `stores-release_done` | Done | ops |

Nomes v1 (`claim`, `open_pr`, `merge_pr`, …) são **rejeitados** pelo gateway (`lib/gateway/v2_events.py`).

Lista completa e nós LangGraph: [`STATEGRAPH_FLOW.md`](./STATEGRAPH_FLOW.md).

## HITL obrigatório

| Situação | Modo |
|----------|------|
| `{ops}_done` (ex. `devops-cicd_done`) | `block_until_human` |
| 3× `qa-gate_return_in_progress` consecutivos | `block_until_human` + blocker |
| `{reviewer}_ready_for_test` em task de alto risco | `propose_only` (humano confirma) |

## Ciclo idle → dispatch

1. `list_idle` — resolve próximo agente livre
2. `emit_status_event` — atualiza board + handoff + audit
3. Agente ocupado → `dispatch_queue`
4. HITL pendente → `hitl_queue` (humano aprova)

Porta única (CLI): `agents/00-orchestration/scripts/cli/gateway_cli.py`
