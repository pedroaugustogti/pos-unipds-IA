# MCP Server — Guardião Família (v2)

Fachada MCP sobre `lib/*` — **13 tools**. Transição de status no board: **somente** `emit_status_event` (eventos role-based).

Catálogo: `list_mcp_tools()`.

## Fluxo por fase

### Entrada no trabalho (orquestrador)

```
on_status_event(role, status) → hitl_guard_actuation → orchestrator_enter_in_progress
  → execute_agent_actuation_tool
```

### Implementação (creator)

```
on_status_event(…, In Progress) → hitl_guard_actuation → developer_implement
  → execute_agent_actuation_tool → emit_status_event(…_in_review | …_return_in_progress)
```

### Review (revisor)

```
on_status_event(…, In Review) → hitl_guard_actuation → developer_review
  → execute_agent_actuation_tool → emit_status_event(…_ready_for_test | …_return_in_progress)
```

### QA gate — In Test (mobile com evidência)

```
on_status_event(qa-gate, In Test)
  → hitl_guard_actuation
  → qa_validate(actuation_context, mode=live, worker_mode=local|docker)
  → execute_agent_actuation_tool
  → emit_status_event(qa-gate_in_pull_request | qa-gate_return_in_progress)
```

**Dentro de `qa_validate`** (por cenário em `ticket.qa.scenarios`; paralelo entre cenários):

```
qa_init_suite_mobile → qa_pipeline_evidence → qa_generate_evidence
```

| Tool | Papel |
|------|--------|
| `qa_init_suite_mobile` | Stack + `apps_ready_ok`; Metro/bundle (`metro_bundle_state`) |
| `qa_pipeline_evidence` | Monta pipeline Appium a partir do ticket |
| `qa_generate_evidence` | Executa script, PNG/MP4/JSON em `agents/00-runtime/output/{task_id}/qa-gate-({N})/evidence/` |

`worker_mode`: `local` = host (default); `docker` = um container por cenário (`GF_QA_SCENARIO_IMAGE`).

### Utilitários de gateway

| Tool | Uso |
|------|-----|
| `list_status_events` | Eventos permitidos por papel |
| `emit_status_event` | Aplicar transição no GitHub Project / issue |

## O que não é MCP

Não existem tools para `get_handoff`, `query_mobile_flow_rag`, `qa_ensure_stack_mobile`, `qa_appium_suite_*` nem `qa_db_seed` standalone. Handoff: arquivo em `agents/00-runtime/output/{task_id}/`. RAG mobile: `lib/mobile/mobile_flow_rag.py`.

## Referências

- Detalhe das tools: `agents/00-orchestration/docs/mcp/`
- Runtime mobile: [`../../../lib/mobile/README.md`](../../../lib/mobile/README.md)
- Entry: `python -m guardiao_mcp` · `guardiao-mcp.cmd` (Cursor)
