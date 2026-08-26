# Relatório final — Fase B: MCP Server

> Data: 2026-08-25  
> Status: **Concluída**  
> Contexto: [RELATORIO_FASE_A_MODEL_TIER.md](RELATORIO_FASE_A_MODEL_TIER.md)  
> Base: [GUIA_LANGGRAPH_MCP_LLM.md](../GUIA_LANGGRAPH_MCP_LLM.md) §3  
> Pacote: `guardiao_mcp/` (evita conflito com o PyPI `mcp`)

---

## 1. Objetivo (atingido)

Expor `lib/*` como tools MCP com contrato JSON uniforme, sem abrir segunda porta de Status. Gateway permanece único.

---

## 2. O que foi implementado

| Entregável | Path |
|------------|------|
| Server FastMCP (stdio) | `guardiao_mcp/server.py` |
| Contrato `ok` / `fail` / `wrap_call` | `guardiao_mcp/contract.py` |
| Entry `python -m guardiao_mcp` | `guardiao_mcp/__main__.py` |
| Launcher Windows | `guardiao-mcp.cmd` |
| README MCP | `guardiao_mcp/README.md` |
| Cursor (módulo) | `modulo-8-.../.cursor/mcp.json` |
| Cursor (workspace) | `.cursor/mcp.json` → server **`guardiao-familia-agents`** |
| Deps | `crew/requirements.txt` → `mcp>=1.9,<2` |
| Testes parity | `tests/test_mcp_gateway_parity.py` (6 OK) |

### Segurança aplicada

- Escrita com `dry_run=true` por default (`emit_status_event`, `approve_hitl`, handoff, history).  
- `dispatch_job_tool` só com `GUARDIAO_MCP_ALLOW_DISPATCH=1`.  
- Sem exposição de secrets como tools.

---

## 3. Catálogo completo de tools (16)

| # | Tool | Grupo | Escrita | Lib / nota |
|---|------|-------|---------|------------|
| 1 | `emit_status_event` | gateway | sim* | `lib.gateway` — porta única Status |
| 2 | `list_hitl_queue` | gateway | não | `lib.gateway` |
| 3 | `approve_hitl` | gateway | sim* | `lib.gateway` |
| 4 | `snapshot_observability` | observability | não† | `lib.observability` |
| 5 | `select_model_tier` | model | não | `lib.model_tier` (Fase A) |
| 6 | `list_idle_agents_tool` | orchestrator | não | `lib.event_orchestrator` |
| 7 | `resolve_agent_for_board_event` | orchestrator | não | idem |
| 8 | `drain_dispatch_queue` | orchestrator | sim | idem |
| 9 | `mark_agent_idle` | orchestrator | sim | idem |
| 10 | `load_tasks_tool` | board | não | `lib.task_router` |
| 11 | `pick_task_tool` | board | não | idem |
| 12 | `get_handoff` | handoff | não | `lib.handoff` |
| 13 | `write_handoff_tool` | handoff | sim* | idem |
| 14 | `append_task_action_tool` | history | sim* | `lib.task_action_history` |
| 15 | `dispatch_job_tool` | dispatch | sim‡ | `lib.dispatch_adapter` |
| 16 | `list_mcp_tools` | meta | não | catálogo |

\* `dry_run` default `true`  
† opcional `write_html` grava dashboard  
‡ requer flag de env

---

## 4. MCP habilitado no Cursor

Registrado como **`guardiao-familia-agents`**:

```json
"guardiao-familia-agents": {
  "command": "cmd",
  "args": ["/c", "modulo-8-exemplo-pratico-guardiao-familia-agents\\guardiao-mcp.cmd"],
  "env": { "PYTHONUTF8": "1" }
}
```

Arquivos: raiz `.cursor/mcp.json` + `modulo-8-.../.cursor/mcp.json`.

**Para ativar na UI:** Cursor Settings → MCP → garantir que `guardiao-familia-agents` está **enabled** (após reload da janela / restart MCP). O JSON do workspace já inclui o server.

---

## 5. Validação executada

```powershell
cd modulo-8-exemplo-pratico-guardiao-familia-agents
pip install "mcp>=1.9,<2"
python -m unittest tests.test_mcp_gateway_parity -v
python -c "from guardiao_mcp.server import list_mcp_tools; print(list_mcp_tools())"
```

| Critério | Resultado |
|----------|-----------|
| Import FastMCP / server sobe (módulo) | OK (`mcp` 1.x) |
| Catálogo 16 tools | OK |
| `emit_status_event` dry-run parity vs `gateway.emit_status_event` | OK |
| Evento inválido rejeitado | OK |
| `select_model_tier` ≡ `select_model` | OK |
| `list_hitl_queue` OK | OK |
| Dispatch bloqueado sem flag | OK |
| Testes unitários | **6/6 OK** |

### Nota de versão

`mcp` 2.x removeu `mcp.server.fastmcp`. Projeto pinado em `mcp>=1.9,<2`.

---

## 6. Impacto

| Área | Efeito |
|------|--------|
| Gateway / Kanban | Neutro — mesma lib |
| Cursor | Tools de board/HITL/model disponíveis via MCP |
| Orquestração | **LangGraph** (CrewAI removido) |
| Fase C | Grafo consome tools via bridge / MCP |
| OpenRouter | No loop na Fase C+ |

---

## 7. Próximo passo

**Fase C — LangGraph:** nós do Kanban chamando estas tools MCP; HITL = `interrupt`; LLM OpenRouter na orquestração via `select_model_tier`.

---

## 8. Resumo

Fase B entregue: **16 tools**, server `guardiao-familia-agents` no Cursor, parity com gateway validada. Pronto para LangGraph.
