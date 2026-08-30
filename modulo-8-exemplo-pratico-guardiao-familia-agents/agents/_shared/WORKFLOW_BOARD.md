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
| Todo | `orchestrator` (claim / dispatch) |
| In Progress | **creator** da task (coluna `agent_role` no CSV) |
| Ready for Code Review | fila → **{creator}-reviewer** |
| In Code Review | **{creator}-reviewer** |
| Ready for Test | `qa-gate` (aguarda CI) |
| In Test | `qa-gate` |
| In Pull Request | `devops-cicd` (prod/infra) ou `stores-release` (track stores) |
| Done | encerramento após HITL em `merge_pr` |

Exceções de roteamento (repo/track fora de escopo): `scope_redirect` — ver [`REPOS_AND_ROUTING.md`](./REPOS_AND_ROUTING.md).

## Eventos principais

| Evento | Status alvo | Quem emite |
|--------|-------------|------------|
| `claim` | In Progress | creator |
| `open_pr` | Ready for Code Review | creator |
| `start_review` | In Code Review | {creator}-reviewer |
| `approve_review` | Ready for Test | {creator}-reviewer |
| `request_changes` | In Progress | {creator}-reviewer |
| `test_passed` | In Pull Request | qa-gate |
| `test_failed_bug` | In Progress | qa-gate |
| `merge_pr` | Done | devops-cicd / stores-release |

Lista completa e nós LangGraph: [`STATEGRAPH_FLOW.md`](./STATEGRAPH_FLOW.md).

## HITL obrigatório

| Situação | Modo |
|----------|------|
| `merge_pr` | `block_until_human` |
| 3× `test_failed_bug` consecutivos | `block_until_human` + blocker |
| `approve_review` em task de alto risco | `propose_only` (humano confirma) |

## Ciclo idle → dispatch

1. `list_idle` — resolve próximo agente livre
2. `emit_status_event` — atualiza board + handoff + audit
3. Agente ocupado → `dispatch_queue`
4. HITL pendente → `hitl_queue` (humano aprova)

Porta única (CLI): `agents/00-orchestration/scripts/cli/gateway_cli.py`
