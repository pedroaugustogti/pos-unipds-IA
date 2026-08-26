# MCP Server — Guardião Família (Fase B)

Fachada MCP sobre `lib/*`. Status **só** via `emit_status_event` (gateway).

## Subir

```powershell
cd modulo-8-exemplo-pratico-guardiao-familia-agents
pip install "mcp>=1.0"
python -m guardiao_mcp
```

Launcher Windows: `guardiao-mcp.cmd`.

## Cursor

Registrado em:

- Raiz do monorepo: `.cursor/mcp.json` → server `guardiao-familia-agents`
- Pasta do módulo: `.cursor/mcp.json`

Reinicie o MCP / Cursor após alterar o JSON. Em Settings → MCP, o server deve aparecer como habilitado.

## Segurança

- Tools de escrita usam `dry_run=true` por default (`emit_status_event`, `approve_hitl`, handoff, history).
- `dispatch_job_tool` exige `GUARDIAO_MCP_ALLOW_DISPATCH=1`.

## Catálogo

Chame a tool `list_mcp_tools` ou veja o relatório em `docs/autonomia/fases/`.
