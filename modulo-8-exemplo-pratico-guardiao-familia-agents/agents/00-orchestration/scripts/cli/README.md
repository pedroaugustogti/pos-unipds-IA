# cli/

| Script | Uso |
|--------|-----|
| `gateway_cli.py` | Emitir evento Status (`--dry-run`) |
| `model_tier_cli.py` | Inspecionar `select_model` |
| `ci_signal.py` / `ci_hint.py` | Sinais CI para nós do grafo |
| `code_index.py` | Índice de código para contexto |

Porta única de Status: sempre `gateway_cli` ou MCP `emit_status_event`.
