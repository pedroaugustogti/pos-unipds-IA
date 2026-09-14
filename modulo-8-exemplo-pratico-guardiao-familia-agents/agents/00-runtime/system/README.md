# system — estado global do runtime

Pasta **efêmera** (`.gitignore`). Estado compartilhado entre tickets — **não** coloque aqui pastas `T-P*`.

| Subpasta | Conteúdo |
|----------|----------|
| `orchestrator/` | Locks, outbox, runtime dos agentes |
| `dispatch/` | Legado — fila worker (substituída pelo grafo v2) |
| `board/` | Cache GitHub Project |
| `audit/` | `audit-trail.jsonl` |
| `observability/` | `snapshot.json`, `tasks/*.json` |
| `mobile/` | Guides RAG, `metro_bundle_state.json` (fingerprint Metro), dumps UI |
| `handoffs/` | Espelho legado (migração); canônico: `output/{ticket}/handoff.json` |

Paths: `lib/paths.py` (`RUNTIME_SYSTEM_DIR`)
