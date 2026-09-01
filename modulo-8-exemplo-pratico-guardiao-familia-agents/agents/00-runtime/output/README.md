# output — artefatos por ticket

Pasta **efêmera** (`.gitignore`). Contém **somente pastas de ticket** (`T-P{n}-{seq}/`).

## Layout por ticket

```
T-P3-009/
  handoff.json
  seed-cache.json
  frontend-mobile-(1)/
    actions.json
    action-history.html
  qa-gate-(1)/
    evidence/
  orchestrator-(1)/
    langgraph-run.json
```

- **Handoff:** `{ticket}/handoff.json`
- **Evidências QA:** `{ticket}/qa-gate-({N})/evidence/`
- **Histórico ReAct:** `{ticket}/{agent_role}-({N})/actions.json`

Estado global (orquestrador, dispatch, audit, caches legados) fica em `../system/`.

Paths: `lib/paths.py` (`RUNTIME_OUTPUT_DIR`, `lib/ticket_output.py`)
