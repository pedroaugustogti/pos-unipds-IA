# lib — biblioteca compartilhada

Código de domínio usado por LangGraph, MCP, CLIs e worker. **Não** contém prompts de agente.

## Pacotes

| Pasta | Responsabilidade | Quando importar |
|-------|------------------|-----------------|
| [`core/`](core/) | LLM tier, repos, ReAct policy | Escolha de modelo |
| [`gateway/`](gateway/) | Status, handoff, HITL | **Qualquer** mudança de board |
| [`orchestrator/`](orchestrator/) | Dispatch, worker, outbox | Jobs Cursor / fila |
| [`observability/`](observability/) | Snapshot, HTML | Dashboard |
| [`ci/`](ci/) | Sinais CI | Nós CI do grafo |
| [`mobile/`](mobile/) | Appium, RAG, evidência | QA mobile |
| [`site/`](site/) | Site marketing | Tasks web |

Raiz: `paths.py`, `env_load.py` — paths canônicos e `.env`.

Board GitHub: pacote [`board_automation/`](../board_automation/) (separado).

## Decisões

```python
from lib.gateway import emit_status_event      # Status
from lib.core.model_tier import select_model   # LLM
from board_automation.board.task_router import pick_task
```

- Não duplicar lógica de board em `lib/` — usar `board_automation.board`
- Shims na raiz de `lib/*.py` podem existir; preferir subpacotes
