# lib — biblioteca compartilhada

Código de domínio do pipeline MCP + LangGraph. Board GitHub: [`board_automation/`](../board_automation/).

## Estrutura

| Pasta | Responsabilidade |
|-------|------------------|
| [`core/`](core/) | LLM tier, repos, ReAct policy, agent registry |
| [`gateway/`](gateway/) | Status, handoff, HITL, guardrail de atuação |
| [`orchestrator/`](orchestrator/) | Runtime, actuation MCP, claim lock, fases |
| [`ci/`](ci/) | Sinais CI → gateway |
| [`mobile/`](mobile/) | Appium, seed QA, RAG de fluxos |
| [`site/`](site/) | Tasks web (hero) |

Raiz: `paths.py`, `env_load.py`, `ticket_output.py`, `runtime_log.py`.

## Imports canônicos

```python
from lib.gateway import emit_status_event
from lib.orchestrator.event_actuation_runner import execute_agent_actuation
from board_automation.board.task_router import load_tasks, pick_task
```
