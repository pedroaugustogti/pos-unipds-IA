# CrewAI Orchestrator — Guardião Família

Orquestrador [CrewAI](https://docs.crewai.com) que trata **mudanças de Status como eventos**, despacha **agentes ociosos** e escala **blocker** após **3 bugs** na mesma task.

## Arquitetura (eventos)

`mermaid
flowchart LR
  E[Evento board] --> N[notify_status_change]
  N --> I{Agente ocioso?}
  I -->|sim| D[Dispatch start_task]
  I -->|nao| Q[dispatch_queue]
  E -->|test_failed_bug| B[bug_count++]
  B -->|count>=3| BL[BLOCKER + skill impactada]
  BL --> JSON[github-project-2-import.json]
  E --> GH[Project #2 via gh]
`

## Modos

| Modo | LLM | Uso |
|------|-----|-----|
| deterministic | Não | Claim em lote |
| events | Não | Idle + dispatch + demo blocker 3 bugs |
| crew | Sim | Sprint com eventos no orchestrator |
| hierarchical | Sim | Manager delega |
| 
eview | Sim | Só revisores |
| events --events-llm | Sim | Crew só de eventos |

## Comandos

`powershell
cd docs/02-criacao-board/10-agents/crew
python main.py --mode events
python main.py --sprint 1 --mode crew --dry-run
`

Saída: output/events_orchestration.json, output/agent_runtime.json.

## Observabilidade (acompanhamento)

| Artefato | Caminho |
|----------|---------|
| Log append-only | `output/observability/workflow.jsonl` |
| Snapshot | `output/observability/snapshot.json` |
| Dashboard | `output/observability/dashboard.html` |

```powershell
cd docs/02-criacao-board/10-agents
python scripts/observability_cli.py --summary --dashboard
python scripts/observability_cli.py --tail 20
python scripts/observability_cli.py --open
```

Cada mudança de status grava no JSONL e atualiza o dashboard (auto-refresh 15s). Tool CrewAI: `observability_summary`.

## Regra de blocker (3 bugs)

No evento 	est_failed_bug / tool 
egister_task_bug:

1. Incrementa ug_counts[task_id]
2. No **3º** bug: marca Release Blocker=yes no JSON local
3. Notifica motivo + **skill impactada** (skills/{role}/SKILL.md e descrição do impacto)

## Tools de evento

| Tool | Função |
|------|--------|
| emit_status_event | Aplica evento no board + notifica dispatch |
| 
otify_board_status_change | Só idle/dispatch (sem gravar) |
| list_idle_crew_agents | Quem está idle/busy + blockers |
| 
esolve_agent_for_board_event | Quem chamar após o evento |
| 
egister_task_bug | Conta bugs / blocker |
| drain_dispatch_queue | Despacha fila quando agente fica idle |
| mark_agent_idle | Libera agente e processa fila |

## Biblioteca

- lib/event_orchestrator.py — runtime, idle, dispatch, blocker
- lib/board_client.py — JSON local + gh
- lib/task_router.py — seleção por oard_status
