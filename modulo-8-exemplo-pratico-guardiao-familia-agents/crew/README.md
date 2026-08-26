# Runtime / configuração (não é orquestrador)

A pasta `crew/` guarda **env**, **requirements** e **artefatos de runtime** (`output/`).

A orquestração do módulo é **somente LangGraph** (`langgraph_app/` + `scripts/langgraph_run.py`).
O CrewAI foi removido.

| Path | Função |
|------|--------|
| `.env` / `.env.example` | Secrets e flags (`GUARDIAO_*`, OpenRouter, LangSmith) |
| `requirements.txt` | Deps LangGraph / MCP / OpenRouter / Cursor SDK |
| `output/` | handoffs, observability, locks, langgraph runs, evals |

```powershell
python scripts/langgraph_run.py --task T-P05-006 --mode dry_run --from-zero
python -m guardiao_mcp
```
