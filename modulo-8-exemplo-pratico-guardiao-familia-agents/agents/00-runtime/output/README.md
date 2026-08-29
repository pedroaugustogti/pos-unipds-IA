# output — artefatos de runtime

Pasta **efêmera** recriada em execução. Conteúdo em `.gitignore`.

| Subpasta | Conteúdo |
|----------|----------|
| `handoffs/` | JSON handoff por `task_id` |
| `observability/` | `snapshot.json`, `tasks/*.html` |
| `langgraph/` | Estado/checkpoints por task |
| `dispatch/` | Jobs worker, prompts, results |
| `board/` | Cache Project, logs de seed |
| `mobile/` | Evidências QA, dumps UI, RAG |
| `orchestrator/` | Locks, outbox, runtime agentes |
| `audit/` | `audit-trail.jsonl` |
| `demo/` | Relatórios demo banca |

## Decisões

- Ler handoff antes de implementar: `handoffs/{task_id}.json`
- Dashboard lê `observability/snapshot.json`
- Limpar para run limpo: apagar pasta ou `reorganize_output.py`

Paths: `lib/paths.py` (`RUNTIME_OUTPUT_DIR`, `HANDOFF_DIR`, …)
