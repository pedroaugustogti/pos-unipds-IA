# orchestrator

| Módulo | Função |
|--------|--------|
| `event_orchestrator.py` | Runtime de agentes, emit board, dispatch_queue |
| `event_actuation_context.py` | Contexto pós `on_status_event` |
| `event_actuation_runner.py` | `execute_agent_actuation` |
| `orchestrator_claim.py` | `orchestrator_enter_in_progress` |
| `claim_lock.py` | WIP / claim lock |
| `outbox.py` | Retry de writes no board |
| `smoke_tasks.py` | `pick_smoke_task` para testes |
