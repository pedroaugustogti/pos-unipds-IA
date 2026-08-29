# scripts — CLIs de orquestração

| Subpasta | Responsabilidade |
|----------|------------------|
| `langgraph/` | Pipeline grafo, smoke, LangSmith |
| `worker/` | Worker, dispatch Cursor, autonomy loop |
| `cli/` | Gateway, observability, model tier, CI |
| `demo/` | Demo banca, live server, publish Pages |
| `ops/` | Manutenção/migração do repositório |
| `board/` | Wrappers legados → preferir `board_automation/scripts/cli/` |

Paths: `lib.paths.orch_script("langgraph/langgraph_run.py")`
