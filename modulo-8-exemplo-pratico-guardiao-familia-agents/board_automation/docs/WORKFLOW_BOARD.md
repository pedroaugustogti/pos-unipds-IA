# Workflow board — módulo 8 (Supervisor + HITL)

Fonte de Status: board do módulo 7  
`modulo-7-exemplo-pratico-guardiao-familia/docs/02-criacao-board/08-board/github-project-2-import.json`  
Override: env `GUARDAO_BOARD_JSON`.

## Status

`Todo` → `In Progress` → `Ready for Code Review` → `In Code Review` → `Ready for Test` → `In Test` → `In Pull Request` → `Done`

## Porta única

```powershell
python agents/00-orchestration/scripts/cli/gateway_cli.py --task T-P05-001 --event claim --dry-run
python agents/00-orchestration/scripts/cli/gateway_cli.py --list-hitl
python agents/00-orchestration/scripts/cli/gateway_cli.py --task T-P05-001 --event merge_pr --approve-hitl
```

## Quem age em cada Status

| Status | Agente |
|--------|--------|
| Todo | orchestrator (despacha) |
| In Progress | creator (`qa` CSV → **qa-author**) |
| Ready/In Code Review | `*-reviewer` (proposta se alto risco) |
| Ready/In Test | **qa-gate** |
| In Pull Request | devops-cicd ou stores-release |
| Done | só após **HITL humano** em `merge_pr` |

## HITL obrigatório

| Situação | Modo |
|----------|------|
| `merge_pr` | block_until_human |
| 3× `test_failed_bug` | block_until_human + blocker |
| `approve_review` em task alto risco | propose_only |

## Eventos + idle

1. `list_idle` → resolve agente  
2. `emit_status_event` (gateway) → board + handoff + audit  
3. Se busy → `dispatch_queue`  
4. Se HITL → `hitl_queue` (humano)

## Crew

```powershell
cd crew
python main.py --mode events --dry-run
```

Supervisor **só** roteia; workers consomem handoff.
