# cli/

Scripts operacionais — eventos **role-based v2** (`{agent_role}_{status_slug}`).

| Script | Uso |
|--------|-----|
| `gateway_cli.py` | Emitir evento (`--event` ou `--agent-role` + `--board-status`) |
| `model_tier_cli.py` | Inspecionar `select_model` |
| `ci_signal.py` / `ci_hint.py` | Sinais GitHub → gateway (eventos role-based) |
| `code_index.py` | Índice de código para contexto |

Exemplo:

```powershell
python agents/00-orchestration/scripts/cli/gateway_cli.py --task T-P3-009 --agent-role frontend-mobile --board-status "Ready for Code Review" --dry-run
```

Porta única de Status: `gateway_cli`, MCP `emit_status_event` ou LangGraph v2.
